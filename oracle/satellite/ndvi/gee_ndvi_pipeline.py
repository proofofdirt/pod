"""
POD Oracle — Sentinel-2 NDVI Pipeline (Python)
Desafarm Plots, Omo Valley, Ethiopia

Authenticates with Earth Engine, loads plot boundaries from GeoJSON,
extracts per-plot NDVI time-series, and saves to CSV.

Requirements:
    pip install earthengine-api geojson pandas

First-time auth:
    earthengine authenticate
    (or set GOOGLE_APPLICATION_CREDENTIALS for service account)

Usage:
    python gee_ndvi_pipeline.py --start 2025-05-01 --end 2025-12-31
    python gee_ndvi_pipeline.py --plot ETH-001 --start 2025-05-01 --end 2025-12-31
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import ee
import pandas as pd


# ── Config ─────────────────────────────────────────────────────────────────

GEOJSON_PATH = Path(__file__).parent.parent.parent / \
    "pod-agents" / "shared-memory" / "plots" / "desafarm-all-plots.geojson"

GEE_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
SCALE_M        = 10          # Sentinel-2 native 10 m resolution
CLOUD_PCT_MAX  = 60          # pre-filter: drop scenes with > 60% cloud cover
OUTPUT_DIR     = Path(__file__).parent / "output"


# ── SCL Cloud Mask ──────────────────────────────────────────────────────────

def mask_s2_clouds(image):
    """Mask clouds/shadows using Sentinel-2 SCL band, scale reflectance."""
    scl = image.select("SCL")
    # Classes to remove: 0 no-data, 1 saturated, 3 shadow,
    #                    8 cloud med, 9 cloud high, 10 cirrus
    bad = [0, 1, 3, 8, 9, 10]
    mask = scl.neq(bad[0])
    for cls in bad[1:]:
        mask = mask.And(scl.neq(cls))
    return (image.updateMask(mask)
                 .divide(10000)
                 .copyProperties(image, ["system:time_start"]))


# ── NDVI ────────────────────────────────────────────────────────────────────

def add_ndvi(image):
    """Compute NDVI = (B8 - B4) / (B8 + B4) and add as band."""
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


# ── Load Plots ──────────────────────────────────────────────────────────────

def load_plots(geojson_path: Path, plot_filter: str | None = None) -> list[dict]:
    """Load plot features from GeoJSON, optionally filter to one plot_id."""
    with open(geojson_path) as f:
        fc = json.load(f)

    features = fc["features"]

    # Assign sequential ETH-00N IDs matching the GEE script
    for i, feat in enumerate(features, start=1):
        feat["properties"]["plot_id"] = f"ETH-{i:03d}"

    if plot_filter:
        features = [f for f in features if f["properties"]["plot_id"] == plot_filter]
        if not features:
            sys.exit(f"No plot found with plot_id={plot_filter}")

    return features


def feature_to_ee(feat: dict) -> ee.Feature:
    """Convert a GeoJSON Feature dict to an ee.Feature."""
    geom = ee.Geometry(feat["geometry"])
    return ee.Feature(geom, feat["properties"])


# ── Extract Time-Series ─────────────────────────────────────────────────────

def extract_ndvi_timeseries(
    plot_feature: ee.Feature,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Return a DataFrame with columns [date, ndvi_mean] for one plot.
    Runs ee.ImageCollection.getRegion — single blocking call.
    """
    geom = plot_feature.geometry()

    collection = (
        ee.ImageCollection(GEE_COLLECTION)
        .filterBounds(geom)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", CLOUD_PCT_MAX))
        .map(mask_s2_clouds)
        .map(add_ndvi)
        .select("NDVI")
    )

    # reduceRegions over the collection → list of dicts
    def reduce_image(image):
        date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd")
        result = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geom,
            scale=SCALE_M,
            maxPixels=1e9,
        )
        return ee.Feature(None, {
            "date":      date,
            "ndvi_mean": result.get("NDVI"),
        })

    reduced = collection.map(reduce_image).getInfo()

    rows = []
    for feat in reduced["features"]:
        props = feat["properties"]
        if props["ndvi_mean"] is not None:
            rows.append({
                "date":      props["date"],
                "ndvi_mean": round(float(props["ndvi_mean"]), 4),
            })

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="POD Oracle — NDVI pipeline")
    parser.add_argument("--start",  default="2025-05-01", help="Start date YYYY-MM-DD")
    parser.add_argument("--end",    default="2025-12-31", help="End date   YYYY-MM-DD")
    parser.add_argument("--plot",   default=None,         help="Single plot_id e.g. ETH-001")
    parser.add_argument("--project", default=None,        help="GEE cloud project ID (optional)")
    args = parser.parse_args()

    # ── Auth ──
    print("Authenticating with Earth Engine...")
    try:
        if args.project:
            ee.Initialize(project=args.project)
        else:
            ee.Initialize()
        print("  ✓ Earth Engine ready")
    except Exception as e:
        print(f"  ✗ Auth failed: {e}")
        print("  Run `earthengine authenticate` first, then retry.")
        sys.exit(1)

    # ── Load plots ──
    if not GEOJSON_PATH.exists():
        sys.exit(f"GeoJSON not found at {GEOJSON_PATH}")

    features = load_plots(GEOJSON_PATH, plot_filter=args.plot)
    print(f"Loaded {len(features)} plot(s) from {GEOJSON_PATH.name}")

    # ── Output dir ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_rows = []

    for feat in features:
        plot_id   = feat["properties"]["plot_id"]
        plot_name = feat["properties"]["name"]
        print(f"\n  Processing {plot_id} — {plot_name}...")

        ee_feat = feature_to_ee(feat)

        try:
            df = extract_ndvi_timeseries(ee_feat, args.start, args.end)
        except Exception as e:
            print(f"    ✗ Failed: {e}")
            continue

        if df.empty:
            print(f"    ⚠ No cloud-free observations found for {plot_id}")
            continue

        df["plot_id"]   = plot_id
        df["plot_name"] = plot_name
        all_rows.append(df)

        # Peak NDVI stats
        peak = df["ndvi_mean"].max()
        peak_date = df.loc[df["ndvi_mean"].idxmax(), "date"]
        print(f"    ✓ {len(df)} observations | peak NDVI {peak:.3f} on {peak_date}")

    if not all_rows:
        print("\nNo data extracted. Check date range and cloud conditions.")
        sys.exit(1)

    # ── Save combined CSV ──
    combined = (
        pd.concat(all_rows, ignore_index=True)
        [["plot_id", "plot_name", "date", "ndvi_mean"]]
    )

    out_csv = OUTPUT_DIR / f"desafarm_ndvi_{args.start[:7]}_{args.end[:7]}_{timestamp}.csv"
    combined.to_csv(out_csv, index=False)
    print(f"\n✅ Saved {len(combined)} rows → {out_csv}")

    # ── Summary table ──
    summary = (
        combined.groupby(["plot_id", "plot_name"])
        .agg(
            observations=("ndvi_mean", "count"),
            ndvi_min=("ndvi_mean", "min"),
            ndvi_mean=("ndvi_mean", "mean"),
            ndvi_peak=("ndvi_mean", "max"),
        )
        .round(3)
        .reset_index()
    )
    print("\nPlot Summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
