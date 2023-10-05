import { shapefileTypes } from './name_maps.js';

function populateLayerDropdown(mapping) {
  const areaLayerDropdown = document.getElementById("area-layer-dropdown");
  const highwayLayerContainer = document.getElementById("highway-layer-checkboxes");
  const pointLayerContainer = document.getElementById("point-layer-checkboxes");

  // Clear existing options and checkboxes
  areaLayerDropdown.innerHTML = "";
  highwayLayerContainer.innerHTML = "";
  pointLayerContainer.innerHTML = "";

  // Make a 'None' option for area feature in case the user doesn't want one
  const option = document.createElement("option");
  option.value = 'None';
  option.textContent = 'None';
  areaLayerDropdown.appendChild(option);

  // Add options for area layers
  for (const key in mapping) {
    if (shapefileTypes[key] === "area") {
      const option = document.createElement("option");
      option.value = mapping[key];
      option.textContent = key;
      areaLayerDropdown.appendChild(option);
    } else if (shapefileTypes[key] === "highway") {
      // Add checkboxes for highway layers
      addLayerCheckbox(key, mapping[key], highwayLayerContainer);
    } else if (shapefileTypes[key] === "point") {
      // Add checkboxes for point layers
      addLayerCheckbox(key, mapping[key], pointLayerContainer);
    }
  }
}

function addLayerCheckbox(key, value, container) {
  const checkboxContainer = document.createElement("div");
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
}

//// Add an event listener to the "Apply" button
//document.getElementById("apply-button").addEventListener("click", applySelection);
//
//function applySelection() {
//  const selectedLayerNames = getSelectedLayers();
//}

function getSelectedLayers() {
  console.log('in getSelectedLayers')
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
    if (option.selected) {
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

export { populateLayerDropdown, getSelectedLayers };