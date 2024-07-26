import { initMap, updateSelectedLayers, updateLegend, attachEventListeners, handleMapClick, handleMapHover, map } from './map.js';
import { populateLayerDropdown, getSelectedLayers } from './ui.js';

let geojsonNames = {};

// Fetch available geojson names from the Flask app
fetch(GET_GEOJSONS)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    geojsonNames = data;
    // Populate the layer selection drop-down with geojson names
    populateLayerDropdown(geojsonNames);
    attachEventListeners(); // Attach event listeners after populating the dropdown
    initMap(); // Initialize the map after populating the dropdown
    map.on('pointermove', handleMapHover);
    map.on('singleclick', handleMapClick);
  })
  .catch(error => {
    console.log('Fetch Error:', error);
  });

export { geojsonNames };
