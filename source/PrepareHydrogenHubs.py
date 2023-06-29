#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:56:00 2023

@author: danikam
"""

# Import needed modules
import sys
import math

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir, saveShapefile

def prepare_electrolyzer_hubs(top_dir):
    '''
    Reads in the csv file containing the locations, and capacities (kW) of proposed and installed electrolyzers and returns a geodataframe for the associated shapefile

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_geodata (pd.DataFrame): Geodataframe containing the electrolyzer capacities and geospatial data
    '''
    df_data = pd.read_csv(f'{top_dir}/data/hydrogen_hubs/electrolyzers.csv')
    
    df_geodata = gpd.GeoDataFrame(df_data, geometry=gpd.points_from_xy(df_data.Longitude, df_data.Latitude), crs="EPSG:4326")
    
    df_geodata = df_geodata.filter(['Location', 'Power (kW)', 'Status', 'geometry'], axis=1).rename(columns={'Power (kW)': 'Power_kW'})
    
    return df_geodata
    
def prepare_refinery_hubs(top_dir):
    '''
    Reads in the csv file containing the locations, and capacities (million standard cubic feet per day) of existing refineries that produce hydrogen as byproducts or via SMR and returns a geodataframe for the associated shapefile

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_geodata (pd.DataFrame): Geodataframe containing the hydrogen production capacities and geospatial data of the refineries
    '''
    df_data = pd.read_csv(f'{top_dir}/data/hydrogen_hubs/Hydrogen_Production_Facilities_Capacity.csv')
    
    df_geodata = gpd.GeoDataFrame(df_data, geometry=gpd.points_from_xy(df_data.Longitude, df_data.Latitude), crs="EPSG:4326")
    
    df_geodata = df_geodata.filter(['City', 'State', 'Capacity (million standard cubic feet per day)', 'Status', 'Process', 'geometry'], axis=1).rename(columns={'Capacity (million standard cubic feet per day)': 'Cap_MMSCFD'})
    
    # Remove the locations that haven't been assigned longitude/latitude coordinates
    df_geodata = df_geodata.dropna(subset=['Cap_MMSCFD'])
    
    return df_geodata

def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Initialize a dictionary to contain geodataframes for hydrogen hubs
    dict_hydrohubs = {}
    
    # Populate the dictionary with the refinery and electrolyzer hubs
    dict_hydrohubs['electrolyzer'] = prepare_electrolyzer_hubs(top_dir)
    dict_hydrohubs['refinery'] = prepare_refinery_hubs(top_dir)
    
    # Save the shapefile for the electrolyzer hubs
    saveShapefile(dict_hydrohubs['electrolyzer'], f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer.shp')
    saveShapefile(dict_hydrohubs['refinery'], f'{top_dir}/data/hydrogen_hubs/shapefiles/refinery.shp')
        
main()
