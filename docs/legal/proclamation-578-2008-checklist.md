# Ethiopian Contract Farming Proclamation 578/2008 — Compliance Checklist

> **Reference only — not legal advice.** All contract templates must be validated by Turmi Technologies' Ethiopian legal counsel before use. Contact [email protected].

This checklist covers the minimum compliance requirements for every plot funded via $PODRWA vaults under the Proof of Dirt protocol. Vault activation on Solana is blocked until all mandatory items are confirmed on-chain.

---

## Pre-Activation Checklist (Oracle Status: REGISTERED required)

### 1. Landholding Verification
- [ ] Land use certificate (Kebele-issued) obtained and photographed
- [ ] Certificate matches the plot GeoJSON polygon (location cross-validation)
- [ ] Land rights holder confirmed as party to the contract (or cooperative representative)
- [ ] No overlapping land claims on the plot GeoJSON polygon

### 2. Contract Farming Agreement
- [ ] Written contract generated from validated Proclamation 578/2008 template
- [ ] Contract contains: crop/commodity type, quantity targets, delivery schedule, payment terms, input delivery obligations
- [ ] Both parties (farmer/cooperative + Turmi as contractor) have signed
- [ ] Digital signature captured: biometric or OTP-verified (Agent App)
- [ ] IPFS hash of signed PDF anchored to Solana Oracle PDA

### 3. Woreda Registration
- [ ] Contract submitted to relevant Woreda Agriculture Office
- [ ] Woreda registration reference number issued
- [ ] Confirmation receipt scanned and stored in Agent App

### 4. Cooperative Requirements (where applicable)
- [ ] Cooperative is formally registered under Ethiopian law
- [ ] Cooperative has designated authorised representative (with ID verification)
- [ ] Aggregate member plot area meets the current financing minimum (set by the DAO per stage) — confirmed via GeoJSON validation

---

## Ongoing Compliance (per vault payment cycle)

### Input Delivery
- [ ] GPS coordinates captured at delivery location
- [ ] Photo of delivered inputs (seed bags, fertiliser containers, equipment)
- [ ] Timestamp within the contracted delivery window
- [ ] Agent signature on delivery receipt

### Activity Confirmation
- [ ] Plowing event: Oracle SAR confirmation (confidence ≥ 0.85) OR manual agent photo if SAR inconclusive
- [ ] Planting: NDVI onset confirmed or agent photo of germinated seedlings
- [ ] Animal delivery: GPS + photo + BCS score ≥ 2.5 (livestock vaults)

### Export Compliance
- [ ] Ethiopian export license valid (animal feed, live animals, or carcass meat as applicable)
- [ ] Phytosanitary certificate / veterinary health certificate issued
- [ ] Customs clearance document uploaded to Oracle API before final vault settlement

---

## Key Legal References

- **Proclamation No. 578/2008** — Contract Farming Proclamation of Ethiopia
- **Proclamation No. 456/2005** — Federal Rural Land Administration and Land Use Proclamation
- **Export Trade Duty Incentive Schemes Proclamation** — Ethiopian export license framework
- **Livestock and Livestock Products Marketing Authority (LLPMA)** — live animal and meat export regulations

All legal references are for contributor context only. Ethiopian legal counsel must validate all templates and workflows before production use.

---

*Contact: [email protected] for legal questions*  
*Last reviewed: 2026 · Proof of Dirt Ecosystem*
