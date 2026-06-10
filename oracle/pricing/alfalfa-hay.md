# Alfalfa Hay -- CIF Price Tracker

HS Code: 1214.10 | Unit: USD/ton CIF | Sources: USDA FAS, CEIC, grainsprices.com

---

## Context

Saudi Arabia is one of the world's largest alfalfa importers. The Kingdom banned domestic alfalfa
production in 2018 (water conservation policy) making it 100% import-dependent. Primary suppliers
have shifted from USA toward Sudan, Argentina, and Australia following KSA's US alfalfa restrictions.

Ethiopia does not currently export alfalfa -- this commodity is a COST input for PoD livestock operations,
not an export product. Track CIF Jeddah to model feed cost for the animal fattening vaults.

---

## Price Table (update monthly)

| Date | Market | Port | Grade | USD/ton CIF | Origin | Source |
|---|---|---|---|---|---|---|
| 2026-04 | Saudi Arabia | Jeddah | Premium | ~430 | Australia | CEIC / USDA FAS |
| 2026-04 | Saudi Arabia | Jeddah | Standard | ~390 | Sudan | USDA FAS estimate |
| 2026-03 | Saudi Arabia | Jeddah | Premium | ~435 | Australia | CEIC |
| 2026-01 | Saudi Arabia | Jeddah | Premium | ~445 | USA/Australia | CEIC (all-time high period) |

*SAR equivalent: multiply USD/ton by current SAR/USD rate (~3.75 fixed peg)*
*SAR/bale (75kg): 29.55 SAR/bale = ~394 SAR/ton = ~$105/ton -- this is RETAIL not CIF import*

---

## MENA Market Spread (indicative, last updated May 2026)

| Market | Est. CIF premium vs Jeddah | Notes |
|---|---|---|
| UAE (Jebel Ali) | +$15-25/ton | Re-export premium, quality grade higher |
| Kuwait | +$10-20/ton | Smaller volumes, less competition |
| Qatar | +$20-30/ton | Premium quality required |
| Egypt | -$30-50/ton | Lower grade accepted, high volume |
| Jordan | +$5-15/ton | Aqaba proximity to Saudi |
| Bahrain | +$5-10/ton | Small market, KSA-linked pricing |
| Oman | +$10-20/ton | Growing dairy sector demand |

---

## Origin Supply Analysis

| Origin | Market share est. | Strengths | Weaknesses |
|---|---|---|---|
| Australia | ~35% | Quality, reliability, no phytosanitary issues | Long shipping, high freight |
| Sudan | ~25% | Low cost, proximity | Quality inconsistency, logistics |
| USA | ~15% | Premium quality | KSA restrictions on some shipments |
| Spain | ~10% | EU quality standards | Higher price |
| Argentina | ~10% | Competitive price | Long shipping, currency risk |
| Pakistan | ~5% | Proximity, low cost | Quality variable |

---

## Price Alerts
- Month-over-month change >10%: alert ops+analytics@proofofdirt.com
- Sudan supply disruption (political instability): immediate alert -- major price impact risk
- Australian drought events: monitor BoM seasonal outlook

## Data Update Instructions
1. Check USDA FAS GAIN Saudi Arabia (apps.fas.usda.gov) for latest semi-annual report
2. Check CEIC for Saudi Arabia average prices of goods: alfalfa series
3. Check grainsprices.com FOB section and add $50-70/ton for CIF Jeddah freight
4. Update table above, add new row, keep last 12 months visible
