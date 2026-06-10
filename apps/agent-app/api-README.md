# apps/agent-app/api — Oracle API Connector

Authenticated sync layer connecting the Agent App to the POD Oracle API (`oracle/api/`).

## Responsibilities

- Authenticated HTTP client with JWT/API key auth
- Offline queue: all submissions stored locally first, synced when connectivity returns
- Retry logic with exponential backoff
- Conflict resolution for overlapping agent submissions
- Sync status indicators (queued / syncing / confirmed / error)

## Endpoints Consumed

```
POST /verify/plowing          ← plot GeoJSON + claimed plowing date
POST /verify/animal-bcs       ← geotagged BCS photo
POST /verify/contract-farming ← IPFS hash of signed contract
POST /geojson/submit          ← new plot boundary submission
POST /delivery/receipt        ← input delivery receipt (GPS + photo + checklist)
GET  /agent/{agent_id}/queue  ← outstanding actions for this agent
GET  /agent/{agent_id}/earnings ← verified earnings to date (ETB — paid by Turmi payroll)
```

## Queue Implementation

Use WatermelonDB or SQLite to persist the submission queue locally. Queue items have status: `pending | syncing | confirmed | failed`. Failed items retry with exponential backoff up to 5 attempts before surfacing an error to the agent.
