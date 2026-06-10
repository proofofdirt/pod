# BOUNTY-002 — NDVI Yield Prediction (Sorghum & Maize, Omo Valley)

**Repository:** `proofofdirt/pod` → `oracle/satellite/ndvi/`  
**Status:** 🟢 OPEN  
**Reward:** USDC or SOL, paid by direct transfer from the DAO treasury multisig (grant/donation-funded; amount published on the bounty issue)  
**Deadline:** 10 weeks from claim date  
**Claim:** Comment on [Issue #2](https://github.com/proofofdirt/pod/issues)

---

## Objective

Build a Sentinel-2 NDVI time-series model that predicts **sorghum and maize** yield **6–8 weeks before harvest** in Ethiopia's Omo Valley. Target RMSE of less than 15% of actual mean yield.

---

## Why These Crops, Why This Timing

KSA imports **100% of its animal feed requirements**. Ethiopia's Omo Valley — with its fertile soils and growing season — is geographically positioned to be a key supplier of sorghum and maize to MENA animal feed markets. These are the primary crops in the POD Oracle's MVP commodity tracking pipeline.

Yield prediction issued 6–8 weeks pre-harvest gives MENA commodity buyers the forward visibility they need to price import contracts with confidence. This data feeds directly into the POD Oracle's forward-contract price transparency layer.

---

## Technical Requirements

### Input
- Plot GeoJSON polygon (minimum 1 ha validated)
- Sentinel-2 time series covering the growing season (planting onset → harvest)

### Output
```json
{
  "plot_id": "POD-ETH-0042",
  "crop": "sorghum",
  "prediction_date": "2026-09-15",
  "estimated_harvest_date": "2026-11-10",
  "yield_t_ha": 3.4,
  "confidence_interval_low": 2.9,
  "confidence_interval_high": 3.9,
  "phenological_stage": "grain_fill",
  "ndvi_peak": 0.88
}
```

### Technical Constraints
- **RMSE:** < 15% of mean yield on the Omo Valley validation set
- **Prediction horizon:** Model output must be issuable 6–8 weeks before observable harvest NDVI decline
- **Crops in scope:** Sorghum and maize (other crops out of scope for this bounty)
- **Calibration region:** SNNP Region / Omo Valley growing conditions
- **Cloud handling:** Must apply cloud masking using Sentinel-2 SCL band; persistent cloud gaps must be handled (interpolation or gap-filling strategy required)

---

## Data Available to Claimant

### Sentinel-2 Imagery (Free)
- GEE collection: `COPERNICUS/S2_SR_HARMONIZED`
- Pilot region: Omo Valley, SNNP Region, Ethiopia
- Bands of interest: B4 (Red), B8 (NIR) for NDVI; full multispectral stack for LAI / EVI

### Pre-compiled Data (in `oracle/satellite/data/`)
- 3 seasons of NDVI time-series for the Omo Valley pilot area
- Phenological calendars for sorghum and maize in the SNNP region

### Yield Records (Restricted)
- Turmi Technologies field yield records from the 2024–2025 test season
- Limited distribution — request in Discord `#oracle-pipeline` after claiming the issue

---

## Technical Approach

NDVI is the normalised difference vegetation index: `NDVI = (NIR - Red) / (NIR + Red)`.

A time-series approach tracks the crop through its full phenological cycle:
1. **Planting onset detection** — initial NDVI rise above bare soil baseline
2. **Vegetative stage** — rapid NDVI increase
3. **Peak greenness** — NDVI plateau (highest correlation with final yield)
4. **Grain fill / senescence** — NDVI begins declining (harvest imminent)

The **6–8 week pre-harvest prediction** should be made at or just before the peak NDVI stage — the signal is most stable and contains the strongest yield information at this point.

**Suggested modelling approaches:**
- NDVI integral (season cumulative NDVI) correlated with yield
- Phenological stage regression (peak NDVI, rate of green-up, time-to-peak)
- LSTM or temporal CNN on the full NDVI time series
- PROSAIL radiative transfer model for LAI → yield estimation (more complex but publication-grade)

---

## Evaluation Criteria

| Criterion | Weight |
|---|---|
| RMSE vs. Turmi yield records on validation set | 50% |
| Prediction issued ≥6 weeks pre-harvest (timing constraint) | 20% |
| Cloud gap handling strategy | 15% |
| Code quality, documentation, reproducibility | 15% |

---

## Deliverables

- Trained model (weights + serialized format)
- `predict_yield(geojson_polygon, season_start_date)` function meeting the output schema
- Google Earth Engine script for Sentinel-2 time-series extraction
- Validation report: RMSE, timing analysis, cloud coverage impact analysis
- Jupyter notebook demonstrating the full pipeline end-to-end
- `requirements.txt` + `README.md` in the PR

---

## Submission

1. Comment on [Issue #2](https://github.com/proofofdirt/pod/issues) to claim
2. Discuss your approach in Discord `#oracle-pipeline`
3. Fork `proofofdirt/pod`, build in `oracle/satellite/ndvi/`
4. Submit PR with validation results and your **Solana wallet address**

---

## Reward Distribution

- **USDC (or SOL)** transferred directly to your Solana wallet upon PR merge — the transaction signature is the payment record
- Long-term core contributors may receive continued grant-funded engagement (the project does not issue a token)

---

*Questions: Discord `#oracle-pipeline` or comment on Issue #2*  
*© 2026 Proof of Dirt Ecosystem · MIT License*
