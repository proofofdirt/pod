// 1. Define Area of Interest (AOI) and Timeframe
var aoi = ee.Geometry.Polygon([[[ -8.5, 40.5], [ -8.5, 40.6], [ -8.4, 40.6], [ -8.4, 40.5]]]);
var preDate = '2026-03-01';
var postDate = '2026-04-15';

// 2. Fetch Sentinel-2 Optical Imagery to confirm Bare Soil/Residue
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate(preDate, postDate)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15));

var calculateNDVI = function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
};
var ndviCollection = s2.map(calculateNDVI);
var minNDVI = ndviCollection.select('NDVI').min(); // Look for structural bare valleys

// 3. Fetch Sentinel-1 SAR imagery (Ascending & Descending tracks)
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filterDate(preDate, postDate)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'));

// Split into pre-tillage and post-tillage time windows to detect the leap
var s1_Pre = s1.filterDate('2026-03-01', '2026-03-20').median();
var s1_Post = s1.filterDate('2026-03-21', '2026-04-15').median();

// 4. Compute Plowing/Tillage Index via Diffuse Backscatter Change (VH band)
var vhChange = s1_Post.select('VH').subtract(s1_Pre.select('VH')).rename('VH_Delta');

// 5. Hybrid Rule-Based Classification
// Condition: Significant spike in soil roughness (VH) AND low NDVI (bare ground)
var tillageMask = vhChange.gt(2.5).and(minNDVI.lt(0.3));

Map.centerObject(aoi, 13);
Map.addLayer(vhChange, {min: -5, max: 5, palette: ['blue', 'white', 'red']}, 'SAR VH Delta');
Map.addLayer(tillageMask.updateMask(tillageMask), {palette: ['orange']}, 'Detected Tilled Fields');