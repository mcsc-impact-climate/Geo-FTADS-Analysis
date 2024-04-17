#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 09:24:00 2023

@author: danikam
"""

# Import needed modules
import sys

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir, mergeShapefile, saveShapefile, state_names_to_abbr

LB_PER_KG = 2.20462

def read_ba_data(top_dir):
    '''
    Reads in grid emission intensities by balancing authorities from eGRIDS
    
    Parameters
    ----------
    None

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2022 eGrid data for each subregion (lb CO2 / MWh)
        
    NOTE: None.

    '''
    
    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/egrid2022_data.xlsx'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'SRL22', skiprows=[0])
    
    # Select the columns of interest
    # SUBRGN: eGRID sub-region acronym
    # SRCO2RTA: eGRID subregion annual CO2 emission rate (lb CO2 / MWh)
    data_df = data_df.filter(['SUBRGN', 'SRCO2RTA'], axis=1)#, 'SRCLPR', 'SROLPR', 'SRGSPR', 'SRNCPR', 'SRHYPR', 'SRBMPR', 'SRWIPR', 'SRSOPR', 'SRGTPR', 'SROFPR', 'SROPPR'], axis=1)
    
    # Rename SRCO2RTA in the merged dataframe to a more generic descriptor
    data_df = data_df.rename(columns={'SRCO2RTA': 'CO2_rate'})

    return data_df
    
def read_state_data(top_dir):
    '''
    Reads in grid emission intensities by state from EIA
    
    Parameters
    ----------
    None

    Returns
    -------
    eia_data (pd.DataFrame): A pandas dataframe containing the 2022 emission intensity data (lb CO2 / MWh)
        
    NOTE: None.

    '''
    
    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/emissions_region2022.xlsx'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'State', skiprows=[0])
    
    # Select the columns of interest
    data_df = data_df.filter(['Year', 'Census Division and State', 'Kilograms of CO2 per Megawatthour of Generation'], axis=1)
    
    # Rename the long columns
    data_df = data_df.rename(columns={'Census Division and State': 'STUSPS', 'Kilograms of CO2 per Megawatthour of Generation': 'CO2_rate'})
    
    # Convert the CO2 rate from kg / MWh to lb / MWh
    data_df['CO2_rate'] = data_df['CO2_rate'] * LB_PER_KG
    
    # Select rows corresponding to year 2022
    data_df = data_df[data_df['Year']==2022]
    
    # Update the state name to its associated abbreviation
    data_df = state_names_to_abbr(data_df, 'STUSPS')
    
    # Remove NaN rows that aren't associated with states
    data_df = data_df.dropna()
    
    return data_df

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Read in the grid CO2 intensity by balancing authority from eGRIDS
    egrid_data = read_ba_data(top_dir)

    # Read in the state-level CO2 intensity from EIA
    eia_data = read_state_data(top_dir)

    # Merge the eGrids data in with the shapefile with subregion borders
    merged_dataframe_egrid = mergeShapefile(egrid_data, f'{top_dir}/data/eGRID2021_subregions/eGRID2021 Subregions Shapefile final.shp', 'SUBRGN')
    
    # Merge the state-level CO2 intensity data with the state borders shapefile
    merged_dataframe_eia = mergeShapefile(eia_data, f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp', 'STUSPS')

    # Save the merged shapefiles
    saveShapefile(merged_dataframe_egrid, f'{top_dir}/data/egrid2022_subregions_merged/egrid2022_subregions_merged.shp')
    saveShapefile(merged_dataframe_eia, f'{top_dir}/data/eia2022_state_merged/eia2022_state_merged.shp')
    
main()
