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
shapefiles = [
    os.path.join(shapefile_directory, "electricity_rates_merged/electricity_rates_by_state_merged.shp"),
    os.path.join(shapefile_directory, "Fuel_Corridors/US_elec/US_elec.shp"),
    os.path.join(shapefile_directory, "highway_assignment_links/highway_assignment_links_single_unit.shp"),
    os.path.join(shapefile_directory, "hydrogen_hubs/shapefiles/electrolyzer_operational.shp")]

@app.route('/get_shapefiles')
def get_shapefiles():
    shapefile_data = {}
    geojson_directory = "geojsons"

    # Check if geojson_directory exists, create it if not
    if not os.path.exists(geojson_directory):
        os.makedirs(geojson_directory)

    for sf_path in shapefiles:
        sf_filename = os.path.basename(sf_path)
        geojson_filename = os.path.join(geojson_directory, os.path.splitext(sf_filename)[0] + '.geojson')

        if os.path.exists(geojson_filename):
            # Read and return the existing .geojson file
            with open(geojson_filename, 'r') as geojson_file:
                shapefile_data[sf_filename] = json.load(geojson_file)
        else:
            # Convert shapefile to .geojson and save it
            shapefile = gpd.read_file(sf_path).to_crs(epsg=3857)
            geojson_data = json.loads(shapefile.to_json())
            shapefile_data[sf_filename] = geojson_data

            # Save the .geojson file
            with open(geojson_filename, 'w') as geojson_file:
                json.dump(geojson_data, geojson_file)

    return jsonify(shapefile_data)

if __name__ == '__main__':
    app.run(debug=True)
