#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu Apr 18 15:15:00 2024

@author: danikam
"""

import numpy as np
import pandas as pd

import geopandas as gpd
from CommonTools import get_top_dir, mergeShapefile, saveShapefile

LB_PER_TON = 2000.
KWH_PER_MWH = 1000.
TONS_PER_KILOTON = 1000.
DAYS_PER_YEAR = 365.

def save_links_without_geo(top_dir):
    '''
    Reads in the FAF5 highway links with freight flow and state data, and removes the geometry data to make the file smaller and easier to work with, and saves them to a csv file

    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository

    Returns
    -------
    file_save_path (string): Path that the file gets saved to
    '''
    
    # Read in the merged shapefile for highway links with state and freight flow data
    highway_links_gdf = gpd.read_file(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin.shp')
    
    # Drop the geometry column
    highway_links_df = highway_links_gdf.drop(columns=['geometry'])
    
    # Save to a csv file
    file_save_path = f'{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin_nogeo.csv'
    highway_links_df.to_csv(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin_nogeo.csv')
    
    return file_save_path
    
def evaluate_average_payload(highway_data_df):
    '''
    Evaluates the average payload carried per trip, in tons

    Parameters
    ----------
    highway_data_df (Pandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_df (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the average payload per trip (in lb)
    '''
    
    # Convert 'Tot Tons' from kilotons/year to tons/day
    tons_per_day = highway_data_df['Tot Tons'] * TONS_PER_KILOTON / DAYS_PER_YEAR
    
    trips_per_day = highway_data_df['Tot Trips']
    
    highway_data_df['Av Payload'] = (tons_per_day / trips_per_day) * LB_PER_TON
    
    return highway_data_df
    
def evaluate_average_mileage(top_dir, highway_data_df):
    '''
    Evaluates the average mileage per trip for each link based on the average payload carried.
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_df (Pandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_df (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the mileage
    
    NOTE: The assessment of mileage uses a linear fit of mileage vs. payload evaluated using NACFE pilot data from the Tesla Semi. The code used to evaluate this best fit line can be found in the following repo: https://github.com/mcsc-impact-climate/PepsiCo_NACFE_Analysis
    '''
    # Read in the linear parameters for the linear approximation of mileage vs. payload
    linear_params = pd.read_csv(f'{top_dir}/data/payload_vs_mileage_best_fit_params.csv')
    
    payloads = highway_data_df['Av Payload']
    slope = float(linear_params['slope (kWh/lb-mi)'])
    intercept = float(linear_params['b (kWh/mi)'])
    
    highway_data_df['Av Mileage'] = slope * payloads + intercept
    
    return highway_data_df
    
def evaluate_annual_e_demand_link(top_dir, highway_data_df, charging_efficiency=0.92):
    '''
    Evaluates the annual energy demand associated with trucks traveling over each highway link
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_df (Pandas DataFrame): Pandas dataframe containing the info for each link
    charging_efficiency (float): Efficiency with which power taken from the grid is converted into battery power

    Returns
    -------
    highway_data_df (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the annual energy demand
    '''
    
    # Convert truck trips per day to trips per year
    trips_per_year = highway_data_df['Tot Trips'] * DAYS_PER_YEAR
    
    highway_data_df['An E Dem'] = ( highway_data_df['Av Mileage'] * highway_data_df['len_miles'] * trips_per_year / KWH_PER_MWH ) / charging_efficiency
    
    return highway_data_df
    
def evaluate_annual_e_demand_state(highway_data_df):
    '''
    Aggregates the annual energy demand for all highway links in each state to evaluate the total annual energy demand associated with operating an EV for each state
    
    Parameters
    ----------
    highway_data_df (Pandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_df (Pandas DataFrame): Pandas dataframe read in, with an additional column containing the annual energy demand
    '''
    
    state_sum_df = highway_data_df.groupby('state')['An E Dem'].sum().reset_index()
    
    # Convert the state column name to STUSPS to match the state border file
    state_sum_df = state_sum_df.rename(columns={'state': 'STUSPS'})
    
    # Drop Hawaii because it essentially has no highways
    state_sum_df = state_sum_df[state_sum_df['STUSPS'] != 'HI']
    
    return state_sum_df
    
def add_gen_cap_ratios(top_dir, state_data_df):
    '''
    Adds in ratios of energy demand for electrified trucking to:
        - total annual electricity generated (Ann_Gen column)
        - total theoretical annual electricity generating capacity (based on net summer capacity) (Ann_Cap column)
        - difference between theoretical maximum electricity generating capacity and annual electricity generated (Ann_Diff column)
    
    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    highway_data_df (Pandas DataFrame): Pandas dataframe containing the info for each link

    Returns
    -------
    highway_data_df (Pandas DataFrame): Pandas dataframe read in, with additional columns containing the ratios
    '''
    
    # Read in the dataframe containing annual electricity generated and theoretical max generating capacity for each state
    gen_cap_data_df = gpd.read_file(f'{top_dir}/data/eia2022_state_merged/gen_cap_2022_state_merged.shp', include_fields=['STUSPS', 'Ann_Gen', 'Ann_Cap', 'Ann_Diff'])
    
    # Drop the geometry info
    gen_cap_data_df = gen_cap_data_df.drop(columns=['geometry'])
    
    state_data_df = state_data_df.merge(gen_cap_data_df, on='STUSPS', how='left').dropna()
    
    # Evaluate the ratios of interest
    state_data_df['Perc Gen'] = 100*state_data_df['An E Dem'] / state_data_df['Ann_Gen']
    state_data_df['Perc Cap'] = 100*state_data_df['An E Dem'] / state_data_df['Ann_Cap']
    state_data_df['Perc Diff'] = 100*state_data_df['An E Dem'] / state_data_df['Ann_Diff']
    
    return state_data_df

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Save the highway links without geometry info to a csv file (can comment this out if the file has already been produced)
    #path_to_hw_info = save_links_without_geo(top_dir)
    
    # Open the highway link data without geometry info
    highway_data_df = pd.read_csv(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_nomin_nogeo.csv')
    
    # Evaluate the average payload carried per trip for each link
    highway_data_df = evaluate_average_payload(highway_data_df)
    
    # Evaluate the average truck mileage per trip (in kWh/mile) based on the payload (calibrated to the Tesla Semi)
    highway_data_df = evaluate_average_mileage(top_dir, highway_data_df)
    
    # Evaluate the annual energy demand per link
    highway_data_df = evaluate_annual_e_demand_link(top_dir, highway_data_df)
    
    # Evaluate the aggregated annual energy demand per state
    state_data_df = evaluate_annual_e_demand_state(highway_data_df)
    
    # Add in ratios of annual energy demand to annual electricity generated and theoretical maximum generating capacity
    state_data_df = add_gen_cap_ratios(top_dir, state_data_df)
    
    # Merge the aggregated annual energy demand per state with the state borders
    merged_state_data_gdf = mergeShapefile(state_data_df, f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp', 'STUSPS').dropna()
        
    # Save the merged shapefile
    saveShapefile(merged_state_data_gdf, f'{top_dir}/data/trucking_energy_demand/trucking_energy_demand.shp')

main()
