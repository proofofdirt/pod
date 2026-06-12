# apps/agent-app — Field Agent Mobile App

> React Native offline-first app for Turmi Technologies field agents operating in Ethiopia's UKE Welega pilot region (Horo Guduru Welega Zone, West Ethiopia).

The Agent App is the human layer of the POD Oracle — the interface through which field agents submit GeoJSON plot boundaries, record agricultural activity, capture contract farming compliance documents, and score livestock body condition.

**Every Oracle verification begins here.** No data in = no satellite cross-validation = no payment.

---

## App Modules

```
apps/agent-app/
├── contract-farming/      # Ethiopian Proclamation 578/2008 compliance module (MANDATORY)
├── geojson/               # Plot boundary collection and GPS capture
├── animal/                # Livestock condition scoring + IoT tag integration
├── api/                   # Oracle API connector (online sync)
└── bounties/
    └── APP-004.md         # Active build bounty
```

---

## Core Requirements

### Offline-First Architecture
Field agents operate in areas with unreliable connectivity. **All workflows must complete without internet access.** Data is queued locally and synced to the Oracle API when connectivity returns.

Minimum offline capability:
- GeoJSON polygon capture and storage
- Contract farming document generation and digital signature capture
- Animal BCS photo capture and local ML inference
- Full activity log queue (syncs to Oracle API on reconnection)

### Languages
All UI and contract templates must be available in:
- **English** (en)
- **Amharic** (am) — Ethiopia's official working language
- **Oromifa / Afaan Oromoo** (or) — primary language of the UKE Welega pilot region (West Ethiopia)

### GPS Accuracy
- Flag all submissions where GPS accuracy is > 5 metres
- Prompt agent to re-capture in better conditions
- Minimum polygon area: 1 ha (plot-level trust tech; financing minimums set by the DAO per stage)

---

## Modules Detail

### `contract-farming/` — Procurement 578/2008 Compliance (MANDATORY)

This module is not optional. Ethiopian Proclamation No. 578/2008 compliance is a legal requirement — vault activation is blocked until a registered contract is confirmed on-chain.

Required deliverables:
- Digital contract PDF generation from legally-validated templates
- Digital signature capture (biometric or OTP)
- Land use rights document photo capture (encrypted storage)
- Woreda registration package generation + confirmation receipt capture
- Input delivery receipt: GPS + timestamp + photo at delivery point

### `geojson/` — Plot Boundary Collection

- GPS polygon capture via map interface
- Minimum area validation (1 ha tech floor)
- Cooperative member plot tagging + aggregate calculation
- Offline polygon storage and batch upload

### `animal/` — Livestock Condition Scoring

- Photo capture workflow for agent field photos
- On-device inference using BCS model from `oracle/satellite/bcs/` (ONNX/TFLite)
- Geotagged JPEG capture with agent ID and timestamp metadata
- IoT livestock tag scanning (NFC/Bluetooth integration — post-MVP)

### `api/` — Oracle API Connector

- Authenticated sync to `oracle/api/` endpoints
- Offline queue with retry logic
- Real-time sync status indicators

---

## Active Bounty

→ [BOUNTY-004: Agent App MVP + Contract Farming Module](./bounties/APP-004.md) — reward: USDC/SOL from the DAO treasury

---

## Tech Stack

- **Framework:** React Native (cross-platform iOS/Android)
- **Offline storage:** SQLite via `react-native-sqlite-storage` or WatermelonDB
- **Maps:** `react-native-maps` + GPS polygon capture
- **PDF generation:** React Native PDF library
- **On-device ML:** ONNX Runtime for React Native or TFLite
- **Signing:** react-native-biometrics or OTP via SMS

---

## Development

```bash
git clone https://github.com/proofofdirt/pod && cd pod/apps/agent-app
cd apps/agent-app
npm install
# iOS
npx pod-install && npx react-native run-ios
# Android
npx react-native run-android
```

---

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development standards and the PR checklist.

*© 2026 Proof of Dirt Ecosystem · MIT License*
