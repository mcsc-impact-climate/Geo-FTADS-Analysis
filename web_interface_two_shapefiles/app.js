// Define the map container
var map = new ol.Map({
    target: 'map',
    layers: [],
    view: new ol.View({
        center: ol.proj.fromLonLat([0, 0]),
        zoom: 2
    })
});

// Fetch shapefile data from the backend
fetch('/get_shapefiles')
    .then(response => response.json())
    .then(data => {
        // Create GeoJSON layers for shapefile data
        var shapefile1Layer = new ol.layer.Vector({
            source: new ol.source.Vector({
                features: (new ol.format.GeoJSON()).readFeatures(data.shapefile1)
            }),
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'blue',
                    width: 2
                })
            })
        });

        var shapefile2Layer = new ol.layer.Vector({
            source: new ol.source.Vector({
                features: (new ol.format.GeoJSON()).readFeatures(data.shapefile2)
            }),
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'red',
                    width: 2
                })
            })
        });

        // Add shapefile layers to the map
        map.addLayer(shapefile1Layer);
        map.addLayer(shapefile2Layer);
    })
    .catch(error => console.error('Error fetching data:', error));
