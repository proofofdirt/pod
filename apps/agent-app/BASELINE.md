# Agent App — Baseline

The working baseline for the agent/operations application lives in `D:\TurmiAppDev`:

- **turmi-frontend-lite** — Next.js dashboard: farmers, farms, plots, contracts, financing
  (templates + requests + disbursements), animal husbandry, portfolio, stakeholders,
  exchange rates, activity log, satellite tile/Earth Engine proxy.
- **turmi-backend-lite** — Django (DigiAgriApp-derived) API: `kyc` (FarmerProfile, Plot,
  Kebele, agent assignment), `finance` (FinancingRequest, Disbursement, RepaymentInstallment,
  RepaymentRecord, ProduceMarketRate, BuybackSettlement, crop/livestock cost templates),
  `contracts` (workflow, buyback fields, templates, documents), `production`, `field_operations`,
  `remotesensing` / `eos_integration`, PostGIS.

This baseline already covers farm management, cost-of-production recording, and contract
capture. Build on it — do not start from scratch. Required upgrades are listed in
`ROADMAP.md` (Section: Agent App workstream): RFID animal registry + intake flow, offline-first
mobile capture, credit scoring surfaces, insurance line items, oracle hash-anchoring.
