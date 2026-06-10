# NBE Compliance Checklist — Ethiopia

**Relevant authority:** National Bank of Ethiopia (NBE)  
**Key regulation:** NBE Directive FXD/68/2022 (Foreign Currency Accounts)  
**Status:** Review required before corridor launch

---

## Architectural Decision: No USDC in Ethiopia

Ethiopian law does not permit USDC or stablecoin transactions. This is resolved at the protocol architecture level:

- **All capital into Ethiopia flows as fiat** via a NBE-licensed commercial bank partner
- **PODRWA SPV KSA** holds hard currency offshore; wires fiat tranches to Ethiopian financial institution partner
- **Solana** serves as audit/trust layer only — Oracle PDAs, cycle state, disbursement hashes
- **No crypto wallet required from Turmi, subcontractors, or farmers**

This architecture eliminates the NBE/USDC classification risk entirely.

---

## Foreign Capital Deployment Checklist

- [x] **USDC/stablecoin issue resolved** — architectural decision: fiat-only flows into Ethiopia
- [ ] Foreign currency enters via NBE-licensed commercial bank (financial institution partner MOU required)
- [ ] Capital Structuring Agent routes all tranches via Turmi Tech's licensed financial partner
- [ ] Export proceeds repatriation window: confirm 28-day rule applies; structure offshore retention via KSA SPV
- [ ] Withholding tax on payments to foreign entities: confirm KSA-Ethiopia DTT status
- [ ] Ethiopian Investment Commission registration: required for PODRWA SPV KSA as foreign party involved in agricultural finance
- [ ] Agricultural land: foreign entities cannot hold title — confirmed Turmi Tech holds land use agreements; liens only

## Ethiopian Financial Institution Partner Requirements

The partner must be:
- NBE-licensed commercial bank or microfinance institution
- Capable of receiving USD/SAR wire from KSA and disbursing ETB to Turmi
- Willing to provide account statements for SPV audit trail
- Familiar with agricultural finance disbursements (MOU to define SLA and fee structure)

## Contract Farming

- Ethiopian Contract Farming Proclamation 578/2008 requires formal Woreda registration
- the agent app contract-farming module (`apps/agent-app/`) handles digital compliance + PDF generation
- Full checklist: `docs/legal/proclamation-578-2008-checklist.md`

## Actions Required

1. Commission legal opinion from Ethiopian counsel on fiat capital deployment structure
2. Identify and execute MOU with NBE-licensed financial institution partner
3. Confirm export proceeds repatriation window and offshore retention legality via KSA SPV
4. Obtain tax clearance certificate template for Turmi Tech
5. Ethiopian Investment Commission registration filing for PODRWA SPV KSA involvement
