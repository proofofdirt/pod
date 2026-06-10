# apps/agent-app/animal — Livestock Condition Scoring

On-device animal body condition scoring for field agents monitoring livestock in $PODRWA husbandry vaults.

## Features

- Guided photo capture workflow with lateral-view overlay guide
- Geotagged JPEG capture: GPS + timestamp + agent ID in metadata
- On-device BCS inference using ONNX Runtime or TFLite model (from `oracle/satellite/bcs/` BOUNTY-005)
- Preliminary BCS score displayed to agent before upload
- One-tap welfare concern flag → escalates to Turmi vet coordinator

## ML Model Integration

Integrates the ONNX/TFLite output of BOUNTY-005. Coordinate with the BCS-005 claimant on the model file format and inference interface.

Target inference: ≤ 2 seconds on mid-range Android (e.g., Samsung Galaxy A-series).
