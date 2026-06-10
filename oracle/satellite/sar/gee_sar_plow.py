"""
POD Oracle — Sentinel-1 SAR Plow Detection (GEE Python API)
Desafarm Plots, Omo Valley, Ethiopia

Uses the POD GEE service account from .env.devnet:
  GEE_SERVICE_ACCOUNT=pod-oracle-agent@arched-inkwell-260613.iam.gserviceaccount.com
  GEE_KEY_FILE=C:\\Users\\bekam\\.config\\pod-agents\\gee-service-account.json
  GEE_PROJECT=arched-inkwell-260613

Requirements:
    pip install earthengine-api python-dotenv

Usage:
    python gee_sar_plow.py --plot ETH-001 --date 2026-04-10
    python gee_sar_plow.py --plot ETH-001 --date 2026-04-10 --env /path/to/.env.devnet
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import ee

# Load .env.devnet if python-dotenv is available, else fall back to os.environ
try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


# ── Plot registry (matches desafarm-all-plots.geojson order) ────────────────

PLOTS = {
    "ETH-001": {"name": "plot 116A under Road", "coords": [
        [36.50974, 9.37088], [36.50476, 9.37359], [36.50673, 9.37483],
        [36.51250, 9.36443], [36.50974, 9.37088]
    ]},
    "ETH-002": {"name": "plot 115A", "coords": [
        [36.50677, 9.37499], [36.50470, 9.37360], [36.50171, 9.37701],
        [36.50425, 9.38003], [36.50677, 9.37499]
    ]},
    "ETH-003": {"name": "plot 115B", "coords": [
        [36.50390, 9.38015], [36.50164, 9.37700], [36.49881, 9.38012],
        [36.50106, 9.38285], [36.50390, 9.38015]
    ]},
    "ETH-004": {"name": "plot 116B", "coords": [
        [36.51120, 9.36956], [36.50475, 9.37332], [36.50219, 9.37112],
        [36.50556, 9.36782], [36.51046, 9.36003], [36.51120, 9.36956]
    ]},
    "ETH-005": {"name": "plot 118", "coords": [
        [36.51018, 9.36863], [36.51448, 9.36984], [36.51495, 9.36658],
        [36.51250, 9.36443], [36.51018, 9.36863]
    ]},
    "ETH-006": {"name": "plot 117", "coords": [
        [36.52118, 9.36980], [36.50795, 9.36811], [36.50566, 9.36774],
        [36.50665, 9.36569], [36.50618, 9.36495], [36.50982, 9.36083],
        [36.52118, 9.36980]
    ]},
    "ETH-007": {"name": "plot 102A", "coords": [
        [36.50591, 9.36703], [36.50665, 9.36554], [36.50236, 9.36198],
        [36.50002, 9.36561], [36.50591, 9.36703]
    ]},
    "ETH-008": {"name": "plot 101", "coords": [
        [36.50259, 9.36178], [36.50608, 9.36441], [36.50981, 9.36076],
        [36.50895, 9.35887], [36.50752, 9.35854], [36.50259, 9.36178]
    ]},
}

# Confidence thresholds (dB) — tune against ground truth when available
CONFIRM_THRESHOLD   = -3.0
UNCERTAIN_THRESHOLD = -1.5


# ── GEE helpers ──────────────────────────────────────────────────────────────

def get_s1_composite(aoi: ee.Geometry, start: str, end: str) -> ee.Image:
    """Load IW GRD VV+VH, ascending orbit, median composite over window."""
    return (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .select(["VV", "VH"])
        .median()
    )


def compute_delta(pre: ee.Image, post: ee.Image) -> ee.Image:
    """
    Compute per-pixel delta-dB (post − pre).
    GEE S1_GRD bands are in dB already.
    Negative delta in VV = backscatter decrease = plowing signal.
    """
    dVV   = post.select("VV").subtract(pre.select("VV")).rename("delta_VV")
    dVH   = post.select("VH").subtract(pre.select("VH")).rename("delta_VH")
    dRatio = dVV.subtract(dVH).rename("delta_VVVH")
    return dVV.addBands(dVH).addBands(dRatio)


def polygon_stats(image: ee.Image, aoi: ee.Geometry, scale: int = 10) -> dict:
    """Reduce image over polygon → mean, stdDev, percentiles."""
    reducer = (
        ee.Reducer.mean()
        .combine(ee.Reducer.stdDev(), sharedInputs=True)
        .combine(ee.Reducer.percentile([10, 25, 75, 90]), sharedInputs=True)
    )
    result = image.reduceRegion(
        reducer=reducer,
        geometry=aoi,
        scale=scale,
        maxPixels=int(1e9),
    )
    return result.getInfo()


def scene_ids(collection: ee.ImageCollection) -> list[str]:
    """Extract system:index (scene IDs) from a collection."""
    ids = collection.aggregate_array("system:index").getInfo()
    return ids


# ── Confidence scoring ────────────────────────────────────────────────────────

def compute_confidence(mean_delta_vv: float, std_delta_vv: float) -> tuple[str, float]:
    """
    Rule-based heuristic — replace with trained classifier when ground truth available.
    Returns (status, confidence_0_to_1).
    """
    # Raw score: more negative mean → higher confidence
    raw = min(max(-mean_delta_vv / 6.0, 0.0), 1.0)
    # Penalise high variance (noise vs real change)
    penalty = min(std_delta_vv / 10.0, 0.2)
    confidence = round(max(raw - penalty, 0.0), 3)

    if mean_delta_vv < CONFIRM_THRESHOLD:
        status = "CONFIRMED"
    elif mean_delta_vv < UNCERTAIN_THRESHOLD:
        status = "UNCERTAIN"
    else:
        status = "UNCONFIRMED"

    return status, confidence


# ── Main ──────────────────────────────────────────────────────────────────────

def predict_plowing(plot_id: str, claimed_date: str, project: str | None = None) -> dict:
    """
    Core oracle function.

    Args:
        plot_id:      'ETH-001' … 'ETH-008'
        claimed_date: 'YYYY-MM-DD'
        project:      GEE cloud project (optional)

    Returns:
        Oracle output dict matching the SAR-001 bounty schema.
    """
    if plot_id not in PLOTS:
        raise ValueError(f"Unknown plot_id: {plot_id}. Valid: {list(PLOTS)}")

    t0      = datetime.strptime(claimed_date, "%Y-%m-%d")
    pre_start  = (t0 + timedelta(days=-14)).strftime("%Y-%m-%d")
    pre_end    = (t0 + timedelta(days=-3)).strftime("%Y-%m-%d")
    post_start = (t0 + timedelta(days=1)).strftime("%Y-%m-%d")
    post_end   = (t0 + timedelta(days=10)).strftime("%Y-%m-%d")

    aoi = ee.Geometry.Polygon([PLOTS[plot_id]["coords"]])

    # Load scenes
    pre_coll  = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(pre_start, pre_end)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .select(["VV", "VH"])
    )
    post_coll = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(aoi)
        .filterDate(post_start, post_end)
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VH"))
        .filter(ee.Filter.eq("orbitProperties_pass", "ASCENDING"))
        .select(["VV", "VH"])
    )

    n_pre  = pre_coll.size().getInfo()
    n_post = post_coll.size().getInfo()

    if n_pre == 0:
        raise RuntimeError(f"No pre-event S1 scenes for {plot_id} in {pre_start}→{pre_end}")
    if n_post == 0:
        raise RuntimeError(f"No post-event S1 scenes for {plot_id} in {post_start}→{post_end}")

    pre_ids  = scene_ids(pre_coll)
    post_ids = scene_ids(post_coll)

    pre_img  = pre_coll.median()
    post_img = post_coll.median()

    delta = compute_delta(pre_img, post_img)
    stats = polygon_stats(delta, aoi)

    mean_vv = stats["delta_VV_mean"]
    std_vv  = stats["delta_VV_stdDev"]

    status, confidence = compute_confidence(mean_vv, std_vv)

    verification_date = datetime.utcnow().strftime("%Y-%m-%d")

    return {
        "plot_id":           plot_id,
        "claimed_date":      claimed_date,
        "status":            status,
        "confidence":        confidence,
        "sar_delta_db":      round(mean_vv, 3),
        "sar_delta_vv_std":  round(std_vv, 3),
        "sar_delta_vh_mean": round(stats.get("delta_VH_mean", 0.0), 3),
        "scene_ids":         pre_ids + post_ids,
        "pre_window":        f"{pre_start}/{pre_end}",
        "post_window":       f"{post_start}/{post_end}",
        "verification_date": verification_date,
        "method":            "GEE_S1_GRD_delta_dB_heuristic_v0"
    }


def init_ee(env_file: str | None = None) -> None:
    """
    Initialise Earth Engine using the POD service account from .env.devnet.
    Falls back to earthengine authenticate / application default credentials.
    """
    # Load env file
    env_path = Path(env_file) if env_file else Path(__file__).parent.parent.parent / "pod-agents" / ".env.devnet"
    if _DOTENV_AVAILABLE and env_path.exists():
        load_dotenv(env_path, override=False)

    sa      = os.environ.get("GEE_SERVICE_ACCOUNT")
    key_file = os.environ.get("GEE_KEY_FILE")
    project  = os.environ.get("GEE_PROJECT")

    if sa and key_file and Path(key_file).exists():
        credentials = ee.ServiceAccountCredentials(sa, key_file)
        ee.Initialize(credentials=credentials, project=project)
        print(f"  ✓ GEE authenticated via service account: {sa}")
    elif project:
        ee.Initialize(project=project)
        print(f"  ✓ GEE authenticated via application default (project: {project})")
    else:
        ee.Initialize()
        print("  ✓ GEE authenticated via application default credentials")


def main():
    parser = argparse.ArgumentParser(description="POD Oracle — SAR plow detection (GEE)")
    parser.add_argument("--plot", required=True, help="Plot ID e.g. ETH-001")
    parser.add_argument("--date", required=True, help="Claimed plowing date YYYY-MM-DD")
    parser.add_argument("--env",  default=None,  help="Path to .env file (default: pod-agents/.env.devnet)")
    args = parser.parse_args()

    print("Initialising Earth Engine...")
    try:
        init_ee(args.env)
    except Exception as e:
        sys.exit(f"Auth failed: {e}")

    print(f"Running SAR plow detection: {args.plot} | claimed date {args.date}")
    try:
        result = predict_plowing(args.plot, args.date)
    except Exception as e:
        sys.exit(f"Error: {e}")

    print("\n── Oracle Result ────────────────────────────────")
    print(json.dumps(result, indent=2))

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"oracle_{args.plot}_{args.date}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Saved → {out_path}")


if __name__ == "__main__":
    main()
