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

METERS_PER_MILE = 1609.34
LB_PER_TON = 2000.
KWH_PER_MWH = 1000.
TONS_PER_KILOTON = 1000.
DAYS_PER_YEAR = 365.

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
    
def make_charger_circles(charger_locations_gdf, radius):
    '''
    Reads in a longitude and latitude, and makes a shapefile object representing a circle of the given radius.
    
    Parameters
    ----------
    center_long (double): Longitude of the center of the circle
    center_lat (double): Latitude of the center of the circle
    radius (double): Radius of the circle (in miles)

    Returns
    -------
    gpd_circle (gpd.DataFrame): Geodataframe with the boundary of a circle centered at (center_long, center_lat) with the given radius.
    '''
    # Convert the given radius to meters
    radius_meters = radius * METERS_PER_MILE
    
    # Convert to projected coordinate system to evaluate a circle of a given radius around the central coordinates
    charger_locations_gdf = charger_locations_gdf.to_crs("EPSG:3857")
    
    charger_circles_gdf = gpd.GeoDataFrame(charger_locations_gdf.buffer(radius_meters), columns=['geometry'])
    
    # Add the info about the nearest center to associate charger circles with charging locations
    charger_circles_gdf['Nearest Center'] = charger_locations_gdf['Nearest Center']

    # Convert back to the geographic coordinate system
    return charger_circles_gdf.to_crs("EPSG:4326")
    
def get_scaled_highway_links_in_circles(charger_circles_gdf, texas_highways_gdf):
    
    # Manually keep the original index from texas_highways_gdf in a new column to retain it through the join
    texas_highways_gdf['original_index'] = texas_highways_gdf.index

    # Perform spatial join
    overlapping_links = gpd.sjoin(texas_highways_gdf, charger_circles_gdf, how="inner", predicate='intersects')
    
    # Drop duplicates to get unique highway links
    unique_highways = overlapping_links.drop_duplicates(subset='original_index')
    
    # Retrieve only the original highway data that overlaps at least one circle using the preserved index
    filtered_highways_gdf = texas_highways_gdf.loc[unique_highways['original_index']]

    # Count overlaps by original index
    overlap_count = overlapping_links.groupby('original_index').size()
    filtered_highways_gdf = filtered_highways_gdf.join(overlap_count.rename('overlap_count'), how='left')

    # Scale Tot Tons and Tot Trips based on the count of overlaps
    filtered_highways_gdf['Tot Tons'] /= filtered_highways_gdf['overlap_count']
    filtered_highways_gdf['Tot Trips'] /= filtered_highways_gdf['overlap_count']

    # Clean up by removing the temporary index column
    filtered_highways_gdf.drop(columns=['original_index'], inplace=True)

    return filtered_highways_gdf
    
def evaluate_average_payload(highway_data_gdf):
    '''
    Evaluates the average payload carried per trip, in tons

    Parameters
    ----------
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe read in, with an additional column containing the average payload per trip (in lb)
    '''
    
    # Convert 'Tot Tons' from kilotons/year to tons/day
    tons_per_day = highway_data_gdf['Tot Tons'] * TONS_PER_KILOTON / DAYS_PER_YEAR
    
    trips_per_day = highway_data_gdf['Tot Trips']
    
    highway_data_gdf['Av Payload'] = (tons_per_day / trips_per_day) * LB_PER_TON
    
    return highway_data_gdf
    
def evaluate_average_mileage(top_dir, highway_data_gdf):
    '''
    Evaluates the average mileage per trip for each link based on the average payload carried.
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe read in, with an additional column containing the mileage
    
    NOTE: The assessment of mileage uses a linear fit of mileage vs. payload evaluated using NACFE pilot data from the Tesla Semi. The code used to evaluate this best fit line can be found in the following repo: https://github.com/mcsc-impact-climate/PepsiCo_NACFE_Analysis
    '''
    # Read in the linear parameters for the linear approximation of mileage vs. payload
    linear_params = pd.read_csv(f'{top_dir}/data/payload_vs_mileage_best_fit_params.csv')
    
    payloads = highway_data_gdf['Av Payload']
    slope = float(linear_params['slope (kWh/lb-mi)'])
    intercept = float(linear_params['b (kWh/mi)'])
    
    highway_data_gdf['Av Mileage'] = slope * payloads + intercept
    
    return highway_data_gdf
    
def evaluate_annual_e_demand_link(top_dir, highway_data_gdf, charging_efficiency=0.92):
    '''
    Evaluates the annual energy demand associated with trucks traveling over each highway link
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe containing the info for each link
    charging_efficiency (float): Efficiency with which power taken from the grid is converted into battery power

    Returns
    -------
    highway_data_gdf (GeoPandas DataFrame): Pandas dataframe read in, with an additional column containing the annual energy demand
    '''
    
    # Convert truck trips per day to trips per year
    trips_per_year = highway_data_gdf['Tot Trips'] * DAYS_PER_YEAR
    
    highway_data_gdf['An E Dem'] = ( highway_data_gdf['Av Mileage'] * highway_data_gdf['len_miles'] * trips_per_year / KWH_PER_MWH ) / charging_efficiency
    
    return highway_data_gdf
    
def evaluate_annual_e_demand_link(top_dir, highway_data_gdf, charging_efficiency=0.92):
    '''
    Evaluates the annual energy demand associated with trucks traveling over each highway link
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_gdf (Pandas DataFrame): Pandas dataframe containing the info for each link
    charging_efficiency (float): Efficiency with which power taken from the grid is converted into battery power

    Returns
    -------
    highway_data_gdf (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the annual energy demand
    '''
    
    # Convert truck trips per day to trips per year
    trips_per_year = highway_data_gdf['Tot Trips'] * DAYS_PER_YEAR
    
    highway_data_gdf['An E Dem'] = ( highway_data_gdf['Av Mileage'] * highway_data_gdf['len_miles'] * trips_per_year / KWH_PER_MWH ) / charging_efficiency
    
    return highway_data_gdf
    
def evaluate_annual_e_demand_charger(filtered_highways_gdf, charger_circles_gdf, charger_locations_gdf):
    '''
    Aggregates the annual energy demand for all highway links in the circle around each charger to evaluate the total annual energy demand on the charger if all highway links within its circle get electrified
    
    Parameters
    ----------
    filtered_highways_gdf (GeoPandas DataFrame): Pandas geodataframe containing the info for each link falling within the circle of at least one charger
    charger_circles_gdf (GeoPandas DataFrame): Pandas geodataframe containing the circles around each charger
    charger_locations_gdf (GeoPandas DataFrame): Pandas geodataframe containing the charger locations

    Returns
    -------
    highway_data_gdf (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the annual energy demand
    '''
        
    # Join highways to circles based on geometry, thereby linking highways to nearest centers
    joined_gdf = gpd.sjoin(filtered_highways_gdf, charger_circles_gdf, how='left', predicate='intersects')
    
    # Sum up 'An E Dem' for each 'Nearest Center'
    aggregated_data = joined_gdf.groupby('Nearest Center')['An E Dem'].sum().reset_index()
    
    # Add the summed 'An E Dem' values to the respective charger locations
    charger_locations_gdf = charger_locations_gdf.merge(aggregated_data, on='Nearest Center', how='left')
    
    # Fill any NaNs with 0 if any location did not have any overlapping highways
    charger_locations_gdf['An E Dem'] = charger_locations_gdf['An E Dem'].fillna(0)
        
    return charger_locations_gdf
    
def visualize_chargers(top_dir, charger_locations_gdf, texas_boundary_gdf, texas_highways_gdf, charger_circles_gdf, filtered_highways_gdf=None):
    # Set up the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot texas_highways_gdf first, with texas_boundary_gdf above it, and charger_locations_gdf on top
    texas_highways_gdf['line_width'] = texas_highways_gdf['Tot Tons'] / texas_highways_gdf['Tot Tons'].max() * 9.5 + 0.5
    size_scale = 150 / (charger_locations_gdf['An E Dem'].max() - charger_locations_gdf['An E Dem'].min())
    charger_locations_gdf['scaled_size'] = 10 + (charger_locations_gdf['An E Dem'] - charger_locations_gdf['An E Dem'].min()) * size_scale

    texas_highways_gdf.plot(ax=ax, color='black', linewidth=texas_highways_gdf['line_width'], label='Highways', zorder=1)  # Highways
    if not filtered_highways_gdf is None:
        filtered_highways_gdf['line_width'] = filtered_highways_gdf['Tot Tons'] / texas_highways_gdf['Tot Tons'].max() * 9.5 + 0.5
        filtered_highways_gdf.plot(ax=ax, color='red', linewidth=filtered_highways_gdf['line_width'], label='Highways', zorder=2)  # Highways overlapping with circles
    texas_boundary_gdf.plot(ax=ax, color='blue', edgecolor='blue', alpha=0.5, linewidth=1, label='Texas Boundary', zorder=3)  # Boundary
    charger_locations_gdf.plot(ax=ax, marker='o', color='red', markersize=charger_locations_gdf['scaled_size'], label='Annual electricity demand (MWh)', zorder=4)  # Chargers
    charger_circles_gdf.plot(ax=ax, color='red', edgecolor='red', alpha=0.2, linewidth=2, label='Charger Coverage', zorder=5)  # Circles

    # Add labels and title
    ax.set_title('Map of Texas with Charger Locations', fontsize=24)

    # Remove x and y axis ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Add a legend
    ax.legend(fontsize=18)

    # Show the plot
    plt.savefig(f'{top_dir}/plots/Texas_charger_locations.png')
    plt.savefig(f'{top_dir}/plots/Texas_charger_locations.pdf')
    
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
      
    # Evaluate circles around each charger of the given radius to contain highway links contributing to the charger's annual energy demand
    charger_circles_gdf = make_charger_circles(charger_locations_gdf, radius=100)

    # Filter the highways to consider only those overlapping with at least one circle. For links with more than one overlapping circle, the freight flow rate is scaled down by the number of overlapping circles to avoid double counting contributions of their associated energy demand to nearby chargers.
    filtered_highways_gdf = get_scaled_highway_links_in_circles(charger_circles_gdf, texas_highways_gdf)
    
    # Evaluate the average payload carried per trip for each link
    filtered_highways_gdf = evaluate_average_payload(filtered_highways_gdf)
    
    # Evaluate the average truck mileage per trip (in kWh/mile) based on the payload (calibrated to the Tesla Semi)
    filtered_highways_gdf = evaluate_average_mileage(top_dir, filtered_highways_gdf)
    
    # Evaluate the annual energy demand associated with trucks passing over each link if they're all electrified
    filtered_highways_gdf = evaluate_annual_e_demand_link(top_dir, filtered_highways_gdf)
    
    # Add up the total annual energy demand associated with fully electrifying highway links in the vicinity of each charger
    charger_locations_gdf = evaluate_annual_e_demand_charger(filtered_highways_gdf, charger_circles_gdf, charger_locations_gdf)

    # Plot the state boundary, charger locations and highways together
    visualize_chargers(top_dir, charger_locations_gdf, texas_boundary_gdf, texas_highways_gdf, charger_circles_gdf)

main()
    
