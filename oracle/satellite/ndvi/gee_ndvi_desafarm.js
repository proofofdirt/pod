/**
 * POD Oracle — Sentinel-2 NDVI Time-Series
 * Desafarm Plots, Omo Valley, Ethiopia
 *
 * GEE Collection: COPERNICUS/S2_SR_HARMONIZED
 * Cloud masking: SCL band (Scene Classification Layer)
 * Output: NDVI time-series chart + CSV export to Drive
 *
 * Usage: Paste into code.earthengine.google.com and click Run.
 *        To export CSV, click "Run" in the Tasks tab after the script completes.
 */

// ── 1. Plot Geometries (from pod-agents/shared-memory/plots/desafarm-all-plots.geojson) ──

var plots = ee.FeatureCollection([
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.50974, 9.37088], [36.50476, 9.37359], [36.50673, 9.37483],
      [36.51250, 9.36443], [36.50974, 9.37088]
    ]]),
    { plot_id: 'ETH-001', name: 'plot 116A under Road' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.50677, 9.37499], [36.50470, 9.37360], [36.50171, 9.37701],
      [36.50425, 9.38003], [36.50677, 9.37499]
    ]]),
    { plot_id: 'ETH-002', name: 'plot 115A' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.50390, 9.38015], [36.50164, 9.37700], [36.49881, 9.38012],
      [36.50106, 9.38285], [36.50390, 9.38015]
    ]]),
    { plot_id: 'ETH-003', name: 'plot 115B' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.51120, 9.36956], [36.50475, 9.37332], [36.50219, 9.37112],
      [36.50556, 9.36782], [36.51046, 9.36003], [36.51120, 9.36956]
    ]]),
    { plot_id: 'ETH-004', name: 'plot 116B' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.51018, 9.36863], [36.51448, 9.36984], [36.51495, 9.36658],
      [36.51250, 9.36443], [36.51018, 9.36863]
    ]]),
    { plot_id: 'ETH-005', name: 'plot 118' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.52118, 9.36980], [36.50795, 9.36811], [36.50566, 9.36774],
      [36.50665, 9.36569], [36.50618, 9.36495], [36.50982, 9.36083],
      [36.52118, 9.36980]
    ]]),
    { plot_id: 'ETH-006', name: 'plot 117' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.50591, 9.36703], [36.50665, 9.36554], [36.50236, 9.36198],
      [36.50002, 9.36561], [36.50591, 9.36703]
    ]]),
    { plot_id: 'ETH-007', name: 'plot 102A' }
  ),
  ee.Feature(
    ee.Geometry.Polygon([[
      [36.50259, 9.36178], [36.50608, 9.36441], [36.50981, 9.36076],
      [36.50895, 9.35887], [36.50752, 9.35854], [36.50259, 9.36178]
    ]]),
    { plot_id: 'ETH-008', name: 'plot 101' }
  )
]);

// Bounding box over all plots for filtering imagery
var aoi = plots.geometry().bounds();

// ── 2. Date Range ──
// Omo Valley main season: planting ~June, harvest ~November
// Adjust START_DATE / END_DATE per season being queried
var START_DATE = '2025-05-01';
var END_DATE   = '2025-12-31';

// ── 3. Cloud Masking via SCL Band ──
// SCL classes to mask: 0=No data, 1=Saturated, 3=Cloud shadow,
//                      8=Cloud medium prob, 9=Cloud high prob, 10=Cirrus
function maskS2clouds(image) {
  var scl = image.select('SCL');
  var cloudMask = scl.neq(0)
    .and(scl.neq(1))
    .and(scl.neq(3))
    .and(scl.neq(8))
    .and(scl.neq(9))
    .and(scl.neq(10));
  return image.updateMask(cloudMask)
    .divide(10000)                         // scale reflectance to [0,1]
    .copyProperties(image, ['system:time_start']);
}

// ── 4. Load Sentinel-2 Collection ──
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate(START_DATE, END_DATE)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60))  // pre-filter noisy scenes
  .map(maskS2clouds);

print('Scene count after cloud filter:', s2.size());

// ── 5. Compute NDVI ──
// NDVI = (B8_NIR - B4_Red) / (B8_NIR + B4_Red)
var withNDVI = s2.map(function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
});

// ── 6. Focus on ETH-001 (first real oracle query) ──
var eth001 = plots.filter(ee.Filter.eq('plot_id', 'ETH-001')).first().geometry();

// ── 7. Time-Series Chart — ETH-001 ──
var chart = ui.Chart.image.series({
  imageCollection: withNDVI.select('NDVI'),
  region: eth001,
  reducer: ee.Reducer.mean(),
  scale: 10,
  xProperty: 'system:time_start'
})
.setOptions({
  title: 'Sentinel-2 NDVI Time-Series — ETH-001 (plot 116A under Road)',
  vAxis: { title: 'Mean NDVI', minValue: 0, maxValue: 1 },
  hAxis: { title: 'Date', format: 'MMM yy' },
  lineWidth: 2,
  pointSize: 4,
  colors: ['#2e7d32'],
  series: { 0: { labelInLegend: 'NDVI (cloud-masked)' } }
});
print(chart);

// ── 8. Chart All Plots ──
var allPlotsChart = ui.Chart.image.seriesByRegion({
  imageCollection: withNDVI.select('NDVI'),
  regions: plots,
  reducer: ee.Reducer.mean(),
  band: 'NDVI',
  scale: 10,
  xProperty: 'system:time_start',
  seriesProperty: 'plot_id'
})
.setOptions({
  title: 'Sentinel-2 NDVI — All Desafarm Plots',
  vAxis: { title: 'Mean NDVI', minValue: 0, maxValue: 1 },
  hAxis: { title: 'Date', format: 'MMM yy' },
  lineWidth: 2,
  pointSize: 3
});
print(allPlotsChart);

// ── 9. Map Visualisation ──
Map.centerObject(aoi, 14);
Map.addLayer(plots, { color: 'orange' }, 'Desafarm Plots');

// Latest cloud-free NDVI composite (median)
var ndviComposite = withNDVI.select('NDVI').median();
var ndviVis = {
  min: 0, max: 0.9,
  palette: ['#d73027','#f46d43','#fdae61','#fee08b','#d9ef8b','#a6d96a','#66bd63','#1a9850']
};
Map.addLayer(ndviComposite.clip(aoi), ndviVis, 'NDVI Median Composite');

// ── 10. Export NDVI Time-Series to Drive (run from Tasks tab) ──
// Extracts mean NDVI per plot per image date → CSV
var ndviTimeSeries = withNDVI.select('NDVI').map(function(image) {
  var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
  var reduced = image.reduceRegions({
    collection: plots,
    reducer: ee.Reducer.mean().setOutputs(['ndvi_mean']),
    scale: 10
  });
  return reduced.map(function(f) {
    return f.set('date', date);
  });
}).flatten();

Export.table.toDrive({
  collection: ndviTimeSeries,
  description: 'desafarm_ndvi_timeseries_' + START_DATE.replace(/-/g,'') + '_' + END_DATE.replace(/-/g,''),
  fileFormat: 'CSV',
  selectors: ['plot_id', 'name', 'date', 'ndvi_mean']
});

print('✅ Script loaded. Check Tasks tab to run the CSV export.');
print('   Chart above shows NDVI time-series for ETH-001 and all plots.');
