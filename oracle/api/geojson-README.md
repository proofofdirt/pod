# oracle/api/geojson — Plot Boundary Tools

GeoJSON validation, spatial operations, and cross-validation tools for field agent-submitted plot boundaries.

## Core Scripts

### `validation.py`
- GeoJSON schema validation (RFC 7946)
- **Minimum area check: polygons must be ≥ 1 ha**
- GPS accuracy flag: submissions with accuracy > 5m are flagged for re-collection
- Cooperative aggregate validation: sum of member plots must reach the current financing minimum (set by the DAO per stage) before vault activation

### `spatial_ops.py`
- Polygon buffering, intersection, and union operations
- Cooperative member plot aggregation (individual plots → cooperative total)
- Plot overlap detection (prevent double-registration)

### `agent_verify.py`
- Cross-validates agent-submitted polygon against satellite footprint
- Confirms the submitted coordinates fall within the SAR/NDVI coverage area
- Flags geometric inconsistencies between claimed activity location and satellite signal

## Data Format

```json
{
  "type": "Feature",
  "properties": {
    "plot_id": "POD-ETH-0042",
    "cooperative_id": "COOP-OMO-007",
    "area_ha": 143.2,
    "woreda": "Salamago",
    "zone": "South Omo",
    "region": "SNNP",
    "land_rights_verified": true,
    "contract_farming_status": "REGISTERED"
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

## Key Constraints

- Minimum validated area: **1 ha** (tech floor)
- Cooperative member plots aggregate toward the current financing minimum
- All coordinates: WGS84 (EPSG:4326)
- All areas calculated using an equal-area projection for accuracy
