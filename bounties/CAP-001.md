# BOUNTY CAP-001 — Ethiopia/KSA Financial Model

**Reward:** USDC or SOL, paid by direct transfer from the DAO treasury multisig (grant/donation-funded; amount published on the bounty issue)  
**Status:** Open  
**Repo:** pod-capital

## What to Build
A Python financial model (`models/ethiopia-ksa-model.py`) that calculates:
- Per-plot financing economics (cost, expected return, default risk)
- Corridor-level P&L across a season
- LP return scenarios (base, stress, upside)
- Break-even analysis for minimum viable corridor scale

## Inputs
- Plot size (ha), crop type, historical yield (kg/ha)
- Input costs (USD/ha), harvest costs (USD/ha)
- Commodity price (USD/tonne)
- Tranche schedule (T1: 25%, T2: 35%, T3: 40%)
- Default rate assumption (0–15%)
- FX rate (USD/ETB) + volatility

## Outputs
- Per-plot: expected LP return, producer net income delta, break-even yield
- Corridor: total capital required, projected return, default scenarios
- Sensitivity tables for commodity price and default rate

## Acceptance Criteria
- Jupyter notebook + clean Python module
- Documented assumptions
- Validated against at least one real Desafarm plot (GeoJSON in `02_Land-Data/`)
