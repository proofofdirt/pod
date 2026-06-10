# Commodity Prices -- Schema and Update Cadence

CIF price tracking for MENA markets. Updated monthly from public sources.
Ground cost of production is NOT stored here -- that lives in corridor-model/.

---

## Price Schema

Each commodity file tracks the following fields per MENA market:

```
date:              YYYY-MM (monthly)
market:            Saudi Arabia / UAE / Kuwait / Qatar / Egypt / Bahrain / Jordan / Oman
port:              Jeddah / Jebel Ali / Shuwaikh / Hamad / Alexandria / Khalifa / Aqaba / Muscat
price_usd_per_ton: CIF landed price in USD/ton
price_sar_per_ton: CIF price in SAR (for KSA market)
origin:            Brazil / Australia / USA / Pakistan / Sudan / Ethiopia / Other
source:            USDA FAS / FAO GIEWS / UN COMTRADE / selinawamucii / market contact
notes:             Seasonal variation, quality grade, shipping conditions
```

---

## Commodity Files

| File | Unit | Primary sources | Update cadence |
|---|---|---|---|
| alfalfa-hay.md | USD/ton CIF | USDA FAS, CEIC, grainsprices.com | Monthly |
| corn-silage.md | USD/ton CIF | USDA FAS, FAO GIEWS | Monthly |
| live-small-ruminants.md | USD/kg live weight | selinawamucii, OEC | Weekly |
| carcass-small-ruminants.md | USD/ton | IndexBox, trade contacts | Monthly |
| live-cattle.md | USD/kg live weight | selinawamucii, FAO | Weekly |
| carcass-cattle.md | USD/ton | FAO GIEWS, trade contacts | Monthly |

---

## Key Price Benchmarks (as of May 2026, indicative)

### Animal Feed
| Commodity | CIF Jeddah est. | Primary origin | Notes |
|---|---|---|---|
| Alfalfa hay (premium) | ~$420-440/ton | USA, Spain, Australia | KSA banned US alfalfa in 2022, shifting to Sudan/AU |
| Alfalfa hay (standard) | ~$370-395/ton | Sudan, Argentina | Growing Sudan supply |
| Corn (feed grade) | Track via USDA FAS | Brazil, Argentina, Ukraine | Highly volatile -- track weekly futures |
| Corn silage | ~$85-110/ton | Regional | Limited CIF data -- estimate from corn + processing |
| Sorghum | ~$220-260/ton | Australia, Argentina | Halal-compatible substitute for corn |

### Livestock (CIF estimates, add $0.30-0.60/kg for Ethiopia/Somalia origin)
| Commodity | Wholesale KSA | Unit | Source | Date |
|---|---|---|---|---|
| Live sheep | $3.67 - $4.20 | /kg live weight | selinawamucii | May 2026 |
| Live goats | $3.50 - $4.00 | /kg live weight | selinawamucii | May 2026 |
| Goat carcass | Estimate $6.50-8.00 | /kg | IndexBox (paid) | 2025 |
| Sheep carcass | Estimate $5.80-7.50 | /kg | IndexBox (paid) | 2025 |
| Live cattle (Brahman) | $2.20 - $2.80 | /kg live weight | FAO / trade contacts | 2025 |

---

## Seasonality Notes

- **Hajj/Eid al-Adha:** Live animal prices spike 40-80% in KSA/UAE in the 6-8 weeks before
- **Ramadan:** Increased demand for lamb/goat, moderate price lift
- **Northern hemisphere winter:** Alfalfa supply tightens, prices rise Jan-Mar
- **Brazilian harvest (Apr-Jun):** Corn prices typically soften -- watch for buying opportunity
- **Ethiopian dry season (Oct-Feb):** Livestock condition declines, live weight prices compress

---

## Update Responsibility
Analytics agent (POD-ANL-01) updates price tables monthly.
Alert ops+analytics@proofofdirt.com when any commodity moves >10% month-over-month.
