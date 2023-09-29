from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import geopandas as gpd
import json
import os
from collections import OrderedDict
from shapely.geometry import shape, mapping
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/main.js')
def serve_js():
    return send_from_directory('.', 'main.js')

shapefile_directory = "shapefiles"

# Create an ordered dictionary to maintain the order of items
shapefiles = OrderedDict()

## Total domestic Imports and Exports
#shapefiles['Truck Imports and Exports'] = os.path.join("../data/Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp")
#
## Grid emission intensity
#shapefiles['Grid Emission Intensity'] = os.path.join("../data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp")
#
## Commercial electricity price by state
shapefiles['Commercial Electricity Price'] = os.path.join(shapefile_directory, "electricity_rates_by_state_merged.shp")
#
## Maximum demand charges from NREL
#shapefiles['Maximum Demand Charge'] = os.path.join("../data/electricity_rates_merged/demand_charges_merged.shp")
#
## Highway flows
#shapefiles['Highway Flows (Interstate)'] = os.path.join("../data/highway_assignment_links/highway_assignment_links_interstate.shp")
shapefiles['Highway Flows (SU)'] = os.path.join(shapefile_directory, "highway_assignment_links_single_unit.shp")
#shapefiles['Highway Flows (CU)'] = os.path.join(shapefile_directory, "highway_assignment_links_combined_unit.shp")

# Alternative fueling stations along highway corridors
shapefiles['DCFC Chargers'] = os.path.join(shapefile_directory, "US_elec.shp")
#shapefiles['Hydrogen Stations'] = os.path.join("../data/Fuel_Corridors/US_hy/US_hy.shp")
#shapefiles['LNG Stations'] = os.path.join("../data/Fuel_Corridors/US_lng/US_lng.shp")
#shapefiles['CNG Stations'] = os.path.join("../data/Fuel_Corridors/US_cng/US_cng.shp")
#shapefiles['LPG Stations'] = os.path.join("../data/Fuel_Corridors/US_lpg/US_lpg.shp")

# Hydrogen hubs
shapefiles['Operational Electrolyzers'] = os.path.join(shapefile_directory, "electrolyzer_operational.shp")
#shapefiles['Installed Electrolyzers'] = os.path.join("../data/hydrogen_hubs/shapefiles/electrolyzer_installed.shp")
#shapefiles['Planned Electrolyzers'] = os.path.join("../data/hydrogen_hubs/shapefiles/electrolyzer_planned_under_construction.shp")
#shapefiles['Hydrogen from Refineries'] = os.path.join("../data/hydrogen_hubs/shapefiles/refinery.shp")

# DOE-funded heavy duty vehicle infrastructure projects
#shapefiles['East Coast ZEV Corridor'] = os.path.join("../data/hd_zev_corridors/eastcoast.shp")
#shapefiles['Midwest ZEV Corridor'] = os.path.join("../data/hd_zev_corridors/midwest.shp")
#shapefiles['Houston to LA H2 Corridor'] = os.path.join("../data/hd_zev_corridors/h2la.shp")
#shapefiles['I-710 EV Corridor'] = os.path.join("../data/hd_zev_corridors/la_i710.shp")
#shapefiles['Northeast EV Corridor'] = os.path.join("../data/hd_zev_corridors/northeast.shp")
#shapefiles['Bay Area EV Roadmap'] = os.path.join("../data/hd_zev_corridors/bayarea.shp")
#shapefiles['Salt Lake City Region EV Plan'] = os.path.join("../data/hd_zev_corridors/saltlake.shp")
#
## Truck stop parking locations
#shapefiles['Truck Stop Locations'] = os.path.join("../data/Truck_Stop_Parking/Truck_Stop_Parking.shp")
#
## Principal ports
#shapefiles['Principal Ports'] = os.path.join("../data/Principal_Ports/Principal_Port.shp")
#
## Regional Incentives
#shapefiles['State-Level Incentives and Regulations'] = os.path.join("../data/incentives_and_regulations_merged/all_incentives_and_regulations.shp")

@app.route('/get_shapefiles')
def get_shapefiles():
    json_str = json.dumps(shapefiles, sort_keys=False)
    return json_str

@app.route('/get_geojson/<shapefile_name>')
def get_geojson(shapefile_name):
    shapefile_path = shapefiles[shapefile_name]
    geojson_directory = "geojsons"
    geojson_filename = os.path.join(geojson_directory, os.path.splitext(os.path.basename(shapefile_path))[0] + '.geojson')
    
    # Create the directory to contain geojsons if it doesn't exist
    if not os.path.exists(geojson_directory):
        print('Making geojson dir')
        os.makedirs(geojson_directory)

    # Check if the shapefile exists before proceeding
    if not os.path.exists(shapefile_path):
        print('path %s does not exist'%shapefile_path)

    if os.path.exists(geojson_filename):
        # Read and return the existing .geojson file
        with open(geojson_filename, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)

            # Simplify the geometries
            tolerance = 10000  # Adjust this value based on your needs
            simplified_features = []

            for feature in geojson_data['features']:
                geometry = shape(feature['geometry'])

                # Check the geometry type and simplify accordingly
                if isinstance(geometry, Polygon):
                    simplified_geometry = geometry.simplify(tolerance)
                elif isinstance(geometry, MultiPolygon):
                    simplified_geometry = MultiPolygon([polygon.simplify(tolerance) for polygon in geometry.geoms])
                elif isinstance(geometry, LineString):
                    simplified_geometry = geometry.simplify(tolerance)
                elif isinstance(geometry, MultiLineString):
                    simplified_geometry = MultiLineString([line.simplify(tolerance) for line in geometry.geoms])
                else:
                    simplified_geometry = geometry

                feature['geometry'] = mapping(simplified_geometry)
                simplified_features.append(feature)

            geojson_data['features'] = simplified_features
    else:
        # Convert shapefile to .geojson and save it
        shapefile = gpd.read_file(shapefile_path).to_crs(epsg=3857)
        geojson_data = json.loads(shapefile.to_json())

        # Save the .geojson file
        with open(geojson_filename, 'w') as geojson_file:
            json.dump(geojson_data, geojson_file)

    print('jsonifying')
    jsonified = jsonify(geojson_data)
    print('done jsonifying')
    return jsonify(geojson_data)

if __name__ == '__main__':
    app.run(debug=True)
