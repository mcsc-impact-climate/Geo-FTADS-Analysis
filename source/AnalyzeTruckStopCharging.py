"""
Created on Fri Sep 9 17:56:00 2023

@author: danikam
"""

import geopandas as gpd
from shapely.ops import nearest_points
from CommonTools import get_top_dir, saveShapefile

def filter_points_by_distance(points_gdf, highways_gdf, distance_threshold):
    '''
    Removes points that lie more than the given distance threshold away from a highway.

    Parameters
    ----------
    points_gdf (gpd.DataFrame): Geopandas dataframe containing the points of interest
    highways_gdf (gpd.DataFrame): Geopandas dataframe containing the highways
    distance_threshold (float): Maximum distance (in meters) that a point can be from a highway, beyond which it gets removed

    Returns
    -------
    filtered_points_gdf (gpd.DataFrame): Points of interest, with points more than the distance threshold from a highway removed

    NOTE: None
    '''
    # Buffer the highways by the given threshold to create a buffer around them
    buffered_highways = highways_gdf.buffer(distance_threshold)

    # Create a GeoDataFrame of the buffered highways
    buffered_highways_gdf = gpd.GeoDataFrame(geometry=buffered_highways, crs=highways_gdf.crs)

    # Iterate over each point
    filtered_points = []
    for idx, point in points_gdf.iterrows():
        # Check if the truck stop is within 100 meters of any buffered highway
        if buffered_highways_gdf.intersects(point['geometry']).any():
            filtered_points.append(point)

    # Create a GeoDataFrame from the filtered truck stops
    filtered_points_gdf = gpd.GeoDataFrame(filtered_points, crs=points_gdf.crs)

    return filtered_points_gdf


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read the shapefiles and ensure the CRS is a projected coordinate system to evaluate separation distances
    truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking.shp').to_crs("EPSG:3857")
    highways_gdf = gpd.read_file(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_interstate.shp').to_crs("EPSG:3857")

    truck_stops_filtered_gdf = filter_points_by_distance(points_gdf=truck_stops_gdf, highways_gdf=highways_gdf, distance_threshold=1000)

    # Save the points along interstates
    saveShapefile(truck_stops_filtered_gdf, f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate.shp')

    # 

main()