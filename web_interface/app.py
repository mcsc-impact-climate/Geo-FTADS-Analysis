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

shapefile_directory = "../data"
shapefiles = [
    os.path.join(shapefile_directory, "electricity_rates_merged/electricity_rates_by_state_merged.shp"),
    os.path.join(shapefile_directory, "Fuel_Corridors/US_elec/US_elec.shp"),
    os.path.join(shapefile_directory, "highway_assignment_links/highway_assignment_links_single_unit.shp"),
    os.path.join(shapefile_directory, "hydrogen_hubs/shapefiles/electrolyzer_operational.shp")]

@app.route('/get_shapefiles')
def get_shapefiles():
    shapefile_data = {}
    for sf_path in shapefiles:
        sf_filename = os.path.basename(sf_path)
        shapefile = gpd.read_file(sf_path).to_crs(epsg=3857)
        shapefile_data[sf_filename] = json.loads(shapefile.to_json())
    return jsonify(shapefile_data)

if __name__ == '__main__':
    app.run(debug=True)
