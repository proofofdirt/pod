"""
POD Oracle — Sentinel-1 SAR Plow Detection (Standalone / No GEE)
Desafarm Plots, Omo Valley, Ethiopia

Downloads S1 GRD scenes from Copernicus CDSE, applies terrain correction
using SNAP GPT, computes VV/VH delta-dB, outputs oracle JSON.

Reads credentials from pod-agents/.env.devnet:
  CDSE_USERNAME, CDSE_PASSWORD, CDSE_STAC_URL, CDSE_DOWNLOAD_URL

Requirements:
    pip install sentinelsat rasterio shapely numpy scipy python-dotenv
    ESA SNAP installed with gpt on PATH (https://step.esa.int/main/download/snap-download/)

Usage:
    python sar_plow_standalone.py --plot ETH-001 --date 2026-04-10
    python sar_plow_standalone.py --plot ETH-001 --date 2026-04-10 --skip-download
    python sar_plow_standalone.py --plot ETH-001 --date 2026-04-10 --env /path/to/.env.devnet
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from shapely.geometry import Polygon, mapping

# sentinelsat — CDSE uses the same API interface as Copernicus SciHub
try:
    from sentinelsat import SentinelAPI, geojson_to_wkt, read_geojson
except ImportError:
    sys.exit("Missing sentinelsat — run: pip install sentinelsat")


# ── Load env ─────────────────────────────────────────────────────────────────

try:
    from dotenv import load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False

_DEFAULT_ENV = Path(__file__).parent.parent.parent / "pod-agents" / ".env.devnet"


def load_env(env_file: str | None = None) -> None:
    path = Path(env_file) if env_file else _DEFAULT_ENV
    if _DOTENV_AVAILABLE and path.exists():
        load_dotenv(path, override=False)


# ── Config ───────────────────────────────────────────────────────────────────

# sentinelsat v1.x targets the legacy SciHub API interface.
# CDSE exposes a compatible endpoint — use CDSE_STAC_URL for search,
# CDSE_DOWNLOAD_URL for downloads (set in .env.devnet).
SENTINELSAT_URL = "https://apihub.copernicus.eu/apihub"  # overridden by env below

DATA_DIR    = Path(__file__).parent / "data" / "s1_scenes"
OUTPUT_DIR  = Path(__file__).parent / "output"
SNAP_GPT    = os.environ.get("SNAP_GPT_PATH", "gpt")   # path to SNAP gpt executable

CONFIRM_THRESHOLD   = -3.0   # dB
UNCERTAIN_THRESHOLD = -1.5   # dB


# ── Plot registry ─────────────────────────────────────────────────────────────

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


# ── Scene search & download ───────────────────────────────────────────────────

def cdse_api(env_file: str | None = None) -> SentinelAPI:
    load_env(env_file)
    user = os.environ.get("CDSE_USERNAME")
    pw   = os.environ.get("CDSE_PASSWORD")
    if not user or not pw:
        sys.exit("CDSE_USERNAME / CDSE_PASSWORD not found. Check pod-agents/.env.devnet")
    # CDSE uses its own auth endpoint but the sentinelsat query API is compatible
    api_url = os.environ.get("SENTINELSAT_API_URL", SENTINELSAT_URL)
    return SentinelAPI(user, pw, api_url=api_url)


def search_scenes(api: SentinelAPI, coords: list, start: str, end: str) -> dict:
    """Search for S1 GRD IW scenes covering the polygon in the date window."""
    poly = Polygon(coords)
    footprint = geojson_to_wkt(mapping(poly))
    products = api.query(
        area=footprint,
        date=(start, end),
        platformname="Sentinel-1",
        producttype="GRD",
        sensoroperationalmode="IW",
    )
    return products


def download_scenes(api: SentinelAPI, products: dict, dest_dir: Path) -> list[Path]:
    """Download products not already cached locally."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for pid, meta in products.items():
        title    = meta["title"]
        zip_path = dest_dir / f"{title}.zip"
        safe_dir = dest_dir / f"{title}.SAFE"
        if safe_dir.exists():
            print(f"  ✓ Cached: {title}")
            paths.append(safe_dir)
            continue
        print(f"  ↓ Downloading: {title}")
        api.download(pid, directory_path=str(dest_dir))
        # Unzip
        import zipfile
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest_dir)
        zip_path.unlink(missing_ok=True)
        paths.append(safe_dir)
    return paths


# ── SNAP terrain correction ───────────────────────────────────────────────────

SNAP_GRAPH_TEMPLATE = """<graph id="S1_Preprocessing">
  <version>1.0</version>
  <node id="Read">
    <operator>Read</operator>
    <sources/>
    <parameters>
      <file>{input_path}</file>
    </parameters>
  </node>
  <node id="Apply-Orbit-File">
    <operator>Apply-Orbit-File</operator>
    <sources><sourceProduct refid="Read"/></sources>
    <parameters>
      <orbitType>Sentinel Precise (Auto Download)</orbitType>
      <polyDegree>3</polyDegree>
      <continueOnFail>true</continueOnFail>
    </parameters>
  </node>
  <node id="Calibration">
    <operator>Calibration</operator>
    <sources><sourceProduct refid="Apply-Orbit-File"/></sources>
    <parameters>
      <outputSigmaBand>true</outputSigmaBand>
      <selectedPolarisations>VV,VH</selectedPolarisations>
      <outputImageScaleInDb>false</outputImageScaleInDb>
    </parameters>
  </node>
  <node id="Speckle-Filter">
    <operator>Speckle-Filter</operator>
    <sources><sourceProduct refid="Calibration"/></sources>
    <parameters>
      <filter>Lee Sigma</filter>
      <filterSizeX>5</filterSizeX>
      <filterSizeY>5</filterSizeY>
    </parameters>
  </node>
  <node id="Terrain-Correction">
    <operator>Terrain-Correction</operator>
    <sources><sourceProduct refid="Speckle-Filter"/></sources>
    <parameters>
      <demName>SRTM 1Sec HGT</demName>
      <pixelSpacingInMeter>10.0</pixelSpacingInMeter>
      <mapProjection>WGS84(DD)</mapProjection>
      <saveDEM>false</saveDEM>
      <saveLocalIncidenceAngle>false</saveLocalIncidenceAngle>
      <bandNamePrefix>Sigma0</bandNamePrefix>
    </parameters>
  </node>
  <node id="LinearToFromdB">
    <operator>LinearToFromdB</operator>
    <sources><sourceProduct refid="Terrain-Correction"/></sources>
    <parameters/>
  </node>
  <node id="Write">
    <operator>Write</operator>
    <sources><sourceProduct refid="LinearToFromdB"/></sources>
    <parameters>
      <file>{output_path}</file>
      <formatName>GeoTIFF</formatName>
    </parameters>
  </node>
</graph>"""


def preprocess_scene(safe_dir: Path, out_dir: Path) -> Path:
    """
    Run SNAP GPT preprocessing:
    Orbit → Calibrate → Speckle filter → Terrain correct → Linear→dB → GeoTIFF
    Returns path to output GeoTIFF.
    """
    title    = safe_dir.stem
    out_tif  = out_dir / f"{title}_TC_dB.tif"
    if out_tif.exists():
        print(f"  ✓ Preprocessed (cached): {out_tif.name}")
        return out_tif

    out_dir.mkdir(parents=True, exist_ok=True)

    # Write SNAP graph to temp file
    graph_xml = SNAP_GRAPH_TEMPLATE.format(
        input_path=str(safe_dir / "manifest.safe"),
        output_path=str(out_tif.with_suffix("")),  # SNAP appends .tif
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as gf:
        gf.write(graph_xml)
        graph_path = gf.name

    print(f"  ⚙ SNAP preprocessing: {title}")
    result = subprocess.run(
        [SNAP_GPT, graph_path, "-q", "4"],   # -q 4 = 4 CPU threads
        capture_output=True, text=True
    )
    Path(graph_path).unlink(missing_ok=True)

    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError(f"SNAP preprocessing failed for {title}")

    # SNAP may append _TC_dB suffix — find actual output
    candidates = list(out_dir.glob(f"{title}*.tif"))
    if not candidates:
        raise FileNotFoundError(f"SNAP output not found in {out_dir}")
    actual = candidates[0]
    if actual != out_tif:
        actual.rename(out_tif)
    print(f"  ✓ Preprocessed → {out_tif.name}")
    return out_tif


# ── Delta-dB computation ──────────────────────────────────────────────────────

def extract_polygon_stats(tif_path: Path, coords: list, band_name: str) -> dict:
    """
    Clip raster to polygon, return mean, std, percentiles for the named band.
    Band matching is by name substring (VV or VH).
    """
    poly    = Polygon(coords)
    geom    = [mapping(poly)]

    with rasterio.open(tif_path) as src:
        # Find band index matching VV or VH
        band_idx = None
        for i, desc in enumerate(src.descriptions, start=1):
            if desc and band_name.upper() in desc.upper():
                band_idx = i
                break
        if band_idx is None:
            # Fall back to position: VV=1, VH=2
            band_idx = 1 if band_name.upper() == "VV" else 2

        out_image, _ = rio_mask(src, geom, crop=True, nodata=np.nan, indexes=[band_idx])
        data = out_image[0].astype(np.float32)
        valid = data[~np.isnan(data)]

    if len(valid) == 0:
        raise ValueError(f"No valid pixels in polygon for band {band_name} in {tif_path.name}")

    return {
        "mean":  float(np.mean(valid)),
        "std":   float(np.std(valid)),
        "p10":   float(np.percentile(valid, 10)),
        "p25":   float(np.percentile(valid, 25)),
        "p75":   float(np.percentile(valid, 75)),
        "p90":   float(np.percentile(valid, 90)),
        "count": int(len(valid)),
    }


def compute_delta_stats(pre_tif: Path, post_tif: Path, coords: list) -> dict:
    """Compute delta-dB polygon stats for VV and VH."""
    pre_vv  = extract_polygon_stats(pre_tif,  coords, "VV")
    post_vv = extract_polygon_stats(post_tif, coords, "VV")
    pre_vh  = extract_polygon_stats(pre_tif,  coords, "VH")
    post_vh = extract_polygon_stats(post_tif, coords, "VH")

    delta_vv_mean = post_vv["mean"] - pre_vv["mean"]
    delta_vh_mean = post_vh["mean"] - pre_vh["mean"]
    delta_vv_std  = (post_vv["std"] ** 2 + pre_vv["std"] ** 2) ** 0.5  # propagated

    return {
        "delta_VV_mean": round(delta_vv_mean, 3),
        "delta_VV_std":  round(delta_vv_std,  3),
        "delta_VH_mean": round(delta_vh_mean, 3),
        "pre_VV_mean":   round(pre_vv["mean"],  3),
        "post_VV_mean":  round(post_vv["mean"], 3),
    }


# ── Confidence scoring ────────────────────────────────────────────────────────

def compute_confidence(delta_stats: dict) -> tuple[str, float]:
    mean_vv = delta_stats["delta_VV_mean"]
    std_vv  = delta_stats["delta_VV_std"]

    raw     = min(max(-mean_vv / 6.0, 0.0), 1.0)
    penalty = min(std_vv / 10.0, 0.2)
    conf    = round(max(raw - penalty, 0.0), 3)

    if mean_vv < CONFIRM_THRESHOLD:
        status = "CONFIRMED"
    elif mean_vv < UNCERTAIN_THRESHOLD:
        status = "UNCERTAIN"
    else:
        status = "UNCONFIRMED"

    return status, conf


# ── Main oracle function ──────────────────────────────────────────────────────

def predict_plowing(
    plot_id: str,
    claimed_date: str,
    skip_download: bool = False,
) -> dict:
    """
    Standalone oracle function (no GEE).

    Args:
        plot_id:       'ETH-001' … 'ETH-008'
        claimed_date:  'YYYY-MM-DD'
        skip_download: If True, reuse scenes already in DATA_DIR

    Returns:
        Oracle dict matching SAR-001 bounty output schema.
    """
    if plot_id not in PLOTS:
        raise ValueError(f"Unknown plot_id: {plot_id}")

    coords = PLOTS[plot_id]["coords"]
    t0     = datetime.strptime(claimed_date, "%Y-%m-%d")

    pre_start  = (t0 + timedelta(days=-14)).strftime("%Y%m%d")
    pre_end    = (t0 + timedelta(days=-3)).strftime("%Y%m%d")
    post_start = (t0 + timedelta(days=1)).strftime("%Y%m%d")
    post_end   = (t0 + timedelta(days=10)).strftime("%Y%m%d")

    api = cdse_api(env_file=None)  # pass env_file arg through when wired to CLI

    # ── Search & download ──
    print(f"\nSearching pre-event scenes ({pre_start} → {pre_end})...")
    pre_products = search_scenes(api, coords, pre_start, pre_end)
    print(f"  Found {len(pre_products)} scenes")

    print(f"Searching post-event scenes ({post_start} → {post_end})...")
    post_products = search_scenes(api, coords, post_start, post_end)
    print(f"  Found {len(post_products)} scenes")

    if not pre_products:
        raise RuntimeError(f"No pre-event S1 scenes found for {plot_id} in window {pre_start}→{pre_end}")
    if not post_products:
        raise RuntimeError(f"No post-event S1 scenes found for {plot_id} in window {post_start}→{post_end}")

    if not skip_download:
        print("\nDownloading pre-event scenes...")
        pre_safes  = download_scenes(api, pre_products,  DATA_DIR / "pre")
        print("Downloading post-event scenes...")
        post_safes = download_scenes(api, post_products, DATA_DIR / "post")
    else:
        pre_safes  = sorted((DATA_DIR / "pre").glob("*.SAFE"))
        post_safes = sorted((DATA_DIR / "post").glob("*.SAFE"))
        if not pre_safes or not post_safes:
            raise FileNotFoundError("--skip-download set but no .SAFE dirs found in data/s1_scenes/")

    # ── Preprocess with SNAP ──
    proc_dir = DATA_DIR / "processed"
    print("\nPreprocessing pre-event scene(s) with SNAP...")
    pre_tifs = [preprocess_scene(s, proc_dir) for s in pre_safes]
    print("Preprocessing post-event scene(s) with SNAP...")
    post_tifs = [preprocess_scene(s, proc_dir) for s in post_safes]

    # Use first scene from each window (median compositing not straightforward in rasterio)
    # TODO: mosaic multiple scenes when ≥2 passes available
    pre_tif  = pre_tifs[0]
    post_tif = post_tifs[0]

    # ── Delta-dB ──
    print(f"\nComputing delta-dB for {plot_id}...")
    delta_stats = compute_delta_stats(pre_tif, post_tif, coords)
    print(f"  delta_VV_mean = {delta_stats['delta_VV_mean']} dB")
    print(f"  delta_VH_mean = {delta_stats['delta_VH_mean']} dB")

    status, confidence = compute_confidence(delta_stats)

    all_scene_ids = (
        [p["title"] for p in pre_products.values()] +
        [p["title"] for p in post_products.values()]
    )

    result = {
        "plot_id":           plot_id,
        "claimed_date":      claimed_date,
        "status":            status,
        "confidence":        confidence,
        "sar_delta_db":      delta_stats["delta_VV_mean"],
        "sar_delta_vv_std":  delta_stats["delta_VV_std"],
        "sar_delta_vh_mean": delta_stats["delta_VH_mean"],
        "scene_ids":         all_scene_ids,
        "pre_window":        f"{pre_start}/{pre_end}",
        "post_window":       f"{post_start}/{post_end}",
        "verification_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "method":            "standalone_SNAP_S1_GRD_delta_dB_heuristic_v0"
    }

    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="POD Oracle — SAR plow detection (standalone)")
    parser.add_argument("--plot",          required=True,      help="Plot ID e.g. ETH-001")
    parser.add_argument("--date",          required=True,      help="Claimed plowing date YYYY-MM-DD")
    parser.add_argument("--skip-download", action="store_true", help="Reuse cached .SAFE dirs")
    parser.add_argument("--env", default=None, help="Path to .env file (default: pod-agents/.env.devnet)")
    args = parser.parse_args()

    load_env(args.env)

    try:
        result = predict_plowing(args.plot, args.date, skip_download=args.skip_download)
    except Exception as e:
        sys.exit(f"Error: {e}")

    print("\n── Oracle Result ────────────────────────────────")
    print(json.dumps(result, indent=2))

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"oracle_standalone_{args.plot}_{args.date}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n✅ Saved → {out_path}")


if __name__ == "__main__":
    main()
