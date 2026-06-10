# pod-vault (Anchor program)

On-chain verification and audit layer (V1: no funds move on-chain):
- record_subscription / record_facility (fiat amounts, authority-gated) -> on-chain financing records (no tokens)
- approve_tranche(disbursement_hash) -> event watched by SPV/FI ops; fiat wire executed off-chain
- oracle milestone PDAs; cycle state machine; immutable disbursement log
Spec: bounties/ESCROW-003.md (fiat/SPV constraints inside).
