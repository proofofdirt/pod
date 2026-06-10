# BOUNTY-003 — $PODRWA Escrow Contracts (Solana/Anchor)

**Repository:** `proofofdirt/pod` → `programs/pod-vault/`  
**Status:** 🟢 OPEN  
**Reward:** USDC or SOL, paid by direct transfer from the DAO treasury multisig (grant/donation-funded; amount published on the bounty issue)  
**Deadline:** 12 weeks from claim date  
**Claim:** Comment on [Issue #3](https://github.com/proofofdirt/pod/issues)

---

## Objective

Build the $PODRWA export vault escrow system on Solana using the Anchor framework. The escrow must be Oracle-gated — payments only release when the POD Oracle confirms agricultural activity with sufficient confidence. Must include the SPV bridge module interface for SAR/USD settlement flows.

This is the financial heart of the protocol. The bounty reward reflects the criticality of this work.

---

## Why This Matters

The $PODRWA vault is the on-chain state machine for every commodity cycle. It tracks: investor subscriptions, oracle milestone states, tranche approval events, cycle completion, and investor settlement. This is the single source of truth that both the Oracle pipeline and PODRWA SPV KSA read to manage capital deployment.

> **Architectural constraint:** Ethiopian law prohibits USDC/stablecoin transactions. The vault does **not** release USDC to Turmi or Ethiopian subcontractors. Its role is: (1) maintain cycle state; (2) record oracle milestone PDAs; (3) emit tranche approval events that trigger SPV ops to execute a fiat bank wire; (4) maintain immutable financing records (no tokens by default — a non-transferable receipt record may be added only if recordkeeping requires it); (5) provide an immutable on-chain audit log of the cycle.

A bug in these contracts is a bug in investor trust and protocol integrity. Build accordingly.

---

## Technical Requirements

### Framework
- **Anchor ≥ 0.30** — mandatory. Raw Solana programs will not be accepted.
- **Rust stable**
- Full `anchor test` coverage required

### Vault Architecture

Each commodity cycle is modelled as a state machine:

```
OPEN → SUBSCRIBED → ACTIVE → T1_APPROVED → T2_APPROVED → T3_APPROVED → EXPORT_CONFIRMED → SETTLED → CLOSED
```

**Key accounts:**

```rust
pub struct ExportVault {
    pub vault_id: [u8; 32],
    pub commodity_type: CommodityType,    // AnimalFeed | LiveAnimals | HalalMeat
    pub plot_id: [u8; 32],
    pub spv_authority: Pubkey,            // PODRWA SPV Ltd KSA signing key
    pub oracle_program: Pubkey,
    pub total_subscribed_usd_cents: u64,  // Fiat subscription total (no USDC held on-chain)
    pub vault_state: VaultState,
    pub season_start: i64,
    pub estimated_harvest: i64,
    pub t1_approved_at: i64,
    pub t2_approved_at: i64,
    pub t3_approved_at: i64,
    pub export_confirmed_at: i64,
    pub bump: u8,
}

pub struct OracleRecord {
    pub plot_id: [u8; 32],
    pub verification_type: VerificationType,
    pub status: VerificationStatus,
    pub confidence: f32,
    pub contract_farming_status: ContractFarmingStatus,
    pub timestamp: i64,
}

pub struct DisbursementLog {
    pub vault_id: [u8; 32],
    pub tranche: TrancheIndex,            // T1 | T2 | T3 | T4
    pub disbursement_hash: [u8; 32],      // Hash of off-chain fiat wire record
    pub approved_by: Pubkey,             // SPV authority
    pub approved_at: i64,
}
```

### Tranche Approval Logic

`approve_tranche` reads the Oracle PDA and advances vault state. It does **not** move tokens — it emits an on-chain event that the SPV ops dashboard monitors to execute a fiat bank wire.

```rust
pub fn approve_tranche(
    ctx: Context<ApproveT ranche>,
    tranche: TrancheIndex,
    disbursement_hash: [u8; 32],  // Hash of the fiat wire instruction prepared off-chain
) -> Result<()> {
    let oracle_record = &ctx.accounts.oracle_record;

    // 1. Verify Oracle confirmation
    require!(
        oracle_record.status == VerificationStatus::Confirmed,
        ErrorCode::OracleUnconfirmed
    );

    // 2. Check confidence threshold
    require!(
        oracle_record.confidence >= 0.85,
        ErrorCode::ConfidenceBelowThreshold
    );

    // 3. Verify Contract Farming compliance (T1 only — subsequent tranches inherit)
    if tranche == TrancheIndex::T1 {
        require!(
            oracle_record.contract_farming_status == ContractFarmingStatus::Registered,
            ErrorCode::ComplianceNotRegistered
        );
    }

    // 4. Advance vault state + log disbursement hash (no token transfer)
    // SPV ops executes fiat wire off-chain; hash is the on-chain audit record
}
```

### SPV Subscription Interface

The vault integrates with `programs/spv-bridge/` (`issue_receipt_tokens`) to:
- Record investor subscription when SPV confirms fiat receipt
- Record the financier position (plain on-chain record; no token by default)
- Track total vault capacity vs subscriptions

### Financing Records (formerly $PODRWA token)

- No token is minted by default — financing positions are plain on-chain records
- Records represent the financier's cycle position for settlement tracking
- Closed on `settle_investor_position` when SPV confirms proceeds distributed

---

## Vault Types to Implement (MVP)

| Vault Type | Commodity | Payment Gate | Settlement Currency |
|---|---|---|---|
| Animal feed crop vault | Sorghum, maize | SAR plowing confirmation + NDVI growth curve | SAR/USD via SPV |
| Animal acquisition vault | Live cattle, sheep, goats | Delivery GPS + BCS score ≥ 2.5 | SAR/USD via SPV |
| Halal carcass meat vault | Beef, mutton (export-certified) | Export customs clearance doc upload | SAR/USD via SPV |

---

## Security Requirements

- Full `anchor test` suite with 100% instruction coverage
- All payment paths tested with both positive and negative Oracle PDA states
- Re-entrancy protection on all release instructions
- Authority checks on all admin instructions (SPV authority, Oracle program, core team multi-sig)
- **Mandatory third-party audit before TVL > $100k.** Do not request mainnet deployment without explicit core team sign-off.
- No hardcoded keys — all authority accounts via Anchor account constraints

---

## Evaluation Criteria

| Criterion | Weight |
|---|---|
| Oracle gate implementation correctness | 35% |
| SPV bridge interface compatibility | 20% |
| Test coverage and edge case handling | 25% |
| Code quality, documentation, upgrade-ability | 20% |

---

## Deliverables

- Working Anchor programs for all three MVP vault types
- Full `anchor test` suite (100% instruction coverage)
- Program IDL files (auto-generated by Anchor)
- Integration spec for `oracle/api/` Oracle PDA writer
- Integration spec for `programs/spv-bridge/` SPV receipt token issuance
- Deployment guide for devnet (mainnet pending audit)
- `README.md` per vault program

---

## Submission

1. Comment on [Issue #3](https://github.com/proofofdirt/pod/issues) to claim
2. Discuss architecture in Discord `#anchor-contracts` before writing significant code
3. Fork `proofofdirt/pod`, build in `programs/pod-vault/`
4. Submit PR with test results and your **Solana wallet address**
5. Core team will arrange third-party audit for mainnet deployment

---

## Reward Distribution

- **USDC (or SOL)** transferred directly to your Solana wallet upon PR merge — the transaction signature is the payment record
- Long-term core contributors may receive continued grant-funded engagement (the project does not issue a token)

---

*Questions: Discord `#anchor-contracts` or comment on Issue #3*  
*© 2026 Proof of Dirt Ecosystem · MIT License*
