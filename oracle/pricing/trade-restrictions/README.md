# Trade Restrictions -- Tracker Schema and Alert Workflow

Monitors active import restrictions affecting Ethiopian livestock exports to MENA markets.
A live ban on any active corridor commodity = potential capital stranding event.
POD-INTEL-01 monitors this weekly. Immediate escalation to ops@ and ir@ on any new ban.

---

## Monitoring Sources (check weekly)

| Source | What to monitor | URL | Alert method |
|---|---|---|---|
| **OIE/WOAH** | Disease event notifications for Ethiopia -- RVF, FMD, PPR, LSD, ASF | woah.int/en/disease-events | Subscribe email alerts |
| **SFDA Saudi Arabia** | Approved/suspended country list for live animal imports | sfda.gov.sa | Manual check weekly |
| **UAE MOCCAE** | Import permit status by origin for live animals | moccae.gov.ae | Manual check monthly |
| **Kuwait PAAAFR** | Live animal import restrictions | moa.gov.kw | Manual check monthly |
| **Qatar MOPH** | Animal import permit requirements | moph.gov.qa | Manual check monthly |
| **USDA APHIS** | Ethiopia animal disease status (used by all MENA vets) | aphis.usda.gov | Email alert subscription |
| **FAOLEX** | Ethiopian export regulation changes | fao.org/faolex | Monthly check |
| **Ethiopian MoA** | Domestic export permit changes | moa.gov.et | Manual check monthly |

---

## Disease Risk Matrix for Ethiopia Livestock Exports

| Disease | Abbrev | Species | Ban trigger | Typical ban duration | Last Ethiopian outbreak |
|---|---|---|---|---|---|
| Rift Valley Fever | RVF | Sheep, goats, cattle | OIE notification -- immediate ban KSA/UAE | 6-24 months | 2022-2023 |
| Foot and Mouth Disease | FMD | Cattle, sheep, goats | Most MENA markets ban | Variable, 3-12 months | Endemic (monitor serotype) |
| Peste des Petits Ruminants | PPR | Sheep, goats | Some markets ban | 3-6 months | Endemic |
| Lumpy Skin Disease | LSD | Cattle | KSA, UAE sensitive | 3-12 months | Monitor |
| African Swine Fever | ASF | Pigs only | Not relevant for PoD | -- | Not applicable |
| Anthrax | -- | All | Immediate, short duration | 2-4 months | Sporadic |

**RVF is the highest risk.** The 2022-2023 RVF outbreak in Ethiopia triggered a full KSA and UAE ban
on Ethiopian live animal imports. Duration was approximately 18 months. This type of event can strand
capital deployed in active livestock vaults. Insurance and corridor diversification are key mitigants.

---

## Active Restrictions Table (update weekly)

| Date updated | Country banned | Commodity | Restricting markets | Trigger | Status | Lifted date |
|---|---|---|---|---|---|---|
| 2026-05-31 | -- | -- | -- | No active bans known | Monitor | -- |

*Fill in as bans are identified. Keep last 24 months of history in restriction-history.md*

---

## Alert Workflow

```
New restriction detected
        |
POD-INTEL-01 confirms via 2 independent sources
        |
Immediate email: ops@proofofdirt.com + ir@proofofdirt.com
Subject: [ALERT] Trade restriction -- [Country] [Commodity] [Restricting market]
        |
ops@ assesses capital exposure in active vaults
        |
If capital at risk > $10,000: escalate to full Squads vault review
        |
Update active-restrictions.md within 24 hours
        |
Weekly report includes restriction status update
```

---

## Risk Mitigation Notes

- **Corridor diversification:** When a second corridor (e.g. Kenya/Tanzania) is activated via DAO vote,
  single-corridor ban risk is significantly reduced.
- **Multi-market routing:** If KSA bans but UAE does not, redirect shipments. Track each market
  restriction independently.
- **Timing:** Livestock vaults should ideally close (animals exported) before the Northern Hemisphere
  summer Eid window to capture peak pricing AND before the August-October East Africa disease season.
- **Insurance:** Capital deployed in livestock vaults should have trade disruption / ban insurance.
  Add this to the legal checklist in pod-capital.
