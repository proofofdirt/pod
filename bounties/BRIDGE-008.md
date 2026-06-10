> ⚠️ **ON HOLD (June 2026):** The project does not issue tokens. Revisit this bounty only if on-chain recordkeeping of fiat transactions ever requires a non-transferable receipt instrument.

# BOUNTY-008 — SPV Subscription Receipt Bridge (SAR/USD → $PODRWA Token)

**Repository:** `proofofdirt/pod` → `programs/spv-bridge/` (ON HOLD)  
**Status:** 🟢 OPEN  
**Reward:** USDC or SOL, paid by direct transfer from the DAO treasury multisig (grant/donation-funded; amount published on the bounty issue)  
**Deadline:** 12 weeks from claim date  
**Claim:** Comment on [Issue #8](https://github.com/proofofdirt/pod/issues)

---

## Objective

Build the on-chain module that issues $PODRWA tokens to investors on Solana when PODRWA SPV Ltd (KSA) confirms a fiat subscription has been received. This is an **investor receipt layer**, not a payment mechanism into Ethiopia.

> **Architectural constraint:** Ethiopian law prohibits USDC/stablecoin transactions. Capital flows into Ethiopia via fiat bank wire only (PODRWA SPV → Ethiopian financial institution partner → Turmi). This module does not touch Ethiopian operations. Its sole function is to issue a verifiable on-chain record of an investor's fiat commitment to the SPV.

---

## Why This Matters

MENA institutional investors subscribe in SAR or USD via PODRWA SPV KSA. They need an on-chain record of their subscription for governance participation and cycle settlement tracking. The $PODRWA token is that record — a Solana-native receipt that the SPV controls minting of, tied to a verified fiat subscription event.

Investors need no crypto knowledge at entry. The SPV can custody tokens on their behalf. The token enables: governance voting, cycle settlement status tracking, and eventual decentralised settlement in later protocol phases.

---

## System Architecture

```
MENA Investor
    │  SAR or USD subscription (fiat, off-chain)
    ▼
PODRWA SPV Ltd (KSA)
    │  Fiat received in KSA bank account
    │  KYC/AML cleared
    │  SPV ops signs on-chain issuance instruction
    ▼
[THIS MODULE] — Solana on-chain
    │  Verifies SPV authority signature
    │  Records subscription hash (amount + date + KYC commitment — no PII)
    │  Mints $PODRWA tokens to investor wallet (or SPV custody wallet)
    ▼
$PODRWA vault state updated (ESCROW-003)
    │  Investor token balance reflects fiat subscription
    │  Cycle state machine updated: vault capacity filled
    ▼
On Solana: subscription hash, SPV attestation, investor token balance, cycle ID
```

---

## Technical Requirements

### On-Chain (Anchor / Rust)

**`issue_receipt_tokens` instruction:**

```rust
pub struct IssueReceiptTokens<'info> {
    #[account(mut)]
    pub vault: Account<'info, ExportVault>,

    #[account(
        constraint = spv_authority.key() == vault.spv_authority @ ErrorCode::UnauthorizedSpv
    )]
    pub spv_authority: Signer<'info>,

    pub podrwa_mint: Account<'info, Mint>,
    pub investor_token_account: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

pub fn issue_receipt_tokens(
    ctx: Context<IssueReceiptTokens>,
    fiat_amount_usd_cents: u64,       // USD equivalent of SAR/USD subscription
    spv_subscription_hash: [u8; 32], // Hash of off-chain subscription agreement
    investor_kyc_commitment: [u8; 32], // KYC hash — no PII on-chain
    cycle_id: [u8; 32],
) -> Result<()>
```

**`settle_investor_position` instruction:**
- Triggered by SPV when export proceeds are received from MENA buyer
- Burns $PODRWA tokens; emits settlement event on-chain
- Actual return payment (SAR/USD) executed off-chain via KSA banking
- Marks investor position SETTLED in vault state

**`revoke_on_kyc_failure` instruction:**
- SPV authority can burn tokens and void subscription if post-issuance KYC failure
- Logs revocation event on-chain for audit

### Off-Chain Integration (TypeScript SDK)

Build `@proofofdirt/spv-bridge-sdk` that:
- Constructs and signs `issue_receipt_tokens` from SPV authority wallet
- Queries investor token balance and cycle settlement status
- Integrates with pod-dashboard investor portal
- Provides subscription event feed for SPV back-office reporting

### Compliance Requirements

- KYC commitment hash computed off-chain by SPV's KYC provider — only hash stored on-chain
- SPV authority keypair HSM-managed — document key management approach in deliverables
- All on-chain events indexable for SPV's KSA regulatory reporting
- No raw PII on-chain at any point

---

## Security Requirements

- SPV authority signature verification on every issuance instruction
- No minting possible without SPV authority signature
- Revocation path fully tested
- No admin upgrade keys without time-lock
- Full `anchor test` coverage including revocation and settlement paths

---

## Evaluation Criteria

| Criterion | Weight |
|---|---|
| SPV authority verification correctness | 35% |
| KYC commitment compliance, event indexability | 25% |
| TypeScript SDK quality and dashboard integration | 20% |
| Test coverage (including revocation, settlement) | 15% |
| Documentation | 5% |

---

## Deliverables

- Anchor program: `spv-bridge` with `issue_receipt_tokens`, `settle_investor_position`, `revoke_on_kyc_failure`
- TypeScript SDK: `@proofofdirt/spv-bridge-sdk`
- Integration spec for ESCROW-003 vault state machine
- Integration spec for pod-dashboard investor portal
- `anchor test` suite with full instruction + error path coverage
- Deployment guide for devnet
- Architecture documentation

---

## Submission

1. Comment on [Issue #8](https://github.com/proofofdirt/pod/issues) to claim
2. Coordinate with ESCROW-003 claimant on vault state interface in Discord `#anchor-contracts`
3. Fork `proofofdirt/pod`, build in `programs/spv-bridge/` (only if reactivated)
4. Submit PR with your **Solana wallet address**

---

## Reward Distribution

- **USDC (or SOL)** transferred directly upon PR merge (if reactivated)
- Long-term core contributors may receive continued grant-funded engagement (the project does not issue a token)

---

*Questions: Discord `#anchor-contracts` or comment on Issue #8*  
*KSA SPV / compliance questions: [email protected]*  
*© 2026 Proof of Dirt Ecosystem · MIT License*
