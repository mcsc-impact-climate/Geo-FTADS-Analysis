from flask import Flask, jsonify
import geopandas as gpd

app = Flask(__name__, static_url_path='', static_folder='./')

@app.route("/")
def root():
    return app.send_static_file("index.html")


# Shapefile directory
SHAPEFILE_DIR = "shapefiles/"

@app.route("/get_shapefiles", methods=["GET"])
def get_shapefiles():
    # Load your shapefiles using geopandas
    shapefile1 = gpd.read_file(SHAPEFILE_DIR + "electricity_rates_by_state_merged.shp")
    shapefile2 = gpd.read_file(SHAPEFILE_DIR + "US_elec.shp")

    # Convert shapefile data to GeoJSON
    geojson1 = shapefile1.to_json()
    geojson2 = shapefile2.to_json()

    # Create a JSON response
    response = {
        "shapefile1": geojson1,
        "shapefile2": geojson2
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)

