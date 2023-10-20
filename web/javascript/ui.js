import { geojsonTypes, availableGradientAttributes, selectedGradientAttributes, legendLabels } from './name_maps.js';
import { updateSelectedLayers, updateLegend, updateLayer, data } from './map.js'

function populateLayerDropdown(mapping) {
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
  const highwayFlowContainer = document.getElementById("highway-flow-checkboxes");
  const highwayInfraContainer = document.getElementById("highway-infra-checkboxes");
  const pointH2prodContainer = document.getElementById("point-h2prod-checkboxes");
  const pointRefuelContainer = document.getElementById("point-refuel-checkboxes");
  const pointOtherContainer = document.getElementById("point-other-checkboxes");

  // Clear existing options and checkboxes
  areaLayerDropdown.innerHTML = "";
  highwayFlowContainer.innerHTML = "";
  highwayInfraContainer.innerHTML = "";
  pointH2prodContainer.innerHTML = "";
  pointRefuelContainer.innerHTML = "";
  pointOtherContainer.innerHTML = "";

  // Make a 'None' option for area feature in case the user doesn't want one
  const option = document.createElement("option");
  option.value = 'None';
  option.textContent = 'None';
  areaLayerDropdown.appendChild(option);

  // Add options for area layers
  for (const key in mapping) {
    if (geojsonTypes[key] === "area") {
      const option = document.createElement("option");
      option.value = mapping[key];
      option.textContent = key;
      areaLayerDropdown.appendChild(option);
    } else if (geojsonTypes[key][0] === "highway") {
      // Add checkboxes for highway layers
      if (geojsonTypes[key][1] === "flow") {
      addLayerCheckbox(key, mapping[key], highwayFlowContainer);
      }
      else if (geojsonTypes[key][1] === "infra") {
      addLayerCheckbox(key, mapping[key], highwayInfraContainer);
      }
    } else if (geojsonTypes[key][0] === "point") {
      // Add checkboxes for point layers
      if (geojsonTypes[key][1] === "refuel") {
        addLayerCheckbox(key, mapping[key], pointRefuelContainer);
      }
      else if (geojsonTypes[key][1] === "h2prod") {
      addLayerCheckbox(key, mapping[key], pointH2prodContainer);
      }
      else if (geojsonTypes[key][1] === "other") {
      addLayerCheckbox(key, mapping[key], pointOtherContainer);
      }
    }
  }
}

function addLayerCheckbox(key, value, container) {
  const checkboxContainer = document.createElement("div");
  checkboxContainer.classList.add("checkbox-container"); // Add this line

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.value = value;
  checkbox.id = `${key}-checkbox`; // Unique ID for the checkbox
  checkboxContainer.appendChild(checkbox);

  const label = document.createElement("label");
  label.setAttribute("for", `${key}-checkbox`);
  label.textContent = key;
  checkboxContainer.appendChild(label);

  container.appendChild(checkboxContainer);

  // New button creation
  const detailsButton = document.createElement("button");
  detailsButton.textContent = "Details";
  detailsButton.setAttribute("data-key", key);
  detailsButton.classList.add("details-btn");
  checkboxContainer.appendChild(detailsButton);
}

//// Add an event listener to the "Apply" button
//document.getElementById("apply-button").addEventListener("click", applySelection);
//
//function applySelection() {
//  const selectedLayerNames = getSelectedLayers();
//}

function getSelectedLayers() {
  const selectedLayerNames = [];
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');

  // Get selected checkboxes
  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      selectedLayerNames.push(checkbox.nextSibling.textContent); // Get the label text
    }
  });

  // Get the selected area layer from the dropdown
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
 for (const option of areaLayerDropdown.options) {
    if (option.selected && option.text !== 'None') {
      selectedLayerNames.push(option.text); // Push the text of the selected option
    }
  }
  return selectedLayerNames;
}

// Add event listener to the parent element of the buttons
document.getElementById("layer-selection").addEventListener("click", function (event) {
  if (event.target.classList.contains("toggle-button")) {
    const targetId = event.target.getAttribute("data-target");
    const target = document.getElementById(targetId);

    if (target.style.display === "none") {
      target.style.display = "block";
    } else {
      target.style.display = "none";
    }
  }
});

document.body.addEventListener('click', function(event) {
  // Check if a details button was clicked
  if (event.target.classList.contains("details-btn")) {
    const key = event.target.getAttribute("data-key");

    // Fetch details based on key or prepare details text in some other way
    document.getElementById('details-content').innerText = getDetails(key);
    document.getElementById('details-title').innerText = `${key} Details`;

    // Show the modal
    document.getElementById('details-modal').style.display = 'flex';

    // Populate the dropdown menu with attribute names
    const attributeDropdown = document.getElementById("attribute-dropdown");
    attributeDropdown.innerHTML = "";

    // Assuming you have an array of attribute names for the current feature
    const attributeNames = getAttributeNamesForFeature(key);

    // Create and add options to the dropdown
    attributeNames.forEach((attributeName) => {
      const option = document.createElement("option");
      option.value = attributeName;
      option.text = legendLabels[key][attributeName];
      if (selectedGradientAttributes[key] === attributeName) {
        option.selected = true;
      }
      attributeDropdown.appendChild(option);
    });

    // Add an event listener to the dropdown to handle attribute selection
    attributeDropdown.addEventListener("change", function () {
      selectedGradientAttributes[key] = attributeDropdown.value;
      // Call a function to update the plot and legend with the selected attribute
      updatePlotAndLegend(key);
    });
  }

  // Check if the close button of the modal was clicked
  if (event.target.classList.contains("close-btn")) {
    document.getElementById('details-modal').style.display = 'none';
  }
});


function getAttributeNamesForFeature(layerName) {
  // Check if the layerName exists in availableGradientAttributes
  if (layerName in availableGradientAttributes) {
    return availableGradientAttributes[layerName];
  } else {
    return []; // Return an empty array if the layerName is not found
  }
}

function updatePlotAndLegend(key) {
  updateLayer(key, selectedGradientAttributes[key]);
  updateLegend(data);
}

// Sample implementation of getDetails function
function getDetails(key) {
  // Fetch or compute details related to the 'key'.
  // For the simplicity of this example, returning a static text.
  return `Details about ${key}. Implement your logic to fetch or compute the real details.`;
}

export { populateLayerDropdown, getSelectedLayers };