#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 14:44:00 2023

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
    
def get_highway_corridor(df_roads, df_states, highway_name, in_states):
    '''
    Reads in the roads and states shapefiles and filters for the East Coast I-95 HD ZEV corridor between Georgia and New Jersey

    Parameters
    ----------
    df_shapefile (pd.DataFrame): A pandas dataframe containing the shapefile info

    df_roads (string): Name of the column to be filtered on

    Returns
    -------
        df_highway (pd.DataFrame): Filtered shapefile
    '''

    # Filter for the highway of interest
    df_highway = df_roads[df_roads['FULLNAME'] == highway_name]
    
    # Filter for the highway in the specified states
    bool_in_states = (df_states['STUSPS'] == in_states[0])
    for state in in_states[1:]:
        bool_in_states = bool_in_states | (df_states['STUSPS'] == state)
    
    # Select the boundaries for the states of interest
    df_in_states = df_states[bool_in_states]
    
    # Convert the state boundaries to EPSG:4269 to match the roads shapefile
    df_in_states = df_in_states.to_crs(4269)
    
    # Get the spatial join of the highway and the states we want it to pass through
    df_highway = gpd.sjoin(df_highway, df_in_states)
    
    return df_highway
    
def get_longs(frame):
    xy = frame.geometry.xy
    return np.asarray(xy[0])
    
def get_lats(frame):
    xy = frame.geometry.xy
    return np.asarray(xy[1])
    
def get_H2LA_corridor(df_roads, df_states):
    '''
    Reads in the roads and states shapefiles and filters for the East Coast I-95 HD ZEV corridor between Georgia and New Jersey

    Parameters
    ----------
    df_shapefile (pd.DataFrame): A pandas dataframe containing the shapefile info

    df_roads (string): Name of the column to be filtered on

    Returns
    -------
    df_eastcoast (pd.DataFrame): Filtered shapefile
    '''

    # Filter for the highways of interest
    df_i10 = df_roads[df_roads['FULLNAME'] == 'I- 10']
    df_i35 = df_roads[df_roads['FULLNAME'] == 'I- 35']
    df_i45 = df_roads[df_roads['FULLNAME'] == 'I- 45']
    
    # Select sections of the I-10 with longitude between Houston and LA
    HOUSTON_LONG = -95.3698
    LA_LONG = -118.2437
    df_i10_longs = df_i10.apply(get_longs, axis=1)
    df_i10 = df_i10[df_i10_longs.apply(np.max) > LA_LONG]            # East of LA
    df_i10 = df_i10[df_i10_longs.apply(np.min) < HOUSTON_LONG]       # West of Houston
    
    # Select sections of the I-35 with latitude between San Antonio and Dallas
    SAN_ANTONIO_LAT = 29.4252
    DALLAS_LAT = 32.779167
    
    df_i35_longs = df_i35.apply(get_lats, axis=1)
    df_i35 = df_i35[df_i35_longs.apply(np.max) > SAN_ANTONIO_LAT]    # North of San Antonio
    df_i35 = df_i35[df_i35_longs.apply(np.min) < DALLAS_LAT]         # South of Dallas
    
    # Select sections of the I-45 with latitude between Houston and Dallas
    HOUSTON_LAT = 29.749907
    DALLAS_LAT = 32.779167
    
    df_i45_longs = df_i45.apply(get_lats, axis=1)
    df_i45 = df_i45[df_i45_longs.apply(np.max) > HOUSTON_LAT]        # North of San Antonio
    df_i45 = df_i45[df_i45_longs.apply(np.min) < DALLAS_LAT]         # South of Dallas
    
    df_h2la = pd.concat([df_i10, df_i35, df_i45])
    
    return df_h2la
    
def get_bay_area():
    df_bay = gpd.read_file('https://spatial.lib.berkeley.edu/public/ark28722-s7hs4j/data.zip', include_fields = ['geometry'])
    return df_bay.dissolve()
    
#    # Filter for the highway in the specified states
#    bool_in_states = (df_states['STUSPS'] == in_states[0])
#    for state in in_states[1:]:
#        bool_in_states = bool_in_states | (df_states['STUSPS'] == state)
#
#    # Select the boundaries for the states of interest
#    df_in_states = df_states[bool_in_states]
#
#    # Convert the state boundaries to EPSG:4269 to match the roads shapefile
#    df_in_states = df_in_states.to_crs(4269)
#
#    # Get the spatial join of the highway and the states we want it to pass through
#    df_eastcoast = gpd.sjoin(df_eastcoast, df_in_states)
#
#    return df_eastcoast
    
def read_states_shapefile(top_dir):
    df_states = gpd.read_file(f'{top_dir}/data/state_boundaries/tl_2012_us_state.shp')
    df_states = df_states.filter(['STUSPS', 'Shape_Area', 'geometry'], axis=1)
    return df_states

def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the US primary national roads shapefile as a pandas dataframe
    df_roads = gpd.read_file(f'{top_dir}/data/tl_2019_us_primaryroads/tl_2019_us_primaryroads.shp', include_fields=['FULLNAME'])
    
    df_states = read_states_shapefile(top_dir)
    
    # Initialize a dictionary to contain geo dataframes for highway infrastructure projects
    dict_infrastructure = {}
    
    # Populate the dictionary with sections of the highway that HD ZEV projects are planned on
    dict_infrastructure['East Coast'] = get_highway_corridor(df_roads, df_states, highway_name = 'I- 95', in_states = ['GA', 'SC', 'NC', 'VA', 'MD', 'NJ', 'DE', 'PA'])
    dict_infrastructure['Midwest'] = get_highway_corridor(df_roads, df_states, highway_name = 'I- 80', in_states = ['IN', 'IL', 'OH'])
    dict_infrastructure['LA'] = get_highway_corridor(df_roads, df_states, highway_name = 'I- 710', in_states = ['CA'])
    dict_infrastructure['H2LA'] = get_H2LA_corridor(df_roads, df_states)
    dict_infrastructure['BayArea'] = get_bay_area()
    
    #dict_infrastructure['H2LA'] = get_highway_corridor(df_roads, df_states, highway_name = 'I- 80', in_states = ['IN', 'IL', 'OH'])
    
    
    # Save the shapefile for the East Coast HD ZEV corridor
    saveShapefile(dict_infrastructure['East Coast'], f'{top_dir}/data/hd_zev_corridors/eastcoast.shp')
    saveShapefile(dict_infrastructure['Midwest'], f'{top_dir}/data/hd_zev_corridors/midwest.shp')
    saveShapefile(dict_infrastructure['LA'], f'{top_dir}/data/hd_zev_corridors/la_i710.shp')
    saveShapefile(dict_infrastructure['H2LA'], f'{top_dir}/data/hd_zev_corridors/h2la.shp')
    saveShapefile(dict_infrastructure['BayArea'], f'{top_dir}/data/hd_zev_corridors/bayarea.shp')
    
#    # Merge the highway flow assignments in with the shapefile containing the highway links
#    merged_dataframe = mergeShapefile(df_highway_assignments, f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp')
#
#    #print(f'Merging took {time.time() - start_time} seconds')
#
#    # Save the merged shapefile
#    saveShapefile(merged_dataframe, f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp')
        
main()

