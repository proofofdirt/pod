/**
 * POD Oracle — Sentinel-1 SAR Plow Detection
 * Desafarm Plots, Omo Valley, Ethiopia
 *
 * GEE Collection: COPERNICUS/S1_GRD
 * Method: VV + VH pre/post log-ratio change detection
 * Output: delta-dB stats per plot + oracle confidence score
 *
 * Usage: Paste into code.earthengine.google.com
 *        Set CLAIMED_DATE and PLOT_ID below, then Run.
 */

// ── 1. Config — edit these per oracle query ──────────────────────────────────

var CLAIMED_DATE = '2026-04-10';   // claimed plowing date (YYYY-MM-DD)
var PLOT_ID      = 'ETH-001';      // plot to verify (ETH-001 through ETH-008)

// Pre-event window: T-14 to T-3 days before claimed date
// Post-event window: T+1 to T+10 days after claimed date
// Sentinel-1 12-day repeat — windows sized to guarantee ≥1 pass each
var PRE_DAYS_START  = -14;
var PRE_DAYS_END    =  -3;
var POST_DAYS_START =   1;
var POST_DAYS_END   =  10;

// Confidence thresholds (tuned to 100 ha+ scale ground truth)
var CONFIRM_THRESHOLD   = -3.0;   // mean delta-dB < this → CONFIRMED
var UNCERTAIN_THRESHOLD = -1.5;   // mean delta-dB between thresholds → UNCERTAIN


// ── 2. Plot Geometries ───────────────────────────────────────────────────────

var plotDict = {
  'ETH-001': ee.Geometry.Polygon([[
    [36.50974, 9.37088], [36.50476, 9.37359], [36.50673, 9.37483],
    [36.51250, 9.36443], [36.50974, 9.37088]
  ]]),
  'ETH-002': ee.Geometry.Polygon([[
    [36.50677, 9.37499], [36.50470, 9.37360], [36.50171, 9.37701],
    [36.50425, 9.38003], [36.50677, 9.37499]
  ]]),
  'ETH-003': ee.Geometry.Polygon([[
    [36.50390, 9.38015], [36.50164, 9.37700], [36.49881, 9.38012],
    [36.50106, 9.38285], [36.50390, 9.38015]
  ]]),
  'ETH-004': ee.Geometry.Polygon([[
    [36.51120, 9.36956], [36.50475, 9.37332], [36.50219, 9.37112],
    [36.50556, 9.36782], [36.51046, 9.36003], [36.51120, 9.36956]
  ]]),
  'ETH-005': ee.Geometry.Polygon([[
    [36.51018, 9.36863], [36.51448, 9.36984], [36.51495, 9.36658],
    [36.51250, 9.36443], [36.51018, 9.36863]
  ]]),
  'ETH-006': ee.Geometry.Polygon([[
    [36.52118, 9.36980], [36.50795, 9.36811], [36.50566, 9.36774],
    [36.50665, 9.36569], [36.50618, 9.36495], [36.50982, 9.36083],
    [36.52118, 9.36980]
  ]]),
  'ETH-007': ee.Geometry.Polygon([[
    [36.50591, 9.36703], [36.50665, 9.36554], [36.50236, 9.36198],
    [36.50002, 9.36561], [36.50591, 9.36703]
  ]]),
  'ETH-008': ee.Geometry.Polygon([[
    [36.50259, 9.36178], [36.50608, 9.36441], [36.50981, 9.36076],
    [36.50895, 9.35887], [36.50752, 9.35854], [36.50259, 9.36178]
  ]])
};

var aoi = plotDict[PLOT_ID];
if (!aoi) { throw new Error('Unknown PLOT_ID: ' + PLOT_ID); }


// ── 3. Date Windows ──────────────────────────────────────────────────────────

var t0      = ee.Date(CLAIMED_DATE);
var preStart  = t0.advance(PRE_DAYS_START,  'day');
var preEnd    = t0.advance(PRE_DAYS_END,    'day');
var postStart = t0.advance(POST_DAYS_START, 'day');
var postEnd   = t0.advance(POST_DAYS_END,   'day');

print('Pre-event window:',  preStart.format('YYYY-MM-dd'), '→', preEnd.format('YYYY-MM-dd'));
print('Post-event window:', postStart.format('YYYY-MM-dd'), '→', postEnd.format('YYYY-MM-dd'));


// ── 4. Load Sentinel-1 GRD ───────────────────────────────────────────────────

var s1Base = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))   // consistent geometry
  .select(['VV', 'VH']);

var preColl  = s1Base.filterDate(preStart,  preEnd);
var postColl = s1Base.filterDate(postStart, postEnd);

print('Pre-event scenes:',  preColl.size());
print('Post-event scenes:', postColl.size());

// Warn if no scenes
preColl.size().evaluate(function(n) {
  if (n === 0) print('⚠ WARNING: No pre-event S1 scenes found. Widen PRE window or check orbit coverage.');
});
postColl.size().evaluate(function(n) {
  if (n === 0) print('⚠ WARNING: No post-event S1 scenes found. Widen POST window or check orbit coverage.');
});


// ── 5. Median Composites ─────────────────────────────────────────────────────

var preComposite  = preColl.median();
var postComposite = postColl.median();


// ── 6. Delta-dB Change Detection ─────────────────────────────────────────────
// S1 GRD bands are already in dB (10*log10 sigma0) in GEE
// ΔdB = post_dB - pre_dB  (positive = backscatter increase = plowing signal)
// Plowing roughens soil → typically −3 to −6 dB drop in VV (surface becomes less specular)
// NOTE: sign convention here: negative delta = backscatter decreased = plowing likely

var deltaVV = postComposite.select('VV').subtract(preComposite.select('VV')).rename('delta_VV');
var deltaVH = postComposite.select('VH').subtract(preComposite.select('VH')).rename('delta_VH');
var deltaVVVH = deltaVV.subtract(deltaVH).rename('delta_VVVH_ratio');

var deltaImage = deltaVV.addBands(deltaVH).addBands(deltaVVVH);


// ── 7. Polygon Statistics ────────────────────────────────────────────────────

var stats = deltaImage.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine(ee.Reducer.stdDev(), null, true)
    .combine(ee.Reducer.percentile([10, 25, 75, 90]), null, true),
  geometry: aoi,
  scale: 10,
  maxPixels: 1e9
});

print('Delta-dB statistics for ' + PLOT_ID + ':', stats);


// ── 8. Rule-Based Confidence Score ──────────────────────────────────────────
// Pre-model heuristic; replace with trained classifier weights once ground truth available

var meanDeltaVV = ee.Number(stats.get('delta_VV_mean'));
var stdDeltaVV  = ee.Number(stats.get('delta_VV_stdDev'));

// Confidence: sigmoid-like mapping from delta_VV_mean
// More negative mean → higher confidence of plowing
var rawScore = meanDeltaVV.multiply(-1).divide(6.0).min(1.0).max(0.0);
// Penalise high variance (could be noise rather than real change)
var variancePenalty = stdDeltaVV.divide(10.0).min(0.2);
var confidence = rawScore.subtract(variancePenalty).max(0.0);

var status = ee.Algorithms.If(
  meanDeltaVV.lt(CONFIRM_THRESHOLD),
  'CONFIRMED',
  ee.Algorithms.If(meanDeltaVV.lt(UNCERTAIN_THRESHOLD), 'UNCERTAIN', 'UNCONFIRMED')
);

print('--- Oracle Result ---');
print('Status:',     status);
print('Confidence:', confidence);
print('SAR delta_VV_mean (dB):', meanDeltaVV);


// ── 9. Map Visualisation ─────────────────────────────────────────────────────

Map.centerObject(aoi, 14);

var deltaVis = { min: -6, max: 6, palette: ['#d73027','#f46d43','#ffffbf','#74add1','#313695'] };
Map.addLayer(preComposite.select('VV').clip(aoi),  {min: -25, max: 0, palette: ['black','white']}, 'Pre VV');
Map.addLayer(postComposite.select('VV').clip(aoi), {min: -25, max: 0, palette: ['black','white']}, 'Post VV');
Map.addLayer(deltaVV.clip(aoi), deltaVis, 'ΔdB VV (post−pre)');
Map.addLayer(ee.FeatureCollection([ee.Feature(aoi, {plot_id: PLOT_ID})]), {color: 'orange'}, PLOT_ID);


// ── 10. Export Delta-dB Raster to Drive ──────────────────────────────────────

Export.image.toDrive({
  image: deltaImage.clip(aoi),
  description: 'SAR_delta_dB_' + PLOT_ID + '_' + CLAIMED_DATE,
  scale: 10,
  region: aoi,
  fileFormat: 'GeoTIFF',
  maxPixels: 1e9
});

print('✅ Script complete. Check Tasks tab to export delta-dB GeoTIFF.');
