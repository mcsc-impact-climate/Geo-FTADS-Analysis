#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:56:00 2023

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

def prepare_electrolyzer_hubs(top_dir):
    
    df_data = pd.read_csv(f'{top_dir}/data/hydrogen_hubs/electrolyzers.csv')
    
    df_geodata = gpd.GeoDataFrame(df_data, geometry=gpd.points_from_xy(df_data.Longitude, df_data.Latitude), crs="EPSG:4326")
    
    df_geodata = df_geodata.filter(['Location', 'Power (kW)', 'Status', 'geometry'], axis=1).rename(columns={'Power (kW)': 'Power_kW'})
    
    return df_geodata
    
def 

def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the electrolyzer locations and information and conver the info to geodataframe
    df_electrolyzers = prepare_electrolyzer_hubs(top_dir)
    
    # Initialize a dictionary to contain geodataframes for hydrogen hubs
    dict_hydrohubs = {}
    
    # Populate the dictionary with sections of the highway that HD ZEV projects are planned on
    dict_hydrohubs['electrolyzer'] = prepare_electrolyzer_hubs(top_dir)
    
    # Save the shapefile for the East Coast HD ZEV corridor
    saveShapefile(dict_hydrohubs['electrolyzer'], f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer.shp')
    
        
main()
