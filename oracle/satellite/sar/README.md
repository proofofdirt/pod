# oracle/satellite/sar — Sentinel-1 SAR Processing

SAR (Synthetic Aperture Radar) plowing detection for Ethiopian plots of **1 ha and above**.

Sentinel-1 C-band SAR operates on microwave frequencies that penetrate cloud cover, dust storms, and heavy rain — critical for tropical growing seasons where optical satellites are blind 70%+ of the time.

## What Gets Built Here

- **Preprocessing:** SNAP graph processing, terrain correction (RD/RTC), speckle filtering
- **Plowing detection models:** VV/VH backscatter ratio change detection across plot-size bands (1 ha+)
- **Validation tools:** Ground-truth comparison against Turmi field agent plowing logs

## Active Bounty

→ [BOUNTY-001: SAR Plowing Detection Model](../bounties/SAR-001.md) — reward: USDC/SOL from the DAO treasury

## Key Technical Notes

- Models must report accuracy by plot-size band (1–10 ha, 10–100 ha, 100 ha+)
- Use Sentinel-1 GRD IW products (VV + VH polarisation)
- Must support both GEE Python API and standalone `sentinelsat` + `rasterio` paths
- 12-day repeat pass cycle; pre/post log-ratio change detection is the primary approach
- Output schema: `{"status": "CONFIRMED|UNCONFIRMED", "confidence": float, "sar_delta_db": float, "scene_ids": list}`

## Data Sources

- Copernicus Open Access Hub: https://scihub.copernicus.eu
- GEE collection: `COPERNICUS/S1_GRD`
- Ground truth: 47 validated plowing events (currently skewed to larger plots) — request via Discord #oracle-pipeline
