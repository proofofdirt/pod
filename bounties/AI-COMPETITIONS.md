# AI Competition Program — Optimizing SAR & NDVI Detection

**Status:** Planned (Phase 1 prep → Phase 2–3 launch) · **Funding:** grant/donation budget (USD prizes) · **License requirement:** all winning solutions released MIT

## Why

Our in-house SAR plowing and NDVI yield models set the baseline. External ML competitions bring hundreds of specialized practitioners to beat that baseline cheaply — prize money is paid only for verified improvement, and every winning model becomes open source for the ecosystem.

## Competition Tracks

| Track | Task | Metric | Baseline to beat |
|---|---|---|---|
| 1. SAR plowing detection | Classify plowing events on Ethiopian plots 1 ha+ from Sentinel-1 GRD (scored per plot-size band) | F1 / accuracy on held-out plots | ≥90% accuracy (current floor) |
| 2. NDVI yield prediction | Sorghum/maize yield 6–8 weeks pre-harvest from Sentinel-2 time series (+S1 fusion for cloud gaps) | RMSE | <15% of mean yield |
| 3. Livestock BCS (later) | Body-condition score from geotagged field photos | MAE vs. vet ground truth | <0.5 BCS points |

## Platforms (in order of fit)

1. **Zindi** — Africa-focused data science community; lowest cost, strongest mission fit, African talent pipeline doubles as recruiting.
2. **Kaggle Community Competitions** — free to host, largest reach; needs a well-packaged dataset and clear leaderboard metric.
3. **DrivenData** — social-impact ML competitions; strong fit for DFI co-branding.
4. **AI for Good (ITU)** — challenge tracks + visibility with UN/DFI audiences; longer lead time.
5. **ESA / Copernicus innovation challenges** — natural fit for Sentinel-based tracks; potential prize co-funding.
6. **Omdena** — collaborative project format (not prize-based); good for the BCS track where iteration with field feedback matters.

## Prerequisite: the dataset is the bottleneck

Competitions live or die on labeled ground truth. Before launch:

- [ ] Package SAR track: Sentinel-1 scene IDs + plot polygons + labeled plowing events (current: 47 positive / 23 negative — target ≥150/100 before launch; every financed cycle adds labels via agent verification)
- [ ] Package NDVI track: per-plot S2 time series + harvest-verified yields (accumulates from funded cycles)
- [ ] Privacy: generalize/offset plot coordinates or gate raw GeoJSON behind a data-use agreement; farmer identity never in the dataset
- [ ] Held-out test set kept private for leaderboard scoring
- [ ] Baseline model + starter notebook published (lowers entry barrier, anchors the metric)

## Budget & prizes

- Prize pools funded from grants (Solana Foundation, ESA/Copernicus, DFI innovation funds) and donations; typical Zindi/Kaggle community pool $3–10k per track
- Paid in USD/USDC from the DAO treasury multisig; tx/transfer is the payment record
- Optional follow-on: top performers offered paid integration bounties (see SAR-001 / NDVI-002) to productionize their models

## Success criteria

A track is worth re-running if it delivers ≥2pp accuracy (SAR) or ≥2pp RMSE (yield) improvement over baseline on the private test set, with reproducible open-source code integrated into `oracle/satellite/`.
