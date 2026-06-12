# oracle/api/contract-farming — Ethiopian Proclamation 578/2008 Compliance

Digital infrastructure supporting Ethiopia's Contract Farming Proclamation No. 578/2008. This module is mandatory — vault activation is blocked until a valid, registered contract is confirmed on-chain.

**Legal constraint:** All contract templates must be validated by Turmi Technologies' Ethiopian legal counsel before merging to `main`. Do not open template PRs without prior coordination via [email protected].

## What Gets Built Here

- **Contract templates:** Machine-readable JSON schemas + PDF templates in English, Amharic, and Oromifa
- **OCR validation:** Land use rights certificate photo capture and text extraction
- **Registry anchoring:** IPFS hash anchoring of signed contracts to Solana Oracle PDAs
- **Woreda registration:** Digital generation of Woreda registration packages + confirmation receipt capture

## Key Files (to be built under BOUNTY-004)

```
templates/
├── contract_eth_578_2008_en.json      # Machine-readable schema (English)
├── contract_eth_578_2008_am.json      # Amharic translation
└── contract_eth_578_2008_or.json      # Oromifa translation

validation/
└── land_rights_ocr.py                 # OCR pipeline for land use certificate photos

registry/
└── anchor_ipfs_bridge.py              # Anchor IPFS hash → Solana Oracle PDA

docs/
└── proclamation-578-2008-checklist.md # Legal compliance checklist
```

## Compliance Requirements

Every funded plot must have on record, before vault payment authorises:
- Digitally signed contract (biometric or OTP) — IPFS hash anchored on Solana
- Land use rights document (photographed, OCR-extracted, encrypted at rest)
- Woreda registration package generated and confirmation receipt captured
- Input delivery receipt: GPS + timestamp + photo at point of delivery

## Localisation

All contract templates and compliance UI must be available in:
- **English** (en)
- **Amharic** (am) — Ethiopia's official working language
- **Oromifa / Afaan Oromoo** (or) — primary language of the UKE Welega pilot region (West Ethiopia)

Translations must be reviewed by a native speaker with legal background before merge.
