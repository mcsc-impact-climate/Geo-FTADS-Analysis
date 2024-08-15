import os
import geopandas as gpd

# Define the directory where your GeoJSON files are located
directory = "geojsons_simplified"

# Get a list of all files in the directory
file_list = os.listdir(directory)

# Filter the list to only include GeoJSON files (optional, if needed)
geojson_files = [file for file in file_list if file.endswith(".geojson")]

# Loop through each GeoJSON file and print column attributes
for geojson_file in geojson_files:
    # Construct the full path to the GeoJSON file
    file_path = os.path.join(directory, geojson_file)

    # Read the GeoJSON file using geopandas
    gdf = gpd.read_file(file_path)

    # Print the available column attributes
    print(f"Columns in {geojson_file}:")
    print(gdf.columns)
    print("\n")
