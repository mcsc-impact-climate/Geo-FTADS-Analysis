#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 4 22:50:00 2023

@author: danikam
"""

# Import needed modules
import sys

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir, mergeShapefile, saveShapefile

def readData_ba(top_dir):
    '''
    Reads in the data file for the electricity demand data
    
    Parameters
    ----------
    None

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2022 electricity demand data for each balancing authority region
        
    NOTE: None.

    '''
    
    # Read in the data associated with each eGrids subregion
    dataPath_Jan_Jun = f'{top_dir}/data/power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jan_Jun.csv'
    dataPath_Jul_Dec = f'{top_dir}/data/power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jul_Dec.csv'
    data_df_Jan_Jun = pd.read_csv(dataPath_Jan_Jun, usecols = ['Balancing Authority', 'Demand (MW)'])
    data_df_Jul_Dec = pd.read_csv(dataPath_Jul_Dec, usecols = ['Balancing Authority', 'Demand (MW)'])
    data_df = pd.concat([data_df_Jan_Jun, data_df_Jul_Dec])
    data_df['Demand (MW)'] = data_df['Demand (MW)'].str.replace(',','').astype('float')
    data_df = data_df[(~data_df['Demand (MW)'].isna())&(data_df['Demand (MW)'] >= 0)]
    
    balancing_authorities = np.unique(data_df['Balancing Authority'])
    
    data_to_save_df = pd.DataFrame(columns=['ABBRV', 'MaxDem', 'AvgDem'])
    for ba in balancing_authorities:
        max_demand = np.max(data_df[data_df['Balancing Authority'] == ba]['Demand (MW)'])
        #min_demand = np.min(data_df[data_df['Balancing Authority'] == ba]['Demand (MW)'])
        avg_demand = np.mean(data_df[data_df['Balancing Authority'] == ba]['Demand (MW)'])
        new_row = pd.DataFrame({'ABBRV': [ba], 'MaxDem': [max_demand], 'AvgDem': [avg_demand]})
        data_to_save_df = pd.concat([data_to_save_df, new_row])

    return data_to_save_df
    
def readData_state(top_dir):
    '''
    Reads in the data file for the electricity demand data by state
    
    Parameters
    ----------
    None

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2022 electricity demand data for each balancing authority region
        
    NOTE: None.

    '''
    
    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/existcapacity_annual.xlsx'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'Existing Capacity', skiprows=[0])
    data_df_2021_total = data_df[(data_df['Year']==2021)&(data_df['Producer Type'] == 'Total Electric Power Industry')&(data_df['Fuel Source'] == 'All Sources')]
    
    data_df_2021_total = data_df_2021_total.drop(columns=['Fuel Source', 'Generators', 'Facilities', 'Nameplate Capacity (Megawatts)', 'Producer Type'])
    
    data_df_2021_total = data_df_2021_total.rename(columns={'State Code': 'STUSPS', 'Summer Capacity (Megawatts)': 'Capacity'})
    data_df_2021_total['Capacity'] = data_df_2021_total['Capacity'].astype('float')
        
    return data_df_2021_total
    
def merge_shapefile_ba(data_df, shapefile_path):
    '''
    Merges the shapefile containing balancing authority boundaries with the dataframe containing the electricity demand

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the balancing authority names, along with max and mean demand

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path)
    shapefile = shapefile.filter(['ABBRV', 'Shape_Area', 'geometry'], axis=1)

    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on='ABBRV', how='left')
    
    merged_dataframe = merged_dataframe[~merged_dataframe['MaxDem'].isna()]
    
    return merged_dataframe
    
def merge_shapefile_state(data_df, shapefile_path):
    '''
    Merges the shapefile containing state boundaries with the dataframe containing the electricity demand

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the state names, along with summer capacity

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path)
    shapefile = shapefile.filter(['STUSPS', 'Shape_Area', 'geometry'], axis=1)
    
    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on='STUSPS', how='left')
                
    return merged_dataframe

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Read in the demand data by balancing authority and by state
    #demand_data_by_ba = readData_ba(top_dir)
    demand_data_by_state = readData_state(top_dir)
    
    # Merge the electricity demand data with the balancing authority and state shapefiles
    #merged_demand_data_by_ba = merge_shapefile_ba(demand_data_by_ba, f'{top_dir}/data/balancing_authority_boundaries/Planning_Areas.shp')
    merged_demand_data_by_state = merge_shapefile_state(demand_data_by_state, f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp')
    
    # Save the merged shapefiles
    #saveShapefile(merged_demand_data_by_ba, f'{top_dir}/data/electricity_demand_merged/electricity_demand_merged_by_ba.shp')
    saveShapefile(merged_demand_data_by_state, f'{top_dir}/data/electricity_demand_merged/electricity_demand_merged_by_state.shp')
    
main()
