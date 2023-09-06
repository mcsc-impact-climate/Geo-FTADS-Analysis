var vectorLayers = [];
var map;
var attributeBounds = {}; // Object to store min and max attribute values for each shapefile


const shapefileLabels = {
  'electricity_rates_by_state_merged': 'Electricity rate (cents/kWh)',
  'US_elec': 'DCFC Charging Stations',
  'highway_assignment_links_single_unit': 'Highway Freight Flows (annual tons/link)',
};

// Key: shapefile name, Value: boolean indicating whether to apply a gradient
const gradientFlags = {
  'electricity_rates_by_state_merged': true,
  'US_elec': false,
  'highway_assignment_links_single_unit': true,
};

const gradientAttributes = {
  'electricity_rates_by_state_merged': 'Cents_kWh',
  'highway_assignment_links_single_unit': 'Tot Tons',
};

// Key: shapefile name, Value: color to use
const shapefileColors = {
  'electricity_rates_by_state_merged': 'red',
  'US_elec': 'blue',
  'highway_assignment_links_single_unit': 'black',
};


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

        const attributeKey = key.split(".")[0];
        const attributeName = gradientAttributes[attributeKey];
        
        const minVal = Math.min(...features.map(f => f.get(attributeName) || Infinity));
        const maxVal = Math.max(...features.map(f => f.get(attributeName) || -Infinity));

        attributeBounds[key] = { min: minVal, max: maxVal };

        const vectorLayer = new ol.layer.Vector({
          source: new ol.source.Vector({
            features: features,
          }),
          style: createStyleFunction(gradientAttributes[key.split(".")[0]], key)
        });

        vectorLayers.push(vectorLayer);
      }
    
    initMap();
      
    // Update the legend after layers have been processed
    updateLegend(data);
  })
  .catch(error => {
    console.log('Fetch Error:', error);
  });

function createStyleFunction(attributeName, shapefileName) {
  return function(feature) {

    const attributeKey = shapefileName.split(".")[0];
    const attributeName = gradientAttributes[attributeKey];

    const bounds = attributeBounds[shapefileName]; // Get the bounds for this specific shapefile
    const attributeValue = feature.get(attributeName);
    
    const useGradient = gradientFlags[shapefileName.split(".")[0]];
    const layerColor = shapefileColors[attributeKey] || 'blue'; // Fetch color from dictionary, or default to blue

    const geometryType = feature.getGeometry().getType();

    if (useGradient && bounds && (geometryType === 'Polygon' || geometryType === 'MultiPolygon')) {
      const component = Math.floor(255 - (255 * (attributeValue - bounds.min) / (bounds.max - bounds.min)));
      const fillColor = `rgb(255, ${component}, ${component})`;
        
      return new ol.style.Style({
        stroke: new ol.style.Stroke({
          color: 'gray',
          width: 1,
        }),
        fill: new ol.style.Fill({
          color: fillColor,
        }),
        zIndex: 1 // Lower zIndex so polygons appear below points
      });
      
  }  else if (geometryType === 'LineString' || geometryType === 'MultiLineString') {
      if (useGradient && bounds) {  // Apply varying width only if gradientFlags is true and bounds are defined
        // Normalize within range 1 to 10
        const normalizedWidth = 1 + 9 * ((attributeValue - bounds.min) / (bounds.max - bounds.min));

        return new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: layerColor,
            width: normalizedWidth,
          }),
          zIndex: 5  // zIndex between points and polygons
        });
      } else {
        // Add default line styling here if you want
        return new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: layerColor,
            width: 1,
          }),
          zIndex: 5  // zIndex between points and polygons
        });
      }
       } else {
    return new ol.style.Style({
      image: new ol.style.Circle({
        radius: 3,
        fill: new ol.style.Fill({
          color: layerColor,  // use the color defined for this shapefile
        }),
      }),
      zIndex: 10 // Higher zIndex so points appear above polygons
    });
  }

    if (attributeValue === null || attributeValue === undefined) {
      return null;  // Skip features with undefined or null values
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

function isLineStringLayer(layer) {
  const source = layer.getSource();
  let features = source.getFeatures();
  if (features.length === 0) return false;

  const geometryType = features[0].getGeometry().getType();
  return geometryType === 'LineString' || geometryType === 'MultiLineString';
}

function initMap() {
  map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.OSM(),
      }),
      ...vectorLayers.filter(layer => isPolygonLayer(layer)),  // Add polygon layers first
      ...vectorLayers.filter(layer => isLineStringLayer(layer)), // Add LineString layers next
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

  Object.keys(data).forEach((key, index) => {
    const layerDiv = document.createElement("div");
    layerDiv.style.display = "flex";
    layerDiv.style.alignItems = "center";

    const symbolLabelContainer = document.createElement("div");
    symbolLabelContainer.style.display = "flex";
    symbolLabelContainer.style.width = "150px";  // Setting fixed width to ensure alignment
    symbolLabelContainer.style.alignItems = "center";
    symbolLabelContainer.style.justifyContent = "center";

    const symbolContainer = document.createElement("div");
    symbolContainer.style.display = "flex";
    symbolContainer.style.alignItems = "center";
    symbolContainer.style.width = "120px"; // fixed width

    const canvas = document.createElement("canvas");
    canvas.width = 50;
    canvas.height = 10;
    const ctx = canvas.getContext("2d");

    const useGradient = gradientFlags[key.split(".")[0]];
    const layer = vectorLayers[index];  // Get the layer for this entry
    const layerColor = shapefileColors[key.split(".")[0]] || 'blue'; // Fetch color from dictionary, or default to blue
    const attributeKey = key.split(".")[0];
    const attributeName = gradientAttributes[attributeKey];
    const bounds = attributeBounds[key];

    if (isPolygonLayer(layer)) {
        if (useGradient) {
            const minVal = bounds.min > 100 ? bounds.min.toExponential(2) : bounds.min;
            const minDiv = document.createElement("div");
            minDiv.innerText = minVal.toString();
            minDiv.style.marginRight = "5px";
            symbolContainer.appendChild(minDiv);
            symbolContainer.style.marginRight = "40px";

            const gradient = ctx.createLinearGradient(0, 0, 50, 0);
            gradient.addColorStop(0, "rgb(255, 255, 255)");
            gradient.addColorStop(1, `rgb(255, 0, 0)`);
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 50, 10);
            symbolContainer.appendChild(canvas);
            symbolContainer.style.marginRight = "40px";

            const maxVal = bounds.max > 100 ? bounds.max.toExponential(2) : bounds.max;
            const maxDiv = document.createElement("div");
            maxDiv.innerText = maxVal.toString();
            maxDiv.style.marginLeft = "5px";
            symbolContainer.appendChild(maxDiv);
            symbolContainer.style.marginRight = "40px";
          } else {
            // Solid color rectangle
            ctx.fillStyle = "rgb(255, 128, 128)";
            ctx.fillRect(0, 0, 50, 10);
            symbolContainer.appendChild(canvas);
            symbolContainer.style.marginRight = "40px";
            }
    } else if (isLineStringLayer(vectorLayers[index])) {
          if (useGradient && bounds) { // Check to make sure bounds are actually defined
            const minVal = bounds.min > 100 ? bounds.min.toExponential(2) : bounds.min;
            const minDiv = document.createElement("div");
            minDiv.innerText = minVal.toString(); // Minimum attribute value
            minDiv.style.marginRight = "5px";
            symbolContainer.appendChild(minDiv);
            symbolContainer.style.marginRight = "40px";

          // New canvas for line width
          const canvas = document.createElement("canvas");
          canvas.width = 50;
          canvas.height = 20; // Increased height to make space for the varying line width
          const ctx = canvas.getContext("2d");

          // Draw a line segment that gradually increases in width from 1 to 10
          let yPosition = 10; // vertical position for the line

          for (let x = 0; x <= 50; x++) {
            let lineWidth = 1 + (x / 50) * 9; // lineWidth will vary between 1 and 10
            ctx.strokeStyle = layerColor;
            ctx.lineWidth = lineWidth;

            ctx.beginPath();
            ctx.moveTo(x, yPosition - lineWidth / 2);
            ctx.lineTo(x, yPosition + lineWidth / 2);
            ctx.stroke();
          }

          symbolContainer.appendChild(canvas);
          symbolContainer.style.marginRight = "40px";

          // Check to make sure bounds are actually defined
            const maxVal = bounds.max > 100 ? bounds.max.toExponential(2) : bounds.max;
            const maxDiv = document.createElement("div");
            maxDiv.innerText = maxVal.toString(); // Maximum attribute value
            maxDiv.style.marginLeft = "5px";
            symbolContainer.appendChild(maxDiv);
            symbolContainer.style.marginRight = "40px";
            } else {
            // New canvas for constant width line
            const constantCanvas = document.createElement("canvas");
            constantCanvas.width = 50;
            constantCanvas.height = 10;  // Set height to 10 for constant line width
            const constantCtx = constantCanvas.getContext("2d");

            constantCtx.strokeStyle = layerColor;
            constantCtx.lineWidth = 1;

            constantCtx.beginPath();
            constantCtx.moveTo(0, 5);
            constantCtx.lineTo(50, 5);
            constantCtx.stroke();

            symbolContainer.appendChild(constantCanvas);
            symbolContainer.style.marginRight = "40px";
      }
    } else {
      // Point symbol
      ctx.fillStyle = layerColor; // Use the fetched color
      ctx.beginPath();
      ctx.arc(25, 5, 3, 0, Math.PI * 2);
      ctx.fill();
      canvas.style.marginLeft = "30px";  // Shift canvas to align the center
      symbolContainer.appendChild(canvas);
      symbolContainer.style.marginRight = "40px";
    }

    layerDiv.appendChild(symbolContainer);

    symbolLabelContainer.appendChild(symbolContainer);  // Append symbolContainer to symbolLabelContainer

    const title = document.createElement("div");
    title.innerText = shapefileLabels[key.split(".")[0]];
    title.style.marginLeft = "20px";

    layerDiv.appendChild(symbolLabelContainer);  // Append symbolLabelContainer to layerDiv
    layerDiv.appendChild(title);
    legendDiv.appendChild(layerDiv);
  });
}


// Update map size when the window is resized
window.addEventListener('resize', function() {
  map.updateSize();
});
