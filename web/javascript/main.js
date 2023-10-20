import { initMap, updateSelectedLayers, updateLegend, attachEventListeners } from './map.js';
import { populateLayerDropdown, getSelectedLayers } from './ui.js';

// Fetch available geojson names from the Flask app
fetch('/get_geojsons')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(geojsonNames => {
    // Populate the layer selection drop-down with geojson names
    populateLayerDropdown(geojsonNames);
    attachEventListeners(); // Attach event listeners after populating the dropdown
    initMap(); // Initialize the map after populating the dropdown
  })
  .catch(error => {
    console.log('Fetch Error:', error);
  });

//// Update map size when the window is resized
//window.addEventListener('resize', function() {
//  if (map) {
//  map.updateSize();
//  }
//});
