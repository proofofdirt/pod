# Proof of Dirt — Build Roadmap

**June 2026 · Single source of truth for this project**

---

## 1. Goal

Finance, verify, and export Ethiopian agricultural products — **animal feed, live animals, and Halal carcass meat** — to MENA markets (KSA first), using oracle-verified ground truth as the trust layer for capital, while complying with Ethiopia's prohibition on stablecoins and cryptocurrencies.

The Oracle's role is **on-chain verification, recordkeeping, and automated milestone confirmation. Every money movement is a fiat exchange.**

---

## 2. Operating Model (locked decisions)

1. **Architecture:** fiat capital + on-chain verification. The Solana layer carries verified data only — oracle records, financing records, tranche approval events, receipt tokens, audit hashes. No funds move on-chain.
2. **Capital flow:** financiers fund an SPV outside Ethiopia (or lend locally — see Section 4) → on oracle-confirmed milestones, fiat (USD into Ethiopia) is wired to **service providers** via Turmi or another managed-services entity. **Money is never paid to the producer directly** — it pays tractor operators, input suppliers, feed suppliers, vets, logistics, insurers.
3. **Financing unit = farm; data unit = plot.** Farms typically contain multiple plots. GeoJSON is captured per plot; financing requirement, ROI, credit scoring, dashboards, and tranches aggregate per farm. **The trust tech works for plots from 1 ha and above.** Any minimum viable farm size for financing is a stage-level economics setting (it covers agent and infrastructure cost), decided by the DAO and expected to fall as costs drop — it is not a limit of the technology.
4. **Privacy model:** unfunded farms — with estimated production-cost financing requirement, ROI, and credit band — are visible to every logged-in financier. Once a farm is financed, all operational data (plowing records, vegetation/yield, animal records, export, repayment) is visible **only to the financing party** until the cycle closes and repayment completes.
5. **People payments:** field agents are paid in **ETB by Turmi payroll** against oracle-verified submissions (no wallets — web3 literacy in the agent workforce is non-existent). Developers, supervisors, and Agent Management are paid in **USDC or SOL by direct transfer from the DAO treasury multisig** (grant/donation-funded) to their own wallets. No on-chain bounty escrow — off-chain registry, direct transfers, tx signature is the audit record.
6. **No token; DAO funded by grants and donations.** The project does not mint or issue a token. The DAO maintains exactly **one crypto donation wallet (treasury multisig)** for crypto-ecosystem grants (Solana Foundation, Gitcoin, etc.) and supporter donations, plus **one fiat bank account in Ethiopia** for DFI grants and donations. Org structures (registered entity + DAO) are kept in place specifically to apply for grants and lawfully receive retail and DFI donations. An on-chain instrument for fiat-transaction recordkeeping (working name $DIRT, non-transferable, no monetary function) may be introduced later **only if recordkeeping requires it**, by governance vote. See `docs/governance.html`.
7. **V2 trigger:** if Ethiopian regulation permits stablecoin transfers, the same contracts and audit trail migrate to fully on-chain settlement (USDC direct to the managed-services entity or producer). Nothing in V1 may block that migration.

---

## 3. Credit Scoring — Producer Trust Over Time

Every producer/farmer has a permanent **Producer ID** (KYC profile + plot registry + agent assignment). Each financed cycle writes to their record:

- Financing taken (% of production cost covered), tranche compliance, oracle verification outcomes
- **Repayment history** (installments, settlements, defaults/late events)
- Yield delivered vs. predicted; contract compliance (Proclamation 578/2008)

The score compounds across seasons and directly drives the **next cycle's terms**:

| Score effect | Lever |
|---|---|
| Loan sizing | % of estimated cost of production financed (e.g., new producer 60% → proven producer 90–100%) |
| Pricing | Platform/financing fees and buyer discount spread tighten with score |
| Tranche structure | High-score producers earn advance payment of tranches; new producers reimbursed after verification |
| Insurance | Premium tier reflects verified history |
| Eligibility | Score gates larger farms, livestock cycles, multi-cycle facilities |

Scores are computed off-chain from the financing/repayment ledger and **hash-anchored on-chain** per cycle, making the history portable and auditable — the long-term asset of the platform and the basis for Ethiopian FI and DFI underwriting.

---

## 4. Capital Sources (V1 — three, in order of pursuit)

1. **Ethiopian financial institution loan (first capital).** A local bank/MFI lends working capital in ETB/USD against: (a) the **trust-tech oracle as collateral substitute** — satellite-verified land prep, vegetation, yield prediction, RFID-traced animals, tranche-gated disbursement the FI can watch live; and (b) a **buyer purchase agreement with floor pricing** as the repayment backstop. The buyer guarantees a floor price at signing; the transaction **settles at market rate at closing** — floor protects the FI's downside, market settlement preserves producer/operation upside.
2. **Buyer-financed offtake.** KSA/MENA buyers prepay production at a discount (Salam/Murabaha-compatible) via the SPV; repaid in product CIF KSA. No fundraising regulation; aligns buyer with quality.
3. **DFI impact debt.** IsDB / IFC / TDB / Gulf development funds lend to the SPV, underwritten on the oracle data package, credit-score ledger, and completed Cycle Trust Reports. Applications start early (6–12 month timelines); first facility targeted after 1–2 proven cycles.

Out of scope for V1: retail or token fundraising, USDC collection platforms, tokenization partners.

---

## 5. Verification & Tranche Model

**ROI calculation (per farm, shown to financiers):** market price feed (feed/live/carcass, FOB–CIF KSA) − full cost basis, where cost basis = inputs + labour + vet/feed + logistics (farm gate→CIF) + **insurance premium** + fees. Investor return shown at market rate; buyer financing shown with discount offer from the managed-services entity.

| Cycle | Disbursement structure | Oracle gates |
|---|---|---|
| **Feed production** | 3 tranches | T1 inputs: SAR plowing confirmed + contract/compliance PASS → T2 mid-season: NDVI growth on track → T3 pre-harvest: yield prediction within band |
| **Animal husbandry** (live/carcass) | Purchase reimbursement + monthly | **Animal purchase reimbursed once intake is complete and the RFID tag is installed** (geolocated photo + RFID documented in the agent app; RFID = per-animal identity used for traceability through export). Then **monthly**: feed, vet, and other expenses **reimbursed — or paid in advance to service providers** for high-credit-score operations — gated on BCS score ≥ 2.5, improving trajectory, confidence ≥ 0.80, head count verified |
| **Export & settlement** | Final | Customs/export docs → buyer receipt CIF KSA → settlement **at market rate** (floor applies only if market < floor) → FI/buyer/DFI repaid in fiat → producer credit score updated → cycle COMPLETE on-chain |

Every approval emits an on-chain event with a `disbursement_hash` tying it to the off-chain fiat wire record.

---

## 6. Agent App — Build on the Turmi Baseline

The working baseline lives in `D:\TurmiAppDev` (`turmi-frontend-lite` Next.js dashboard + `turmi-backend-lite` Django/PostGIS API). It already covers **farm management** (farmers, farms, plots, KYC, agent assignment), **cost-of-production recording** (crop financing templates, livestock cost templates, disbursement lines), **contract capturing** (workflow statuses, buyback fields, templates, documents), financing lifecycle (request → approval → disbursement → repayment installments/records), market rates, buyback settlement, and remote-sensing hooks. See `apps/agent-app/BASELINE.md`.

**Required upgrades (in priority order):**

1. **RFID animal registry** — per-animal record: RFID tag ID, intake date, geolocated intake photo, owner farm, BCS history; intake-complete event triggers purchase reimbursement; traceability through fattening → slaughter → export
2. **Offline-first mobile capture** for field agents (plot GeoJSON, photos, receipts, contract signing) syncing into the baseline API — ETB earnings view, no wallets
3. **Credit scoring module** — score computation from the existing repayment ledger; score surfaces on farmer profile and financier dashboard; terms engine (loan %, fees, advance-vs-reimburse)
4. **Insurance line items** in cost templates and ROI output; policy documents on the farm record
5. **Oracle integration** — hash-anchor contracts, datasets, scores, and milestone verifications on-chain; consume SAR/NDVI/BCS results as tranche gates
6. **Financier dashboard** (public unfunded / private funded views) and SPV/FI ops wire queue

---

## 7. Build Phases

### Phase 0 — Repo & Foundations (Weeks 1–2)
- [ ] Initialize git in this folder (owner does this); CI scaffold; branch strategy (`main`/`develop`/`feature/*`)
- [ ] Stand up TurmiAppDev baseline locally (Docker) and confirm the lite route surface runs
- [ ] Confirm bounty specs in `bounties/` against this roadmap

### Phase 1 — Data & Verification Layer + Legal Track (Months 1–3)
- [ ] Plot/farm registry hardened: per-plot GeoJSON, farm aggregation, area/overlap validation
- [ ] Price feeds live (feed FOB/CIF, live animal, carcass) — monthly oracle publishing
- [ ] CoP + logistics datasets v1 (insurance premium included), hash-anchored
- [ ] ROI calculator per farm (market-rate return + buyer discount view)
- [ ] SAR plowing + NDVI pipelines on pilot AOI; BCS model started
- [ ] AI competition prep: package labeled SAR/NDVI challenge datasets + baseline notebooks (see `bounties/AI-COMPETITIONS.md`)
- [ ] RFID animal registry + intake flow in agent app; offline mobile capture MVP
- [ ] Credit score v0: scoring rules defined, computed from existing repayment ledger
- [ ] **Legal (parallel):** SPV jurisdiction + formation; Shariah advisor; buyer offtake template **with floor-price + market-settlement clause**; Ethiopian FI partner engagement with oracle-as-collateral proposal; NBE-compliant USD inflow design
- **Gate →** one satellite module verifying a real plot + FI/buyer term discussions underway

### Phase 2 — Tranche Engine + First Capital (Months 4–6)
- [ ] Vault program: financing records, tranche approval events with disbursement hashes, cycle state machine (no token transfers)
- [ ] Financier dashboard: public unfunded-farm list (financing requirement, ROI, credit band) → privacy flip on funding → FI/SPV ops wire queue
- [ ] BCS scoring live; monthly livestock tranche flow end-to-end in staging
- [ ] 3–5 pilot farms onboarded with full data
- [ ] **First capital closed: Ethiopian FI loan (oracle collateral + floor-price offtake) and/or buyer prepayment**; DFI applications submitted with the data package
- **Gate →** first financing committed + 10+ farms live

### Phase 3 — First Funded Cycles (Months 7–9)
- [ ] Feed cycle: T1→T2→T3 wires on oracle confirmation, every wire hash-anchored
- [ ] Fattening cycle: RFID intake reimbursement + monthly BCS-gated disbursements
- [ ] Yield prediction live; export margin calculator (gated); insurance claims flow tested
- [ ] Launch external AI competitions (Zindi/Kaggle/AI for Good) to beat the SAR + NDVI baselines; winning models integrated open source
- [ ] Credit scores updating from live repayment events

### Phase 4 — Export, Settlement, Proof (Months 10–14)
- [ ] First export CIF KSA; settlement at market rate; FI/buyer repaid; producer scores updated
- [ ] Cycle Trust Report published — the DFI diligence asset
- [ ] **Gate →** first DFI facility closed on the strength of 1–2 proven cycles

### Phase 5 — Scale (Month 15+)
- [ ] Score-driven terms live (advance payments, larger loan %, lower fees for proven producers)
- [ ] More farms, second FI partner, additional buyers/corridors; new commodity categories
- [ ] Lower the per-farm financing minimum as agent/infrastructure costs fall; cooperative aggregation reaches the smallest producers (tech already works at 1 ha plot level)
- [ ] Evaluate monetization for sustainability (compensates dev + leadership): trust-tech-as-a-service for **banks, DFIs, and insurers** — oracle access subscriptions, white-label licensing, verification-per-cycle pricing
- [ ] **Regulatory watch:** Ethiopia permits stablecoins → execute V2 fully on-chain settlement

---

## 8. Repository Structure

```
PODFinal/
├── ROADMAP.md                  # this file
├── docs/                       # dev-guidance.html, governance, budget, org structure
│   ├── legal/                  # Procl. 578/2008, NBE + KSA checklists, MSA template
│   └── financiers/             # corridor model, ops runbook, agent specs
├── oracle/
│   ├── satellite/              # SAR + NDVI pipelines (GEE) + research reference
│   ├── pricing/                # commodity price feeds, publishing guide, trade restrictions
│   ├── costs/                  # CoP + logistics datasets (insurance-inclusive), hash-anchored
│   ├── roi/                    # financial model (per-plot/farm/corridor economics)
│   └── api/                    # oracle REST API + on-chain anchoring
├── programs/pod-vault/         # Anchor: financing records + approvals (no tokens, no transfers)
├── apps/
│   ├── agent-app/              # baseline = D:\TurmiAppDev (see BASELINE.md) + upgrades
│   ├── financier-dashboard/    # buyers, DFIs, Ethiopian FI partners
│   └── contributor-dashboard/  # dev bounties, payouts, agent-mgmt ETB reports
├── bounties/                   # single canonical bounty folder
├── workflows/                  # tranche release, new corridor, grant application
├── scripts/                    # ops reporting, payout tooling
└── assets/branding/
```

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Ethiopian FI unfamiliar with oracle-as-collateral | Lead with the live dashboard + floor-price offtake backstop; start with one pilot facility, small ticket |
| Floor-price buyer reneges at settlement | Binding offtake with floor clause; settlement at market only above floor; SPV holds export docs |
| FI/SPV/DFI timelines slip | Three capital sources pursued in parallel; buyer prepayment carries cycle 1 if needed |
| Single-operator dependence (Turmi) | Contracts name a substitutable "managed services entity"; oracle data is operator-agnostic |
| FX / USD inflow friction | NBE-compliant design from Phase 1; wires only to service providers |
| Oracle errors gate real money | Accuracy floors (SAR >90%, BCS confidence ≥0.80), held-out validation, human ops sign-off on every wire |
| New-producer default | Credit-score-sized loans (lower % of CoP), insurance in cost basis, reimburse-after-verify for unproven producers |
| Animal substitution/fraud | RFID per animal + geolocated photos + BCS continuity checks from intake to export |
