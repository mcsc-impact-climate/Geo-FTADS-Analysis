import { initMap, updateSelectedLayers, updateLegend, attachEventListeners } from './map.js';
import { populateLayerDropdown, getSelectedLayers } from './ui.js';

// Fetch available shapefile names from the Flask app
fetch('/get_shapefiles')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(shapefileNames => {
    // Populate the layer selection drop-down with shapefile names
    populateLayerDropdown(shapefileNames);
    attachEventListeners(); // Attach event listeners after populating the dropdown
    initMap(); // Initialize the map after populating the dropdown
  })
  .catch(error => {
    console.log('Fetch Error:', error);
  });

// Update map size when the window is resized
window.addEventListener('resize', function() {
  if (map) {
  map.updateSize();
  }
});
