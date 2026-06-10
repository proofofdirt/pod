# oracle/satellite/ndvi — Sentinel-2 Vegetation & Yield Analysis

NDVI time-series processing for sorghum and maize feed crops in Ethiopia's Omo Valley. Yield prediction 6–8 weeks pre-harvest enables MENA buyers to price forward contracts with confidence.

## What Gets Built Here

- **Preprocessing:** Atmospheric correction (L2A), cloud masking (SCL band), phenological stage classification
- **Yield models:** NDVI time-series regression calibrated for sorghum and maize (SNNP Region growing conditions)
- **Validation tools:** RMSE comparison against Turmi field yield records

## Active Bounty

→ [BOUNTY-002: NDVI Yield Prediction — Sorghum & Maize](../bounties/NDVI-002.md) — reward: USDC/SOL from the DAO treasury

## Key Technical Notes

- Target RMSE < 15% of mean yield
- Prediction must be issuable 6–8 weeks before harvest NDVI decline
- Crops in scope: sorghum and maize (primary KSA animal feed import commodities)
- GEE collection: `COPERNICUS/S2_SR_HARMONIZED`
- Output: yield prediction in tons/hectare with confidence interval

## Data Sources

- Sentinel-2 L2A (GEE: `COPERNICUS/S2_SR_HARMONIZED`) — UKE Valley pilot region
- 3 seasons of pre-compiled NDVI time-series in `../data/`
- Turmi yield records 2024–2025 (limited distribution — Discord request)
