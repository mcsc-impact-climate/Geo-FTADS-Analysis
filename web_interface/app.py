from flask import Flask, jsonify, render_template, send_file
import geopandas as gpd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_shapefile_data')
def get_shapefile_data():
    shapefile_path = 'electricity_rates_by_state_merged.shp'
    try:
        # Read the Shapefile
        gdf = gpd.read_file(shapefile_path)
        gdf = gdf.to_crs({'init': 'epsg:4326'})  # Replace 'epsg:4326' with your desired CRS
        
        # Create a temporary GeoJSON file
        temp_geojson_file = 'temp.geojson'
        gdf.to_file(temp_geojson_file, driver='GeoJSON')
        
        # Return the temporary GeoJSON file to the client for download
        return send_file(temp_geojson_file, as_attachment=True, download_name='shapefile.geojson')
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
