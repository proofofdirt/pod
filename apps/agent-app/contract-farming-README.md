# apps/agent-app/contract-farming — Proclamation 578/2008 Compliance Module

Mobile implementation of the Ethiopian Contract Farming Compliance Module. This is a mandatory feature — vault activation on Solana is blocked until a valid registered contract is confirmed on-chain.

See `oracle/api/contract-farming/` for the backend (templates, OCR, registry anchoring) that this module integrates with.

## Workflows

- Contract PDF generation on-device from template JSON schemas
- Digital signature capture (biometric fingerprint or OTP)
- Land rights document photo capture (encrypted local storage)
- Woreda registration package generation and confirmation receipt capture
- Input delivery receipt with GPS + photo + checklist

## Legal Constraint

Contract templates must be validated by Turmi's Ethiopian legal counsel. Do not modify templates without coordination via [email protected].
