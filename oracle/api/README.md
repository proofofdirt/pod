# oracle/api — Oracle API → Solana PDAs

FastAPI server that bridges the Oracle processing pipeline to the Solana blockchain. Writes verified results to Oracle Program Derived Addresses (PDAs) that the `$PODRWA` Anchor escrow contracts read before authorising payments.

## Architecture

```
Oracle Pipeline (Python)
        ↓
FastAPI Oracle API
        ↓
Solana Oracle PDA (program-derived address)
        ↓
$PODRWA Anchor Escrow Contract reads PDA → releases or withholds payment
```

## Key Endpoints (to be implemented)

```
POST /verify/plowing          → triggers SAR verification for a plot + date window
POST /verify/ndvi             → triggers NDVI check for a plot
POST /verify/animal-bcs       → triggers BCS scoring for an agent photo
POST /verify/contract-farming → confirms contract farming registration status
GET  /status/{plot_id}        → returns current Oracle status for a plot
GET  /history/{plot_id}       → returns full verification history
```

## Solana PDA Schema

The Oracle PDA stores the minimal data required by the Anchor escrow contract:

```rust
pub struct OracleRecord {
    pub plot_id: [u8; 32],
    pub verification_type: VerificationType,
    pub status: VerificationStatus,   // CONFIRMED | UNCONFIRMED | PENDING
    pub confidence: f32,              // 0.0 – 1.0
    pub timestamp: i64,
    pub sentinel_scene_id: [u8; 64],  // nullable
    pub contract_farming_status: ContractFarmingStatus,
}
```

## Development

```bash
cd oracle/api
pip install -r requirements.txt
cp .env.example .env
# Configure Solana RPC endpoint and Oracle program ID in .env
uvicorn main:app --reload
```

## Environment Variables

```env
SOLANA_RPC_URL=https://api.devnet.solana.com
ORACLE_PROGRAM_ID=<program_id>
ORACLE_AUTHORITY_KEYPAIR=<path_to_keypair>
GEE_SERVICE_ACCOUNT=<service_account_email>
GEE_KEY_FILE=<path_to_key_file>
```
