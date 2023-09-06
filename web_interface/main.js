var vectorLayers = [];
var map; // Declare map as a global variable
var minAttributeValue = Infinity;
var maxAttributeValue = -Infinity;

// Fetch shapefile data from the Flask app
fetch('/get_shapefiles')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    console.log('Fetched data:', data); // Debug log to check what's returned
    let allFeatures = [];
    
    for (const [key, value] of Object.entries(data)) {
      const features = new ol.format.GeoJSON().readFeatures(value, {
        dataProjection: 'EPSG:3857',
        featureProjection: 'EPSG:3857',
      });
      
      allFeatures = allFeatures.concat(features);
      
      const vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
          features: features,
        }),
        style: createStyleFunction(attributeName),
      });

      vectorLayers.push(vectorLayer);
    }

    // Calculate min and max
    minAttributeValue = Math.min(...allFeatures.map(f => f.get(attributeName) || Infinity));
    maxAttributeValue = Math.max(...allFeatures.map(f => f.get(attributeName) || -Infinity));
    
    initMap();
      
    // Update the legend after layers have been processed
    updateLegend(data);
  })
  .catch(error => {
    console.log('Fetch Error:', error);
  });

function createStyleFunction(attributeName) {
  return function(feature) {
    const geometryType = feature.getGeometry().getType();
    const attributeValue = feature.get(attributeName);

    // Always style Point and MultiPoint as filled circles
    if (geometryType === 'Point' || geometryType === 'MultiPoint') {
      return new ol.style.Style({
        image: new ol.style.Circle({
          radius: 3,
          fill: new ol.style.Fill({
            color: 'blue',
          }),
        }),
        zIndex: 10 // Higher zIndex so points appear above polygons
      });
    }

    if (attributeValue === null || attributeValue === undefined) {
      return null;  // Skip features with undefined or null values
    }

    // Generate a color based on the attribute value
    if (!isNaN(minAttributeValue) && !isNaN(maxAttributeValue)) {
      const component = Math.floor(255 - (255 * (attributeValue - minAttributeValue) / (maxAttributeValue - minAttributeValue)));
      const fillColor = `rgb(255, ${component}, ${component})`;

      if (geometryType === 'Polygon' || geometryType === 'MultiPolygon') {
        return new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: 'black',
            width: 2,
          }),
          fill: new ol.style.Fill({
            color: fillColor,
          }),
          zIndex: 1 // Lower zIndex so polygons appear below points
        });
      }
    }

    // For any other geometry type, use default styling
    return null;
  };
}

function isPolygonLayer(layer) {
  const source = layer.getSource();
  let features = source.getFeatures();
  if (features.length === 0) return false;  // Empty layer
  
  // Check the first feature as a sample to determine the type of layer.
  // This assumes that all features in the layer have the same geometry type.
  const geometryType = features[0].getGeometry().getType();
  return geometryType === 'Polygon' || geometryType === 'MultiPolygon';
}

function isPointLayer(layer) {
  const source = layer.getSource();
  let features = source.getFeatures();
  if (features.length === 0) return false;  // Empty layer

  // Check the first feature as a sample to determine the type of layer.
  // This assumes that all features in the layer have the same geometry type.
  const geometryType = features[0].getGeometry().getType();
  return geometryType === 'Point' || geometryType === 'MultiPoint';
}


const attributeName = 'Cents_kWh';
function initMap() {
  map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM(),
      }),
      ...vectorLayers.filter(layer => isPolygonLayer(layer)),  // Add polygon layers first
      ...vectorLayers.filter(layer => isPointLayer(layer))    // Add point layers last
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([0, 0]),
      zoom: 2,
    }),
  });
}

function updateLegend(data) {
  const legendDiv = document.getElementById("legend");
  legendDiv.style.display = "flex";
  legendDiv.style.flexDirection = "column";

  // Clear existing legend entries
  while (legendDiv.firstChild) {
    legendDiv.removeChild(legendDiv.firstChild);
  }

  // Add and style Legend header
  const header = document.createElement('h3');
  header.appendChild(document.createTextNode('Legend'));
  header.style.fontWeight = "bold";
  legendDiv.appendChild(header);

  let maxWidth = 0;

  Object.keys(data).forEach((key, index) => {
    const layerDiv = document.createElement("div");
    layerDiv.style.display = "flex";
    layerDiv.style.alignItems = "center";

    // Container for symbol or gradient, and min/max labels
    const symbolContainer = document.createElement("div");
    symbolContainer.style.display = "flex";
    symbolContainer.style.alignItems = "center";
    symbolContainer.style.width = "120px";  // fixed width

    // Add gradient or symbol
    const canvas = document.createElement("canvas");
    canvas.width = 50;
    canvas.height = 10;
    const ctx = canvas.getContext("2d");

    if (isPolygonLayer(vectorLayers[index])) {
      const minDiv = document.createElement("div");
      minDiv.innerText = minAttributeValue;
      minDiv.style.marginRight = "5px";
      symbolContainer.appendChild(minDiv);

      const gradient = ctx.createLinearGradient(0, 0, 50, 0);
      gradient.addColorStop(0, "rgb(255, 255, 255)");
      gradient.addColorStop(1, `rgb(255, 0, 0)`);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 50, 10);
      symbolContainer.appendChild(canvas);

      const maxDiv = document.createElement("div");
      maxDiv.innerText = maxAttributeValue;
      maxDiv.style.marginLeft = "5px";
      symbolContainer.appendChild(maxDiv);
    } else {
      // Align the point symbol to the center
      symbolContainer.style.justifyContent = "center";

      // Point symbol
      ctx.fillStyle = "blue";
      ctx.beginPath();
      ctx.arc(25, 5, 3, 0, Math.PI * 2);
      ctx.fill();
      symbolContainer.appendChild(canvas);
    }

    layerDiv.appendChild(symbolContainer);

    // Add shapefile name
    const title = document.createElement("div");
    title.innerText = key.split(".")[0];
    title.style.marginLeft = "20px";

    layerDiv.appendChild(title);
    legendDiv.appendChild(layerDiv);
  });
}


// Update map size when the window is resized
window.addEventListener('resize', function() {
  map.updateSize();
});
