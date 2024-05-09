#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed May 8 15:43:00 2024

@author: danikam
"""

import numpy as np
import pandas as pd
import os

import geopandas as gpd
from shapely.geometry import Point
from CommonTools import get_top_dir, mergeShapefile, saveShapefile

import matplotlib.pyplot as plt

def get_charger_locations(csv_path, charger_location_geojson_path):
    '''
    Reads in a csv file containing the locations of 8 chargers in the Texas Triangle optimized by the Jacquillat model, converts them to geopandas format, and saves them to a geojson

    Parameters
    ----------
    csv_path (string): Path to the csv file containing the charger locations
    charger_location_geojson_path (string): Geojson file path to save the charger locations to

    Returns
    -------
    charger_locations_gpd (string): Path that the file gets saved to
    '''
    
    # Read in the csv file with charger locations
    charger_locations_df = pd.read_csv(csv_path)
    
    # Convert the Latitude and Longitude to a Shapely Point() object
    charger_locations_df['geometry'] = [Point(xy) for xy in zip(charger_locations_df.Longitude, charger_locations_df.Latitude)]
    
    # Convert DataFrame to GeoDataFrame
    charger_locations_gdf = gpd.GeoDataFrame(charger_locations_df, geometry='geometry')
    
    # Save to a geojson and return
    charger_locations_gdf.to_file(charger_location_geojson_path)
        
    return charger_locations_gdf
    
def get_texas_boundary(state_boundaries_path, state_boundaries_geojson_path):
    '''
    Reads in the state boundaries for all us states, and returns the one for Texas

    Parameters
    ----------
    state_boundaries_path (string): Path to the shapefile containing US state boundaries
    state_boundaries_geojson_path (string): Geojson file path to save the Texas state boundary to

    Returns
    -------
    charger_locations_gpd (string): Path that the file gets saved to
    '''

    # Read in the boundaries for all us states
    state_boundaries_gdf = gpd.read_file(state_boundaries_path)
    
    # Select only the Texas state boundary
    texas_boundary_gdf = state_boundaries_gdf[state_boundaries_gdf['STUSPS'] == 'TX']
    
    # Drop columns we're not interested in
    texas_boundary_gdf = texas_boundary_gdf[['Shape_Leng', 'Shape_Area', 'geometry']]
    
    # Ensure the file is in the geographic coordinate system
    texas_boundary_gdf = texas_boundary_gdf.to_crs("EPSG:4326")
    
    # Save to a geojson and return
    texas_boundary_gdf.to_file(state_boundaries_geojson_path)
    
    return texas_boundary_gdf
    
def get_texas_highways(us_highways_path, texas_highways_geojson_path):
    '''
    Reads in the state highways for all U states, and returns the ones in Texas

    Parameters
    ----------
    us_highways_path (string): Path to the shapefile containing US highways
    texas_highways_geojson_path (string): Geojson file path to save the Texas highways to

    Returns
    -------
    texas_highways_gdf (string): Path that the file gets saved to
    '''
    us_highways_gdf = gpd.read_file(us_highways_path)
    texas_highways_gdf = us_highways_gdf[us_highways_gdf['state'] == 'TX']
    
    # Ensure the file is in the geographic coordinate system
    texas_highways_gdf = texas_highways_gdf.to_crs("EPSG:4326")
    
    # Save to a geojson and return
    texas_highways_gdf.to_file(texas_highways_geojson_path)
    
    return texas_highways_gdf
    
def visualize_chargers(top_dir, charger_locations_gdf, texas_boundary_gdf, texas_highways_gdf):
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot texas_highways_gdf first, with texas_boundary_gdf above it, and charger_locations_gdf on top
    texas_highways_gdf.plot(ax=ax, color='black', linewidth=1, label='Highways', zorder=1)  # Roads
    texas_boundary_gdf.plot(ax=ax, edgecolor='blue', alpha=0.5, linewidth=1, label='Texas Boundary', zorder=2)  # Boundary
    charger_locations_gdf.plot(ax=ax, marker='o', color='red', markersize=30, label='Charger Locations', zorder=3)  # Chargers

    # Add labels and title
    ax.set_title('Map of Texas with Charger Locations', fontsize=24)
    ax.set_xlabel('Longitude', fontsize=20)
    ax.set_ylabel('Latitude', fontsize=20)

    # Remove x and y axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add a legend
    ax.legend(fontsize=18)

    # Show the plot
    plt.savefig(f'{top_dir}/plots/Texas_charger_locations.png')
    
def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Get charger locations, state boundary, and highways for Texas (only run in if the geojsons don't already exist)
    charger_location_path = f'{top_dir}/data/Jacquillat_Charger_Locations.csv'
    charger_location_geojson_path = f'{top_dir}/geojsons/TT_charger_locations.json'
    
    state_boundaries_path = f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp'
    state_boundaries_geojson_path = f'{top_dir}/geojsons/texas_state_boundary.json'
    
    us_highways_path = f'{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin.shp'
    texas_highways_geojson_path = f'{top_dir}/geojsons/texas_state_highways.json'
        
    if os.path.exists(charger_location_geojson_path):
        charger_locations_gdf = gpd.read_file(charger_location_geojson_path)
    else:
        charger_locations_gdf = get_charger_locations(charger_location_path, charger_location_geojson_path)

    if os.path.exists(state_boundaries_geojson_path):
        texas_boundary_gdf = gpd.read_file(state_boundaries_geojson_path)
    else:
        texas_boundary_gdf = get_texas_boundary(state_boundaries_path, state_boundaries_geojson_path)

    if os.path.exists(texas_highways_geojson_path):
        texas_highways_gdf = gpd.read_file(texas_highways_geojson_path)
    else:
        texas_highways_gdf = get_texas_highways(us_highways_path, texas_highways_geojson_path)

    # Plot the state boundary, charger locations and highways together
    visualize_chargers(top_dir, charger_locations_gdf, texas_boundary_gdf, texas_highways_gdf)

main()
    
