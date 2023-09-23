from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import geopandas as gpd
import json
import os

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/main.js')
def serve_js():
    return send_from_directory('.', 'main.js')

shapefile_directory = "shapefiles"
shapefiles = {
    'Truck Imports and Exports': os.path.join("../data/Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp"),
    'Electricity Rates': os.path.join(shapefile_directory, "electricity_rates_by_state_merged.shp"),
    'DCFC Chargers': os.path.join(shapefile_directory, "US_elec.shp"),
    'Highway Flows (SU)': os.path.join(shapefile_directory, "highway_assignment_links_single_unit.shp"),
    #'Highway Flows (Interstate)': os.path.join("../data/highway_assignment_links/highway_assignment_links_interstate.shp"),
    'Electrolyzers': os.path.join(shapefile_directory, "electrolyzer_operational.shp"),
}

@app.route('/get_shapefiles')
def get_shapefiles():
    return jsonify(shapefiles)

@app.route('/get_geojson/<shapefile_name>')
def get_geojson(shapefile_name):
    shapefile_path = shapefiles[shapefile_name]
    geojson_directory = "geojsons"
    geojson_filename = os.path.join(geojson_directory, os.path.splitext(os.path.basename(shapefile_path))[0] + '.geojson')

    # Check if the shapefile exists before proceeding
    if not os.path.exists(shapefile_path):
        print('path %s does not exist'%shapefile_path)

    if os.path.exists(geojson_filename):
        # Read and return the existing .geojson file
        with open(geojson_filename, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)
    else:
        # Convert shapefile to .geojson and save it
        shapefile = gpd.read_file(shapefile_path).to_crs(epsg=3857)
        geojson_data = json.loads(shapefile.to_json())

        # Save the .geojson file
        with open(geojson_filename, 'w') as geojson_file:
            json.dump(geojson_data, geojson_file)

    return jsonify(geojson_data)

if __name__ == '__main__':
    app.run(debug=True)
