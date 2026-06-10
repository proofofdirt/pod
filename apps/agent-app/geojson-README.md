# apps/agent-app/geojson — Plot Boundary Collection

Mobile GPS polygon capture interface for Turmi field agents.

## Key Behaviours

- Interactive map polygon drawing (react-native-maps)
- **Minimum area validation: plots ≥ 1 ha** — financing minimums per farm are an economics setting decided by the DAO per stage (agent + infrastructure cost), not a tech limit
- **GPS accuracy gate: flag submissions with accuracy > 5 metres**
- Cooperative aggregate display: running total of member plots vs the current financing minimum
- Full offline capture and storage (sync to Oracle API on reconnection)

## Output Format

Matches the schema in `oracle/api/geojson/` — all submissions validated against the same GeoJSON schema before Oracle API sync.
