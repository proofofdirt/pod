# Workflow: Oracle-Gated Tranche Release

## Overview

The Oracle verifies agricultural milestones on-chain. SPV ops reads those PDAs and executes fiat bank wires. The chain is the audit trigger — the bank is the payment mechanism.

> **Constraint:** Ethiopian law prohibits USDC. No crypto payments to Turmi or Ethiopian subcontractors. All capital flows are fiat: PODRWA SPV KSA → Ethiopian financial institution partner → Turmi Technologies PLC.

## Trigger
Field agent submits GeoJSON plot boundary + activity claim via the agent app (`apps/agent-app/`).

## Step-by-step

1. **Orchestrator** receives GeoJSON job → routes to POD-ORACLE-01
2. **Oracle/AI Agent** queries Sentinel-1 or Sentinel-2 for plot + date window
3. **Oracle/AI Agent** runs appropriate model (T1: SAR plowing / T2: NDVI or BCS / T3: yield prediction or head count)
4. If confidence < threshold → flag for manual review + notify Turmi field agent
5. If confidence ≥ threshold → Oracle PDA written to Solana (confidence, status, contract farming status, timestamp)
6. **Capital Structuring Agent** monitors Oracle PDA; detects milestone PASS
7. **Capital Structuring Agent** notifies SPV ops via tranche dashboard (pod-dashboard SPV view)
8. **SPV ops** reviews Oracle PDA on dashboard → approves fiat wire instruction
9. PODRWA SPV KSA executes wire → Ethiopian financial institution partner → Turmi Technologies PLC (ETB)
10. **Capital Structuring Agent** logs disbursement hash on Solana via vault `approve_tranche` instruction (audit trail — not a payment)
11. **Analytics Agent** records event in KPI dashboard
12. **Orchestrator** updates `shared-memory/active-corridors.md`

## Tranche Gates

| Tranche | Oracle Check | On-Chain Action | Off-Chain Action |
|---------|-------------|-----------------|-----------------|
| T1 | SAR plowing confirmed ≥0.85 + compliance PASS | Vault → T1_APPROVED + disbursement hash | SPV wire → ETH bank → Turmi |
| T2 | NDVI on target ≥0.75 OR BCS within range ≥0.80 | Vault → T2_APPROVED + disbursement hash | SPV wire → ETH bank → Turmi |
| T3 | Yield prediction ±15% OR livestock head count verified | Vault → T3_APPROVED + disbursement hash | SPV wire → ETH bank → Turmi |
| T4 | Export payment confirmed received by SPV | Vault → EXPORT_CONFIRMED + hash | SPV releases holdback to Turmi |

## Failure paths
- Oracle FAIL → Orchestrator notifies Corridor Agent + Turmi field agent; tranche held
- Compliance breach → Legal Agent alerted; vault blocked until resolved
- SPV ops does not approve within SLA → Orchestrator escalates to ops@proofofdirt.com
- SME escalation → Engagement Agent posts to Discord #oracle-review
