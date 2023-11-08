import { geojsonTypes, availableGradientAttributes, selectedGradientAttributes, legendLabels, truckChargingOptions, selectedTruckChargingOptions } from './name_maps.js';
import { updateSelectedLayers, updateLegend, updateLayer, data, removeLayer, loadLayer } from './map.js'

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
  detailsButton.textContent = "More";
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

function getSelectedLayersValues() {
  const selectedLayerValues = new Map();
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');

  // Get selected checkboxes
  checkboxes.forEach((checkbox) => {
    if (checkbox.checked) {
      // print(checkbox)
      selectedLayerValues.set(checkbox.nextSibling.textContent, checkbox.value); // Get the label text
    }
  });

  // Get the selected area layer from the dropdown
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
 for (const option of areaLayerDropdown.options) {
    if (option.selected && option.text !== 'None') {
      selectedLayerValues.set(option.text, option.value); // Push the text of the selected option
    }
  }
  return selectedLayerValues;
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

document.getElementById("area-details-button").addEventListener("click", function () {
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
  const selectedAreaLayer = areaLayerDropdown.value;

  if (selectedAreaLayer !== "") {
    // Fetch details based on the selected area layer
    const selectedAreaLayerName = getAreaLayerName(selectedAreaLayer);

    const details = getAreaLayerDetails(selectedAreaLayer);

    // Reset the content of the modal
    resetModalContent();

    // Fetch details based on key or prepare details text in some other way
    document.getElementById('details-content').innerText = '';   // DMM: Replace with actual details about the data source
    document.getElementById('details-title').innerText = `${selectedAreaLayerName} Details`;

    // Show the modal
    document.getElementById('details-modal').style.display = 'flex';

    // Create a dropdown menu to choose attributes for the area layer
    createAttributeDropdown(selectedAreaLayerName);
  }
});

// Function to get the selected area layer's name based on its value
function getAreaLayerName(selectedValue) {
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
  const selectedOption = Array.from(areaLayerDropdown.options).find((option) => option.value === selectedValue);

  return selectedOption ? selectedOption.textContent : "";
}


function getAreaLayerDetails(layerName) {
  // Fetch or compute details related to the 'layerName'.
  // Replace this with your logic to get area layer details.
  // For example, you can fetch data from an API or a database.
  return `Details about ${layerName}`;
}

function createAttributeDropdown(key) {
  // Check if the attribute-dropdown already exists
  if (document.getElementById("attribute-dropdown")) {
    return; // Exit the function if it already exists
  }

  const attributeDropdownContainer = document.createElement("div");
  attributeDropdownContainer.classList.add("attribute-dropdown-container");

  const label = document.createElement("label");
  label.setAttribute("for", "attribute-dropdown");
  label.textContent = "Gradient Attribute: ";

  const attributeDropdown = document.createElement("select");
  attributeDropdown.id = "attribute-dropdown";

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

  // Append the label and dropdown to the container
  attributeDropdownContainer.appendChild(label);
  attributeDropdownContainer.appendChild(attributeDropdown);

  // Append the container to the modal content
  const modalContent = document.querySelector(".modal-content");
  modalContent.appendChild(attributeDropdownContainer);
}

function createTruckChargingDropdown(name, parameter, dropdown_label, key) {
  const options = truckChargingOptions[parameter]
  // Check if the dropdown already exists
  if (document.getElementById(name + "-dropdown")) {
    return; // Exit the function if it already exists
  }

  const dropdownContainer = document.createElement("div");
  dropdownContainer.classList.add(name + "-dropdown-container");

  const label = document.createElement("label");
  label.setAttribute("for", name + "-dropdown");
  label.textContent = dropdown_label;

  const dropdown = document.createElement("select");
  dropdown.id = name + "-dropdown";

  // Create and add options to the dropdown
  for (const this_option in options) {
    if (options.hasOwnProperty(this_option)) {
        const option = document.createElement("option");
        option.value = options[this_option]; // Use the key as the value
        option.text = this_option; // Use the corresponding value as the text
        if (selectedTruckChargingOptions[parameter] === option.value) {
            option.selected = true;
        }
        dropdown.appendChild(option);
    }
  }

  // Add an event listener to the dropdown to handle attribute selection
  dropdown.addEventListener("change", async function () {
    selectedTruckChargingOptions[parameter] = dropdown.value;
    await removeLayer(key);
    await loadLayer(key, "Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_" + selectedTruckChargingOptions['Range'] + "_chargingtime_" + selectedTruckChargingOptions['Charging Time'] + "_maxwait_" + selectedTruckChargingOptions['Max Allowed Wait Time'] + ".geojson");
    await updateSelectedLayers();
    await updateLegend();
  });

  // Append the label and dropdown to the container
  dropdownContainer.appendChild(label);
  dropdownContainer.appendChild(dropdown);

  // Append the container to the modal content
  const modalContent = document.querySelector(".modal-content");
  modalContent.appendChild(dropdownContainer);
}

function createChargingDropdowns(key) {
  const rangeDropdownResult = createTruckChargingDropdown("range", "Range", "Truck Range: ", key);
  const chargingTimeDropdownResult = createTruckChargingDropdown("chargingTime", "Charging Time", "Charging Time: ", key);
  const maxWaitTimeDropdownResult = createTruckChargingDropdown("maxWaitTime", "Max Allowed Wait Time", "Max Allowed Wait Time: ", key);
}

document.body.addEventListener('click', function(event) {
  // Check if a details button was clicked
  if (event.target.classList.contains("details-btn") && event.target.hasAttribute("data-key")) {
    const key = event.target.getAttribute("data-key");

    // Reset the content of the modal
    resetModalContent();

    // Fetch details based on key or prepare details text in some other way
    document.getElementById('details-content').innerText = getDetails(key);
    document.getElementById('details-title').innerText = `${key} Details`;

    // Show the modal
    document.getElementById('details-modal').style.display = 'flex';

    // Create a dropdown menu to choose the gradient attribute
    createAttributeDropdown(key);

    // Create additional dropdown menus for the truck charging layer
    if(key === "Truck Stop Charging") {
        createChargingDropdowns(key);
    }
  }

  // Check if the close button of the modal was clicked
  if (event.target.classList.contains("close-btn") || event.target.parentElement.tagName === 'SELECT') {
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
  updateLegend();
}

// Sample implementation of getDetails function
function getDetails(key) {
  // Fetch or compute details related to the 'key'.
  // For the simplicity of this example, returning a static text.
  //return `Details about ${key}`;
  return '';
}

function resetModalContent() {
  const modalContent = document.querySelector(".modal-content");

  // Remove attribute-dropdown-container if it exists
  const attributeDropdownContainer = document.querySelector(".attribute-dropdown-container");
  if (attributeDropdownContainer) {
    modalContent.removeChild(attributeDropdownContainer);
  }

  // Remove range-dropdown-container if it exists
  const rangeDropdownContainer = document.querySelector(".range-dropdown-container");
  if (rangeDropdownContainer) {
    modalContent.removeChild(rangeDropdownContainer);
  }

  // Remove chargingTime-dropdown-container if it exists
  const chargingTimeDropdownContainer = document.querySelector(".chargingTime-dropdown-container");
  if (chargingTimeDropdownContainer) {
    modalContent.removeChild(chargingTimeDropdownContainer);
  }

  // Remove maxWaitTime-dropdown-container if it exists
  const maxWaitTimeDropdownContainer = document.querySelector(".maxWaitTime-dropdown-container");
  if (maxWaitTimeDropdownContainer) {
    modalContent.removeChild(maxWaitTimeDropdownContainer);
  }
}

export { populateLayerDropdown, getSelectedLayers, getSelectedLayersValues};