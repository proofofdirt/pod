# 60-Day MVP Sprint — Full Scope

**Start: Day 1 = first team sync · Target: working MVP demo on Day 60 · No descopes.**
Read with `docs/dev-guidance.html` (DEV-00 → DEV-07). This plan is the execution layer on top of it.

---

## 1. The Finish Line (Definition of Done)

A live demo any financier, DFI, or grantmaker can watch:

1. **Feed path:** pilot plot GeoJSON captured → SAR plowing confirmed (real Sentinel-1 data, pilot AOI) → oracle record published via **Switchboard** → vault financing record on devnet → **tranche approval event** with disbursement hash → visible on the financier dashboard.
2. **Livestock path:** animal intake on the **offline-first mobile app** (RFID tag + geolocated photo, captured with airplane mode ON, synced later) → intake-complete event → purchase reimbursement flagged in the SPV/FI ops queue → monthly BCS reading recorded.
3. **Dashboard:** public unfunded-farm list (financing requirement, insurance-inclusive ROI, credit band) → farm funded → **privacy flip** (server-side 403 for everyone but the financing party) → private operational view → ops wire queue.
4. **Proof pack:** mock Cycle Trust Report + 10-minute demo script, rehearsed.

Everything devnet. No real money, no token, no on-chain transfers — records and events only.

---

## 2. Team & Capacity

| Who | Hours/wk | Owns |
|---|---|---|
| Dev Lead A (Chain & Data) | 20 | Vault program (DEV-05), Switchboard publishing (DEV-02), anchoring service, oracle API |
| Dev Lead B (Interfaces) | 20 | Financier dashboard (DEV-06), mobile capture app (DEV-04), auth/privacy |
| Intern 1 (A-track) | 10–20 | Satellite pipeline (DEV-01), dataset prep, oracle publisher runs |
| Intern 2 (B-track) | 10–20 | Django baseline upgrades (DEV-03: RFID, scoring v0, insurance), dashboard components |
| Claude agents (Cowork Pro) | — | Scaffolding, tests, IDL/clients, migrations, review drafts — per the AI Prompts appendix in dev-guidance |

≈ 70 person-hours/week → ≈ 560–600 hours over 60 days. Full-scope estimate is 350–450 focused hours — the margin is real but thin; protect it with the working agreements below.

## 3. Working Agreements

- **WIP limit: one work package per person.** Claude generates faster than part-time leads can review — review capacity is the bottleneck, so never open a second package before the first merges.
- **AI-assisted, human-owned:** agents draft, you verify against the actual code (especially baseline model names and oracle schemas). Disclose substantial AI assistance in the PR. You own the merge.
- **Branches:** `main` (protected) ← `develop` ← `feature/devXX-short-name`. PR review SLA 3 business days; leads cross-review each other's track weekly.
- **Cadence:** Monday 30-min sync (blockers + package assignment), Friday demo-what-you-built in #dev-log. Every Friday ends with the repo in a demoable state.
- **Hard rules:** no on-chain money movement, ever; no manual oracle overrides; no secrets in the repo; devnet only; Windows devs use WSL for the Anchor toolchain.

---

## 4. Week-by-Week Plan

### Days 1–7 — Foundations (everything starts in parallel)
- **Intern 1:** GEE is already set up — run the JS scripts (`gee_sar_plow.js`, `hybridsen1sen2plowdetectionee.js`, NDVI scripts) on the pilot AOI **day 1–3**; team reviews outputs; pick the demo plot + historical plowing event with known date
- **Dev Lead A:** Sprint 0 (DEV-00): devnet wallets, Anchor toolchain (WSL), placeholder program deployed, repo conventions; start vault account structs
- **Dev Lead B:** stand up Turmi baseline locally (Docker); scaffold financier dashboard (Next.js) and Expo mobile app shells
- **Intern 2:** baseline tour; draft `livestock/` Django models (AnimalRecord, BCSReading) with Claude; migration plan reviewed by Lead B
- **Gate G1 (Day 7):** satellite outputs reviewed on a named demo plot · vault skeleton compiles on devnet · baseline runs locally

### Days 8–14 — First real records
- **Intern 1:** port reviewed JS logic into the Python pipeline (`run_oracle.py`); produce the demo plot's SAR confirmation JSON with confidence + scene IDs
- **Dev Lead A:** `record_subscription` + oracle record PDA writer working on devnet; Switchboard queue + first aggregator feed created (DEV-02)
- **Dev Lead B:** mobile: SQLite offline queue + GPS/photo capture working on a physical Android device
- **Intern 2:** RFID models merged; intake API endpoint; insurance premium line type added to cost templates
- **Gate G2 (Day 14):** a real SAR verification exists as an on-chain record on devnet — the heartbeat of the whole MVP

### Days 15–28 — Core build
- **Dev Lead A:** `approve_tranche` with full gate logic (feed: SAR/NDVI; livestock: intake + BCS), `TrancheApprovedEvent` + disbursement hash; anchor test suite (happy path + all rejection paths); monthly publisher run scripted
- **Intern 1:** NDVI time-series for the demo plot; price feeds published to Switchboard (sheep KSA + sorghum to start); CoP dataset v0 with insurance line, hash-anchored
- **Dev Lead B:** dashboard public view live against devnet + baseline API (farm list, financing requirement, ROI, credit band); financier auth (email + 2FA invited accounts)
- **Intern 2:** credit scoring v0 (`finance/scoring.py`) computed from baseline repayment tables; score surfaces on farmer profile + dashboard band
- **Gate G3 (Day 28):** feed path runs end-to-end from pipeline → record → approval event → visible on dashboard (rough is fine)

### Days 29–42 — Livestock path + privacy flip
- **Dev Lead B + Intern 2:** mobile RFID intake flow (tag entry/scan + geolocated photo, offline) → sync → intake-complete event → reimbursement flagged in ops queue; BCS reading entry
- **Dev Lead A:** anchoring service (contract hash, GeoJSON hash, score snapshot, dataset versions); ops wire queue feed from approval events
- **Dev Lead B:** privacy flip done properly — server-side authorization, funded farm 403s for non-financing parties (test it, don't eyeball it)
- **Intern 1:** banded accuracy report for SAR on the AOI (1–10 / 10–100 / 100+ ha) — honest numbers for the demo Q&A
- **Gate G4 (Day 42):** livestock path runs end-to-end on a staged intake; privacy flip passes its tests

### Days 43–53 — Integration, hardening, CI
- Full E2E test pass per DEV-07 (both paths + offline submission + 403 test); GitHub Actions CI green on anchor + frontend tests
- Demo data seeded: 2–3 additional unfunded farms so the public list looks real
- Mock Cycle Trust Report built from the demo plot's actual data
- Bug-fix burn-down; **feature freeze Day 53** — nothing new after this, only fixes
- **Gate G5 (Day 53):** freeze; demo runs start-to-finish without hands in the engine

### Days 54–60 — Demo polish + handoff to fundraising
- 10-minute demo script written and rehearsed (×3, different drivers — it can't depend on one person)
- Record a backup screen-capture of the full demo (demos break; videos don't)
- Package for DevRel/Grants: demo access, Trust Report, banded accuracy report, architecture one-pager
- Retro + backlog for the field phase (Switchboard hardening, multi-farm onboarding, BCS ML model)
- **Day 60: MVP demo delivered. Fundraising phase begins.**

---

## 5. Milestone Gates (the schedule's truth-tellers)

| Gate | Day | Must be true | If missed |
|---|---|---|---|
| G1 | 7 | Satellite outputs reviewed; vault compiles; baseline runs | Fix env blockers before anything else |
| G2 | 14 | Real SAR verification on devnet as an on-chain record | Drop Switchboard to direct PDA writes (revisit later) — decide here, not later |
| G3 | 28 | Feed path end-to-end | Pull Intern 2 onto dashboard; defer scoring v0 to W7 |
| G4 | 42 | Livestock path + privacy flip | Stage the mobile sync (manual upload) for demo; finish offline sync in W7 |
| G5 | 53 | Feature freeze, clean demo run | Push demo to Day 67 — never demo unfrozen code |

The fallbacks exist so a slip costs a feature's polish, not the demo date.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Review bottleneck (20 hr/wk leads vs AI output volume) | WIP limit of 1; cross-review weekly; interns write tests for leads' code |
| Anchor/Solana toolchain friction | WSL/devcontainer from Day 1; pin versions in the repo |
| Switchboard quirks eat days | G2 fallback: direct PDA writes; Switchboard becomes a field-phase task |
| Offline mobile sync edge cases | Physical-device testing from W2, not W6; airplane-mode test in CI checklist |
| No confirmed plowing event in window | Use a historical event on the pilot AOI (date already known from the JS runs) |
| Part-time schedules collide | All work packages written down with named owners; nothing lives in someone's head |

---

*Owned by the Development Leaders · reviewed at every Monday sync · changes to gates require both leads + coordinator.*
