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

shapefiles = ["electricity_rates_by_state_merged.shp", "US_elec.shp", "highway_assignment_links_single_unit.shp", "electrolyzer_operational.shp"]

@app.route('/get_shapefiles')
def get_shapefiles():
    shapefile_data = {}
    for sf in shapefiles:
        shapefile = gpd.read_file(sf).to_crs(epsg=3857)
        shapefile_data[sf] = json.loads(shapefile.to_json())
    return jsonify(shapefile_data)

if __name__ == '__main__':
    app.run(debug=True)
