// Function to populate the layer selection drop-down using the mapping
function populateLayerDropdown(mapping) {
  const layerDropdown = document.getElementById("layer-dropdown");

  // Clear existing options
  layerDropdown.innerHTML = "";

//  // Add an "All Layers" option
//  const allOption = document.createElement("option");
//  allOption.value = "all";
//  allOption.textContent = "All Layers";
//  layerDropdown.appendChild(allOption);

  // Add options based on the mapping
  for (const key in mapping) {
    const layerOption = document.createElement("option");
    layerOption.value = mapping[key];
    layerOption.textContent = key;
    layerDropdown.appendChild(layerOption);
  }
}

function getSelectedLayers() {
  const selectedLayerNames = [];
  const layerDropdown = document.getElementById("layer-dropdown");

  // Get selected options from the drop-down
  for (const option of layerDropdown.options) {
    if (option.selected) {
      selectedLayerNames.push(option.text); // Push the text of the selected option
    }
  }

  return selectedLayerNames;
}

export { populateLayerDropdown, getSelectedLayers };