#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 22:38:22 2023

@author: micahborrero
"""
# Import needed modules
# NOTE: For testing purposes qgis packages are commented out
# from qgis.core import *
# import qgis.utils
# from qgis.PyQt import QtGui
# from console.console import _console

import os
import sys

import numpy as np
import pandas as pd

# Random efficiency modules
# from dask import delayed
# import multiprocessing
# from numba import jit, cuda
# import dask.dataframe as dd


import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir


# =============================================================================
# # Get the path to top level of the git directory so we can use relative paths
# source_dir = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)
# if source_dir.endswith('/source'):
#     top_dir = source_dir[:-7]
# elif source_dir.endswith('/source/'):
#     top_dir = source_dir[:-8]
# else:
#     print("ERROR: Expect current directory to end with 'source'. Cannot use relative directories as-is. Exiting...")
#     sys.exitfunc()
# =============================================================================

# Convert to class using python's built in __init__ and __call__ later
# def getDir():
path = os.getcwd()
# print("Current Directory", path)
 
# prints parent directory
# print('Parent Directory', os.path.abspath(os.path.join(path, os.pardir)))
#top_dir = os.path.dirname(path)
top_dir = get_top_dir()
                              
def geocode(loc):
    locator = geopy.Nominatim(user_agent = "MyGeocoder")
    location = locator.geocode(loc)
    print(location.longitude, location.latitude)

def readMeta():
    '''
    Reads in the metadata file (functionally keys) for the FAF5 data
    
    Parameters
    ----------
    None

    Returns
    -------
    dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata
        
    NOTE: None.

    '''

    # Read in Meta Data
    metaPath = f'{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx'
    meta = pd.ExcelFile(metaPath)
    
    tradeType = pd.read_excel(meta, 'Trade Type')
    dest = pd.read_excel(meta, 'FAF Zone (Domestic)')
    # dest.head()
    # print(origin)
    # geocode(origin.iloc[1, 1])
    
    # print('Meta read succesfully')

    return dest
    
    
def readData(cols=None):
    '''
    Reads in FAF5 origin-destination data
    
    Parameters
    ----------
    cols (list): List of columns to filter the data by

    Returns
    -------
    None
        
    NOTE: dms_dest -> index 2; dms_orig -> index 1; tons_2020 -> index 12

    '''
    dataPath = f'{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5.4.1_2018-2020.csv'
    #data = pd.read_csv(dataPath)
    data = pd.read_csv(dataPath, nrows=10000)  # DMM: This line is just for testing/development, to reduce processing time
    
    if cols is not None: data = data[cols]
    
    return data


# @jit(target_backend='cuda')
def processData(dest):
    '''
    Assigns a net ton (either import or export) to each FAF5 region
    
    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata

    Returns
    -------
    None
        
    NOTE: dms_dest -> index 2; dms_orig -> index 1; tons_2020 -> index 12

    '''
    data = readData(["dms_orig", "dms_dest", "tons_2020"])
    tons_in = np.zeros(len(dest))
    tons_out = np.zeros(len(dest))

    # Currently the algorithm works by iterating through the values in the meta data
    #   folloqws by iterating over the entirety of the data
    i = 0
    for row in tqdm(dest.values):
        for line in data.values:
            # if tons_in[i] == 0: print(line[0], line[1])
            if line[1] == row[0]:
                tons_in[i] += line[2]
                
            if line[0] == row[0]:
                tons_out[i] += line[2]
        i+=1
        # if i==2: break
    
    # Incorec -> should be zfilling 'Numeric Label" instead
    dest['Total Import'] = tons_in # pd.Series(np.rint(tons_in).astype(int)).astype(str).str.zfill(9)
    dest['Total Export'] = tons_out
    dest['Numeric Label'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
    dest = dest.rename(columns={'Numeric Label': 'FAF_Zone'})  # DMM: Renaming for consistency with shapefile
    return dest
    
def processDataByRegion(dest):
    '''
    Assigns a net ton (either import or export) to each FAF5 region for imports to or exports from the specified region
    
    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata

    Returns
    -------
    None
        
    NOTE: dms_dest -> index 2; dms_orig -> index 1; tons_2020 -> index 12

    '''
    tons_into_region_dict = {}
    tons_out_of_region_dict = {}
    
    dest_dict = {}
    
    for region in dest.values:
        region_code = region[0]
        region_name = region[1].replace(' ', '_')
        region_info = f'{region_code}_{region_name}'
        print(region_code, region_name)
        tons_into_region_dict[region_info] = {'imports into region': np.zeros(len(dest))}
        tons_out_of_region_dict[region_info] = {'exports out of region': np.zeros(len(dest))}
        dest_dict[region_info] = dest.copy(deep=True)
    
    data = readData(["dms_orig", "dms_dest", "tons_2020"])

#    # Currently the algorithm works by iterating through the values in the meta data
#    #   follows by iterating over the entirety of the data
    i = 0
    for row in tqdm(dest.values):
        for line in data.values:
            # if tons_in[i] == 0: print(line[0], line[1])
            if line[1] == row[0]:
                region_into_info = f"{row[0]}_{row[1].replace(' ', '_')}"
                tons_into_region_dict[region_into_info]['imports into region'][i] += line[2]

            if line[0] == row[0]:
                region_out_of_info = f"{row[0]}_{row[1].replace(' ', '_')}"
                tons_out_of_region_dict[region_out_of_info]['exports out of region'][i] += line[2]
        i+=1
        # if i==2: break

    # Fill in the imports and exports to/from each region
    for region in dest_dict:
        print(tons_into_region_dict[region_info])
        dest_dict[region]['Total Import'] = tons_into_region_dict[region_info]
        dest_dict[region]['Total Export'] = tons_into_region_dict[region_info]
        
        # Incorec -> should be zfilling 'Numeric Label" instead
        dest_dict[region]['Numeric Label'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
        dest_dict[region] = dest_dict[region].rename(columns={'Numeric Label': 'FAF_Zone'})  # DMM: Renaming for consistency with shapefile
        
    return dest_dict

def mergeShapefile(dest, shapefile_path):
    '''
    Merges the shapefile containing FAF5 region borders with the csv file containing total tonnage
    calculated in processData()

    Parameters
    ----------
    dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata, along
    with total tonnages calculated in processData()

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path)
    
    # Select columns of interest
    shapefile_filtered = shapefile.filter(['Short Description', 'FAF_Zone', 'FAF_Zone_D', 'ShapeSTAre', 'ShapeSTLen', 'geometry'], axis=1)
    dest_filtered = dest.filter(['FAF_Zone', 'Total Import', 'Total Export'], axis=1)
    
    merged_dataframe = shapefile_filtered.merge(dest_filtered, on='FAF_Zone', how='left')
    
    # Add columns with imports and exports per unit area (km^2)
    meters_per_mile = 1609.34
    merged_dataframe['Tot Imp Dens'] = merged_dataframe['Total Import'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tot Exp Dens'] = merged_dataframe['Total Export'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
        
    return merged_dataframe


def saveFile(file, name):
    savePath = f'{top_dir}/data/'
    file.to_csv(savePath + f'{name}.csv', index=False)
    print(f'file has been saved as a csv')

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

def main ():
    # Load FAF5 Regional Metadata
    dest = readMeta()
    
    
#    dest_with_tonnage = processData(dest)
    #saveFile(dest_with_tonnage, 'total_tons_short')

    # DMM: To save time for testing and development, can read in saved csv with the following three lines
    # and comment out above two lines
    #dest = pd.read_csv(f'{top_dir}/data/total_tons.csv', dtype=object)
    #dest['Total Import'] = dest['Total Import'].astype('float')
    #dest['Total Export'] = dest['Total Export'].astype('float')

#    merged_dataframe = mergeShapefile(dest_with_tonnage, f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp')
#    saveShapefile(merged_dataframe, f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage.shp')

    # Evaluate imports and exports to/from each individual region
    dest_with_tonnage_by_region_dict = processDataByRegion(dest)

    for region in dest_with_tonnage_by_region_dict:
        print(dest_with_tonnage_by_region_dict[region])
        merged_dataframe = mergeShapefile(dest_with_tonnage_by_region_dict[region], f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp')
        saveShapefile(merged_dataframe, f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage_{region}.shp')
        
main()
