# Cost Datasets (off-chain, hash-anchored)

Holds the cost-of-production and logistics datasets:
- CoP per commodity/cycle/farm tier: inputs, labour, vet, feed, **insurance premium**, certification
- Logistics: farm gate -> processing -> export docs -> freight -> CIF KSA, per category
- Each published dataset version is hashed and anchored on-chain by the Oracle API

Baseline source: turmi-backend-lite `finance` cost templates (CropFinancingTemplate,
LivestockCostTemplate) — extend with insurance lines and export to this dataset format.
