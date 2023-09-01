var map = L.map('map').setView([39.8283, -98.5795], 4); // Centered on the U.S. with zoom level 4

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

var shapefileLayer = L.geoJSON().addTo(map);

var minValue, maxValue; // Define these variables in a higher scope

// Fetch shapefile data from the backend
fetch('/get_shapefile_data')
    .then(response => response.json())
    .then(data => {
        // Automatically calculate the minimum and maximum values of the property you want to map
        minValue = Number.POSITIVE_INFINITY;
        maxValue = Number.NEGATIVE_INFINITY;

        data.features.forEach(function (feature) {
            var propertyValue = feature.properties.Cents_kWh; // Replace with your property name
            if (propertyValue < minValue) {
                minValue = propertyValue;
            }
            if (propertyValue > maxValue) {
                maxValue = propertyValue;
            }
        });

        shapefileLayer.addData(data);

        shapefileLayer.setStyle(function (feature) {
            var propertyValue = feature.properties.Cents_kWh; // Replace with your property name
            var color = 'gray'; // Default to gray if no mapping found

            // Calculate the gradient color based on the property value
            var gradientColor = calculateGradientColor(propertyValue, minValue, maxValue);

            return { fillColor: gradientColor, fillOpacity: 0.7, color: 'black', weight: 1 };
        });
        
        // Create a legend and add it to the map
        createLegend(map, data, 'Cents_kWh');
    });

// Add a variable to track the shapefileLayer visibility
var isShapefileLayerVisible = true;

function createLegend(map, data, propertyName) {
    var legend = L.control({ position: 'bottomright' });

    // Define the labels for the legend
    legend.onAdd = function (map) {
        var div = L.DomUtil.create('div', 'legend');
        var labels = [];

        // Calculate the minimum and maximum values from the data
        var minValue = Number.POSITIVE_INFINITY;
        var maxValue = Number.NEGATIVE_INFINITY;

        data.features.forEach(function (feature) {
            var propertyValue = feature.properties[propertyName]; // Use the provided property name
            if (propertyValue < minValue) {
                minValue = propertyValue;
            }
            if (propertyValue > maxValue) {
                maxValue = propertyValue;
            }
        });

        // Add a left-justified header
        labels.push('<div class="legend-header">' + propertyName + '</div>');

        // Calculate the number of steps in the color gradient
        var numSteps = 5; // Adjust the number of steps as needed

        // Calculate the step size based on the range of values
        var stepSize = (maxValue - minValue) / numSteps;

        // Generate labels and colors for the legend based on the gradient
        for (var i = 0; i <= numSteps; i++) {
            var value = minValue + i * stepSize;
            var color = calculateGradientColor(value, minValue, maxValue);

            // Use the same property value that's being visualized in the shapefile
            var propertyValue = value.toFixed(2); // Use a formatted version of the value

            // Create a colored square next to the value
            var coloredSquare = '<div class="color-square" style="background-color:' + color + '"></div>';

            labels.push(
                '<div class="legend-row">' +
                coloredSquare +
                '<div class="legend-value">' + propertyValue + '</div>' +
                '</div>'
            );
        }

        // Add a white background to the legend
        div.style.backgroundColor = 'white';

        // Set a fixed width for the legend
        div.style.width = '200px';

        // Add a black border to the legend
        div.style.border = '2px solid black';

        // Append CSS styles for the legend to the <head> of the document
        var style = document.createElement('style');
        style.innerHTML = `
            /* CSS for colored squares */
            .color-square {
                width: 20px; /* Adjust the width as needed */
                height: 20px; /* Adjust the height as needed */
                display: inline-block;
                margin-right: 5px; /* Adjust the margin as needed */
            }

            /* CSS for legend rows */
            .legend-row {
                margin-bottom: 5px; /* Adjust the margin as needed */
                display: flex;
                align-items: center;
            }

            /* CSS for legend header */
            .legend-header {
                text-align: left; /* Left-justify the text */
                margin-bottom: 5px; /* Add space below the header */
                font-weight: bold; /* Make the header bold */
            }
        `;
        document.head.appendChild(style);

        // Add the legend content to the div
        div.innerHTML = '<div><b>Legend</b></div>' + labels.join('');
        
        // Create a checkbox for the shapefileLayer visibility
        var shapefileToggle = document.createElement('input');
        shapefileToggle.type = 'checkbox';
        shapefileToggle.id = 'shapefile-toggle';

        // Add an event listener to the checkbox to toggle the shapefileLayer visibility
        shapefileToggle.addEventListener('change', toggleShapefileVisibility);

        // Create a container div for the checkbox and property name
        var propertyContainer = document.createElement('div');
        propertyContainer.className = 'legend-property-container';

        // Add the checkbox to the container
        propertyContainer.appendChild(shapefileToggle);

        // Add the property name to the container
        propertyContainer.appendChild(document.createTextNode(propertyName));

        // Append the container to the legend div
        div.appendChild(propertyContainer);

        return div;
    };

    legend.addTo(map);
}



// Define a function to calculate gradient color based on a value
function calculateGradientColor(value, minValue, maxValue) {
    // Define the color range (white to dark red)
    var minColor = [255, 255, 255]; // White
    var maxColor = [255, 0, 0];     // Dark Red

    // Calculate the normalized value between 0 and 1
    var normalizedValue = (value - minValue) / (maxValue - minValue);

    // Interpolate between minColor and maxColor based on the normalized value
    var interpolatedColor = [
        Math.round(minColor[0] + (maxColor[0] - minColor[0]) * normalizedValue),
        Math.round(minColor[1] + (maxColor[1] - minColor[1]) * normalizedValue),
        Math.round(minColor[2] + (maxColor[2] - minColor[2]) * normalizedValue)
    ];

    // Convert the RGB values to a CSS color string
    return 'rgb(' + interpolatedColor.join(',') + ')';
}

function toggleShapefileVisibility() {
    isShapefileLayerVisible = !isShapefileLayerVisible;

    if (isShapefileLayerVisible) {
        shapefileLayer.addTo(map);
    } else {
        shapefileLayer.removeFrom(map);
    }
}
