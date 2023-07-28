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
from CommonTools import get_top_dir

import time

def mergeShapefile(dest, shapefile_path, min_tonnage = 10000):
    '''
    Reads in the shapefile containing the highway links, and merges it with the highway flux assignments

    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing the highway links

    shapefile_path (string): Path to the shapefile to be joined with the dataframe
    
    min_tonnage (float): Minimum annual tons per link required to save the link to the output shapefile

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    
    shapefile = gpd.read_file(shapefile_path, include_fields=['ID', 'LENGTH', 'DATA', 'VERSION', 'ShapeSTLen', 'geometry'])
    merged_dataframe = shapefile.merge(dest, on='ID', how='left')
    
#    # Convert to tons per mile
#    merged_dataframe['TOT Tons_22 All'] = merged_dataframe['TOT Tons_22 All'] / merged_dataframe['ShapeSTLen']
    
    # Filter for links where the total tons transported (TOT Tons_22 All) isn't NULL and is greater than 10,000
    merged_dataframe = merged_dataframe[(~(merged_dataframe['Tot Tons'].isna())) & (merged_dataframe['Tot Tons'] > min_tonnage)]
    
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
    
def read_highway_assignments(top_dir, unit_type='All'):
    '''
    Reads in the FAF5 highway assignments as a dataframe, and gets the columns of interest

    Parameters
    ----------
    top_dir (string): Path to top-level directory of the repository
    unit_type (string): Type of truck unit. SU: Single unit. CU: Combined unit.

    Returns
    -------
    highway_assignments_filtered_df (pd.DataFrame): Dataframe containing the highway link IDs and any other columns of interest
    '''
    
    highway_assignment_modifier = ''
    if unit_type == 'SU':
        highway_assignment_modifier = 'SU '
    elif unit_type == 'CU':
        highway_assignment_modifier = 'CU '
    
    highway_assignments_df = pd.read_csv(f'{top_dir}/data/FAF5_highway_assignment_results/FAF5_2022_Highway_Assignment_Results/CSV Format/FAF5 Total {highway_assignment_modifier}Truck Flows by Commodity_2022.csv')
    
    # Filter for the columns we're interested in
    highway_assignments_filtered_df = highway_assignments_df.filter(['ID', f'TOT Tons_22 {unit_type}'], axis=1)
    highway_assignments_filtered_df = highway_assignments_filtered_df.rename(columns={f'TOT Tons_22 {unit_type}': 'Tot Tons'})
    
    return highway_assignments_filtered_df
    
def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the highway flow assignments for each link
    df_highway_assignments_all = read_highway_assignments(top_dir, unit_type='All')
    df_highway_assignments_su = read_highway_assignments(top_dir, unit_type='SU')
    df_highway_assignments_cu = read_highway_assignments(top_dir, unit_type='CU')
    #start_time = time.time()
    
    # Merge the highway flow assignments in with the shapefile containing the highway links
    merged_dataframe_all = mergeShapefile(df_highway_assignments_all, f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp')
    merged_dataframe_su = mergeShapefile(df_highway_assignments_su, f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp')
    merged_dataframe_cu = mergeShapefile(df_highway_assignments_cu, f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp')
    
    #print(f'Merging took {time.time() - start_time} seconds')
    
    # Save the merged shapefile
    saveShapefile(merged_dataframe_all, f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp')
    saveShapefile(merged_dataframe_su, f'{top_dir}/data/highway_assignment_links/highway_assignment_links_single_unit.shp')
    saveShapefile(merged_dataframe_cu, f'{top_dir}/data/highway_assignment_links/highway_assignment_links_combined_unit.shp')
    
        
main()
