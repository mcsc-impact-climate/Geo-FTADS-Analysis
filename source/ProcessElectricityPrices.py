#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 16 11:24:00 2023

@author: danikam
"""

# Import needed modules
import sys

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir, saveShapefile

def read_state_data(top_dir):
    '''
    Reads in the data file for state-level electricity prices
    
    Parameters
    ----------
    None

    Returns
    -------
    state_data (pd.DataFrame): A pandas dataframe containing the 2021 electricity rate data for each state
        
    NOTE: None.

    '''

    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/electricity_rates/sales_annual_a.xlsx'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'Total Electric Industry', skiprows=[0,1])
    
    # Select columns of interest, and the year 2021
    data_df = data_df[data_df['Year']==2021]
    
    # Column 1: State abbreviation
    # Column 9: Commercial electricity price (cents / kWh)
    data_df = data_df.iloc[:,[1,9]]
    
    # Rename the state header to match the shapefile
    data_df = data_df.rename(columns={'STATE': 'STUSPS'})

    return data_df
    
def read_zipcode_data(top_dir):
    '''
    Reads in the data file for zipcode-level electricity prices
    
    Parameters
    ----------
    None

    Returns
    -------
    zipcode_data (pd.DataFrame): A pandas dataframe containing the 2020 electricity rate data for each zipcode
        
    NOTE: None.

    '''
    # Read in the data from a csv
    data_df = pd.read_csv(f'{top_dir}/data/electricity_rates/iou_zipcodes_2020.csv')
    
    # Select the columns of interest
    data_df = data_df.filter(['zip', 'service_type', 'comm_rate'], axis=1)
    
    # Select entries with bundled service (rather than delivery-only)
    data_df = data_df[data_df['service_type'] == 'Bundled']
    
    # Can now remove the service_type column to save memory
    data_df = data_df.drop(['service_type'], axis=1)
    
    # Multiply the commercial electricity price by 100 to conver from $ to cents
    data_df['comm_rate'] = 100*data_df['comm_rate']
    
    # Rename the zipcode header to match the shapefile
    data_df = data_df.rename(columns={'zip': 'ZIP_CODE'})
    
    # Convert the zip code column from int to str to match the type in the shapefile
    data_df['ZIP_CODE'] = data_df['ZIP_CODE'].astype(str).apply(lambda x: x.zfill(5))
    
    return data_df
    
def read_demand_charge_data(top_dir):
    '''
    Reads in the data file for demand charges
    
    Parameters
    ----------
    None

    Returns
    -------
    state_data (pd.DataFrame): A pandas dataframe containing maximum demand charge data compiled by NREL in 2017
        
    NOTE: None.

    '''

    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/Demand_charge_rate_data.xlsm'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'Data')
    
    # Select columns of interest, and the year 2021
    data_df = data_df.filter(['Utility ID (EIA)', 'Maximum Demand Charge ($/kW)'], axis=1)
    
    # Rename the headers
    data_df = data_df.rename(columns={'Utility ID (EIA)': 'ID', 'Maximum Demand Charge ($/kW)': 'MaxDemCh'})
    
    # Convert the utility ID column from float to str to match the type in the shapefile
    data_df = data_df[~data_df['ID'].isna()]
    data_df['ID'] = data_df['ID'].astype(int).astype(str)
    
    # For each ID, get the maximum demand charge over all instances of the same utility ID
    data_df_unique_ID = pd.DataFrame(columns=['ID', 'MaxDemCh'])
    for ID in np.unique(data_df['ID']):
        max_demand_charge = np.max(data_df['MaxDemCh'][data_df['ID'] == ID])
        dict = {'ID': [ID], 'MaxDemCh': [max_demand_charge]}
        data_df_unique_ID = pd.concat([data_df_unique_ID, pd.DataFrame(dict)], ignore_index=True)

    return data_df_unique_ID
    
def merge_state_shapefile(data_df, shapefile_path):
    '''
    Merges the shapefile containing state boundaries with the dataframe containing the electricity prices by state

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the subregion names and emissions data for each subregion

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
    
def merge_zipcode_shapefile(data_df, shapefile_path):
    '''
    Merges the shapefile containing zipcode boundaries with the dataframe containing the electricity prices by zip code

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the subregion names and emissions data for each subregion

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path, include_fields = ['ZIP_CODE', 'geometry'])
        
    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on='ZIP_CODE', how='left')
    merged_dataframe = merged_dataframe[~merged_dataframe['comm_rate'].isna()]
            
    return merged_dataframe
    
def merge_demand_charge_shapefile(data_df, shapefile_path):
    '''
    Merges the shapefile containing zipcode boundaries with the dataframe containing the electricity prices by utility

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the subregion names and emissions data for each subregion

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path, include_fields = ['ID', 'geometry'])
    
    # Merge the dataframes based on the utility ID
    merged_dataframe = shapefile.merge(data_df, on='ID', how='left')
    
    # Ensure all demand charges are non-negative
    merged_dataframe = merged_dataframe[merged_dataframe['MaxDemCh'] >= 0]
            
    return merged_dataframe

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Read electricity price data for 2021 by state
    state_data = read_state_data(top_dir)
    
#    # Merge the electricity price data by state with the shapefile with state borders
#    merged_state_data = merge_state_shapefile(state_data, f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp')
#
#    # Save the merged shapefile
#    saveShapefile(merged_state_data, f'{top_dir}/data/electricity_rates_merged/electricity_rates_by_state_merged.shp')

#    # Read electricity price data for 2020 by zipcode
#    zipcode_data = read_zipcode_data(top_dir)
#
#    # Merge the electricity price data by zipcode with the shapefile with zipcode borders
#    merged_zipcode_data = merge_zipcode_shapefile(zipcode_data, f'{top_dir}/data/zip_code_regions/USA_ZIP_Code_Boundaries.shp')
#
#    # Save the merged shapefile
#    saveShapefile(merged_zipcode_data, f'{top_dir}/data/electricity_rates_merged/electricity_rates_by_zipcode_merged.shp')
 
    # Read maximum demand charge by utility ID
    demand_charge_data = read_demand_charge_data(top_dir)
 
    # Merge the demand charge data by utility with the shapefile with utility borders
    merged_demand_charge_data = merge_demand_charge_shapefile(demand_charge_data, f'{top_dir}/data/utility_boundaries/Electric_Retail_Service_Territories.shp')
    
    # Save the merged shapefile
    saveShapefile(merged_demand_charge_data, f'{top_dir}/data/electricity_rates_merged/demand_charges_merged.shp')

main()
