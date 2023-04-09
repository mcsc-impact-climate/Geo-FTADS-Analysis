#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Apr 8 22:08:00

@author: danikam
"""

import os
import sys

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from pathlib import Path

import time

def mergeShapefile(dest, shapefile_path):
    '''
    Reads in the shapefile containing the highway links, and merges it with the highway flux assignments

    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing the highway links

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path, include_fields=['ID', 'LENGTH', 'DATA', 'VERSION', 'ShapeSTLen', 'geometry'])
    merged_dataframe = shapefile.merge(dest, on='ID', how='left')
    
    # Filter for links where the total tons transported (TOT Tons_22 All) isn't NULL
    merged_dataframe = merged_dataframe[(~(merged_dataframe['TOT Tons_22 All'].isna())) & (merged_dataframe['TOT Tons_22 All'] > 10000)]
    
    #print(merged_dataframe)
    
    return merged_dataframe
    
def saveShapefile(file, name):
    '''
    Saves a pandas dataframe as a shapefile

    Parameters
    ----------
    file (pd.DataFrame): Dataframe to be saved as a shapefile

    name (string): Filename to the shapefile save to (must end in .shp)

    Returns
    -------
    None
    '''
    # Make sure the filename ends in .shp
    if not name.endswith('.shp'):
        print("ERROR: Filename for shapefile must end in '.shp'. File will not be saved.")
        exit()
    # Make sure the full directory path to save to exists, otherwise create it
    dir = os.path.dirname(name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    file.to_file(name)

def get_top_dir():
    '''
    Gets the path to the top level of the git repo (one level up from the source directory)
        
    Parameters
    ----------
    None

    Returns
    -------
    top_dir (string): Path to the top level of the git repo
        
    NOTE: None
    '''
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    top_dir = os.path.dirname(source_dir)
    return top_dir
    
top_dir = get_top_dir()
    
def read_highway_assignments():
    '''
    Reads in the FAF5 highway assignments as a dataframe, and gets the columns of interest

    Parameters
    ----------
    None

    Returns
    -------
    highway_assignments_filtered_df (pd.DataFrame): Dataframe containing the highway link IDs and any other columns of interest
    '''
    
    highway_assignments_df = pd.read_csv(f'{top_dir}/data/FAF5_highway_assignment_results/FAF5_2022_Highway_Assignment_Results/CSV Format/FAF5 Total Truck Flows by Commodity_2022.csv')
    
    # Filter for the columns we're interested in
    highway_assignments_filtered_df = highway_assignments_df.filter(['ID', 'TOT Tons_22 All'], axis=1)
    
    return highway_assignments_filtered_df
    
def main():
    # Read in the highway flow assignments for each link
    df_highway_assignments = read_highway_assignments()
    #start_time = time.time()
    
    # Merge the highway flow assignments in with the shapefile containing the highway links
    merged_dataframe = mergeShapefile(df_highway_assignments, f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp')
    
    #print(f'Merging took {time.time() - start_time} seconds')
    
    # Save the merged shapefile
    saveShapefile(merged_dataframe, f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp')
        
main()
