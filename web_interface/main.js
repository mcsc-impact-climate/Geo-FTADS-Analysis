var vectorLayers = [];
var map;
var attributeBounds = {}; // Object to store min and max attribute values for each shapefile


const shapefileLabels = {
  'electricity_rates_by_state_merged': 'Electricity rate (cents/kWh)',
  'US_elec': 'DCFC Charging Stations',
};

// Key: shapefile name, Value: boolean indicating whether to apply a gradient
const gradientFlags = {
  'electricity_rates_by_state_merged': true,
  'US_elec': false,
};

const gradientAttributes = {
  'electricity_rates_by_state_merged': 'Cents_kWh',
};

// Key: shapefile name, Value: color to use
const shapefileColors = {
  'electricity_rates_by_state_merged': 'red',
  'US_elec': 'blue',
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
        
        const minVal = Math.min(...features.map(f => f.get(gradientAttributes[key.split(".")[0]]) || Infinity));
        const maxVal = Math.max(...features.map(f => f.get(gradientAttributes[key.split(".")[0]]) || -Infinity));

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
    const bounds = attributeBounds[shapefileName]; // Get the bounds for this specific shapefile
    const attributeValue = feature.get(attributeName);
    
    const useGradient = gradientFlags[shapefileName.split(".")[0]];
    const layerColor = shapefileColors[shapefileName.split(".")[0]];

    if (useGradient && bounds) {
      const component = Math.floor(255 - (255 * (attributeValue - bounds.min) / (bounds.max - bounds.min)));
      const fillColor = `rgb(255, ${component}, ${component})`;
        
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

  Object.keys(data).forEach((key, index) => {
    const layerDiv = document.createElement("div");
    layerDiv.style.display = "flex";
    layerDiv.style.alignItems = "center";

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
    const layerColor = shapefileColors[key.split(".")[0]];

    if (isPolygonLayer(layer)) {
      if (useGradient) {
        const bounds = attributeBounds[key];
        const minDiv = document.createElement("div");
        minDiv.innerText = bounds.min;
        minDiv.style.marginRight = "5px";
        symbolContainer.appendChild(minDiv);

        const gradient = ctx.createLinearGradient(0, 0, 50, 0);
        gradient.addColorStop(0, "rgb(255, 255, 255)");
        gradient.addColorStop(1, `rgb(255, 0, 0)`);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 50, 10);
        symbolContainer.appendChild(canvas);

        const maxDiv = document.createElement("div");
        maxDiv.innerText = bounds.max;
        maxDiv.style.marginLeft = "5px";
        symbolContainer.appendChild(maxDiv);
      } else {
        // Solid color rectangle
        ctx.fillStyle = "rgb(255, 128, 128)";
        ctx.fillRect(0, 0, 50, 10);
        symbolContainer.appendChild(canvas);
      }
    } else {
      // Point symbol
      ctx.fillStyle = layerColor;
      ctx.beginPath();
      ctx.arc(25, 5, 3, 0, Math.PI * 2);
      ctx.fill();
      canvas.style.marginLeft = "80px";  // Shift canvas to align the center
      symbolContainer.appendChild(canvas);
    }

    layerDiv.appendChild(symbolContainer);

    const title = document.createElement("div");
    title.innerText = shapefileLabels[key.split(".")[0]];
    title.style.marginLeft = "20px";

    layerDiv.appendChild(title);
    legendDiv.appendChild(layerDiv);
  });
}




// Update map size when the window is resized
window.addEventListener('resize', function() {
  map.updateSize();
});
