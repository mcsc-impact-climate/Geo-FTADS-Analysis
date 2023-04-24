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

import LCATools as LCAT


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
    mode (pd.DataFrame): A pandas dataframe containing (currently) all modes of transit used in the FAF5_metadata

        
    NOTE: None.

    '''

    # Read in Meta Data
    metaPath = f'{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx'
    meta = pd.ExcelFile(metaPath)
    
    tradeType = pd.read_excel(meta, 'Trade Type')
    # Only include truck rail and water
    mode = pd.read_excel(meta, "Mode")[0:3]
    dest = pd.read_excel(meta, 'FAF Zone (Domestic)')
    comms = pd.read_excel(meta, 'Commodity (SCTG2)')
    # dest.head()
    # print(origin)
    # geocode(origin.iloc[1, 1])
    
    # print('Meta read succesfully')

    return dest, mode, comms
    
    
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
    data = pd.read_csv(dataPath)
    #data = pd.read_csv(dataPath, nrows=100)  # DMM: This line is just for testing/development, to reduce processing time
    
    if cols is not None: data = data[cols]
    
    return data


# @jit(target_backend='cuda')
def processData(dest, mode):
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
    data = readData(["dms_orig", "dms_dest", "tons_2020", "dms_mode"])
    tons_in = np.zeros(len(dest))
    tons_out = np.zeros(len(dest))

    # Currently the algorithm works by iterating through the values in the meta data
    #   folloqws by iterating over the entirety of the data
    # The new goal is to break things down by mode utilizing the "dms_mode" key
    i = 0
    for row in tqdm(dest.values):
        print(row)
        for momo in mode.values:
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
    dest['Mode'] = pd.concat([mode]*len(dest)/len(mode), ignore_index=True)
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
    tons_exported_to_dict = {}
    tons_imported_from_dict = {}
    
    dest_dict = {}
    
    for region in dest.values:
        region_code = region[0]
        region_info = region_code
        tons_exported_to_dict[region_info] = np.zeros(len(dest))
        tons_imported_from_dict[region_info] = np.zeros(len(dest))
        dest_dict[region_info] = dest.copy(deep=True)
    
    data = readData(["dms_orig", "dms_dest", "tons_2020"])

    # Currently the algorithm works by iterating through the values in the meta data
    #   follows by iterating over the entirety of the data
    i = 0
    for row in tqdm(dest.values):
        # i: row (faf5 region)
        for line in data.values:
            # if tons_in[i] == 0: print(line[0], line[1])
            
            # If the cargo is going to the region associated with the given row (i), add it to the exports from the origin (line[0]) to the given row (i)
            if line[1] == row[0]:
                origin_region = line[0]
                tons_exported_to_dict[origin_region][i] += line[2]

            # If the cargo is originating from the region associated with the given row (i), add it to the imports from the given row (i) to the destination (line[1])
            if line[0] == row[0]:
                dest_region = line[1]
                tons_imported_from_dict[dest_region][i] += line[2]
        i+=1
        # if i==2: break

    # Fill in the imports and exports to/from each region
    for region in dest_dict:
        dest_dict[region]['Total Imported From'] = tons_imported_from_dict[region_info]
        dest_dict[region]['Total Exported To'] = tons_exported_to_dict[region_info]
        
        # Incorec -> should be zfilling 'Numeric Label" instead
        dest_dict[region]['Numeric Label'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
        dest_dict[region] = dest_dict[region].rename(columns={'Numeric Label': 'FAF_Zone'})  # DMM: Renaming for consistency with shapefile
        
    return dest_dict

def filterLCA(item='CO2 (w/ C in VOC & CO)', comm='all'):
    emit = LCAT.df_lca_dict
    lca_filt = pd.DataFrame()
    commodities = []
    modes = []
    
    # print(list(LCAT.df_lca_dict.keys()))
    # print(LCAT.df_lca_dict['truck'])
    
    # It is a two layer dictionary with the first being modes 
    # The second layer is commodities
    for key, mode in emit.items():
        # This only goes through a specific commodity for all modes given the input
        # The default value is 'all' for the sake of ease
        if comm != None:
            new_row = mode[comm].loc[mode[comm]['Item'] == item]
            lca_filt = pd.concat([lca_filt.loc[:], new_row]).reset_index(drop=True)
            commodities.append(comm)
            modes.append(key)
            # print(new_row)
            # print(lca_filt)
            
        else:
            for cKey, commodity in mode.items():
                # This loop goes through all possible commodities given that the input is none
                if cKey != 'all':
                    new_row = commodity.loc[commodity['Item'] == item]
                    lca_filt = pd.concat([lca_filt.loc[:], new_row]).reset_index(drop=True)
                    commodities.append(cKey)
                    modes.append(key)    
                
    lca_filt['Commodity'] = commodities
    lca_filt['Modes'] = modes
    # print(lca_filt)
    # print(commodities)
    
    return lca_filt

# The method will be modified to incorporate the below calculation of emissions in 
#   completeOD() for simplification purposes
def emissions_OD(dest, mode, comm=None):
    data = readData(["dms_orig", "dms_dest", "tons_2020", "dms_mode", 'tmiles_2020', 'sctg2'])
    
    # This is dest*mode based on the idea that we account for all possible 
    #   values (excluding the finer commodity ones)
    tot_len = len(dest)*len(mode)
    
    tons_in = np.zeros(tot_len)
    tons_out = np.zeros(tot_len)
    ton_miles = np.zeros(tot_len)
    
    emissions = np.zeros(tot_len)
    
    emissions_data = filterLCA()
    
    # Currently the algorithm works by iterating through the values in the meta
    #   data follows by iterating over the entirety of the data
    # The new goal is to break things down by mode utilizing the "dms_mode" key
    i = 0
    for row in tqdm(dest.values):
        # 0 will be truck, 1 will be rail, 2 will be water
        #   for momo in mode.values:        
        for line in data.values:           
            if line[3] == mode['Numeric Label'][0]:
                j = i
                eMult = emissions_data['WTW'][0]
            elif line[3] == mode['Numeric Label'][1]:
                j = i+1
                eMult = emissions_data['WTW'][1]
            elif line[3] == mode['Numeric Label'][2]:
                j = i+2
                eMult = emissions_data['WTH'][2]
            else:
                # This continue exists as we only want to consider truck, rail,
                #   or water
                continue
            
            if line[1] == row[0]:
                tons_in[j] += line[2]
                ton_miles[j] += line[4]
                emissions[j] += line[4] * eMult
                
            if line[0] == row[0]:
                tons_out[j] += line[2]
        
        i+=1
        # if i==2: break
    
    dest['Total Import'] = tons_in
    dest['Total Export'] = tons_out
    dest['FAF_Zone'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
    # dest = dest.rename(columns={'Numeric Label': 'FAF_Zone'})  # DMM: Renaming for consistency with shapefile
    dest['Mode'] = pd.concat([mode['Description']]*tot_len, ignore_index=True)
    dest['Ton-Miles'] = ton_miles
    dest['Emissions'] = emissions
    
    return dest


def completeOD(mode, commodity):
    '''
    The idea behind this method is that since modifying the origin destination
        pairs by commodity and then mode is the same as going over the entire
        data set, we simply calculate the emissions for the entire dataset and
        then use that new dataset to be summed over (it's less math/operations
        overall)

    Parameters
    ----------
    mode : DataFrame
        Is a DataFrame from the meta data containing the associated keys for
            the various FAF5 modes. Note we only are considering truck, rail,
            and ship.
    commodity : DataFrame
        DESCRIPTION.

    Returns
    -------
    data : DataFrame
        DESCRIPTION.

    '''
    
    data = readData(["dms_orig", "dms_dest", "tons_2020", "dms_mode", 'tmiles_2020', 'sctg2'])
    tot_len = len(data)

    emissions_data = filterLCA(comm=None)
    emissions = np.zeros(tot_len)
    
    mode_complete = np.zeros(tot_len)
    comm_complete = np.zeros(tot_len)

    i = 0    
    for row in tqdm(data.values):
        # Finds the keys for mode and commodity
        commodity_sp = commodity.loc[row[5]][1]
        mode_sp = mode.loc[row[3]][1].lower()
        
        if mode_sp == 'ship':
            w2 = 'WTH'
        else:
            w2 = 'WTW'
        
        # print(commodity_sp)
        modifier = emissions_data.loc[
            (emissions_data['Modes'] == mode_sp) 
            & (emissions_data['Commodity'] == commodity_sp)].iloc[-1][w2]
        
        emissions[i] = row[4] * modifier
        mode_complete[i] = mode_sp
        comm_complete[i] = commodity_sp
        
        i += 1

    data['emissions'] = emissions
    data['commodity'] = comm_complete
    data['mode'] = mode_complete
    
    return data


def getCompleteOD():
    '''
    Method gets the saved csv of the completeOD() data and returns as a DF

    Returns
    -------
    data : DataFrame
        DataFrame of the complete emissions data.

    '''
    savePath = f'{top_dir}/data/'
    
    dataPath = savePath + 'completeOD.csv'
    data = pd.read_csv(dataPath)

    return data


def filterDataOD(data, mode, commodity):
    '''
    This method filters the data based on a given array of modes and commodities.

    Parameters
    ----------
    data : DataFrame
        DataFrame of the entire dataset produced in completeOD().
    mode : Array
        Array of the modes that are being filtered.
    commodity : Array
        Array of the commodities that are being filtered.

    Returns
    -------
    data_filtered : DataFrame
        DataFrame of the filtered and summed data based on the input modes and 
            commodities.

    '''
    data_filtered = pd.DataFrame()
    data_length = len(mode) * len(commodity)
    
    data_filtered['Mode'] = pd.concat([mode]*len(commodity), ignore_index=True)
    data_filtered['Commodity'] = pd.concat([commodity]*len(mode), ignore_index=True)
    
    emissions = np.zeros(data_length)
    
    i = 0
    for row in tqdm(data_filtered.values):
        for line in data.values:
            if line[-1] == row[0]:
                if line[-2] == row[1]:
                    emissions[i] += line[-3]
        i += 1
        
    data_filtered['Emissions'] = emissions()
    
    return data_filtered


def mergeShapefile(dest, shapefile_path, by_region = False):
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
    
    if by_region:
        dest_filtered = dest.filter(['FAF_Zone', 'Total Imported From', 'Total Exported To'], axis=1)
    else:
        dest_filtered = dest.filter(['FAF_Zone', 'Total Import', 'Total Export'], axis=1)
    
    merged_dataframe = shapefile_filtered.merge(dest_filtered, on='FAF_Zone', how='left')
    
    # Add columns with imports and exports per unit area (km^2)
    meters_per_mile = 1609.34
    
    if by_region:
        merged_dataframe['Tot Imp Dens'] = merged_dataframe['Total Imported From'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
        merged_dataframe['Tot Exp Dens'] = merged_dataframe['Total Exported To'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    else:
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
    # filterLCA()
    
    # Load FAF5 Regional Metadata
    dest, mode, comms = readMeta()
    dataOD = completeOD(mode, comms)
    saveFile(dataOD, 'total_tons_short')
    
    # dest_with_tonnage = emissions_OD(dest, mode)
    # saveFile(dest_with_tonnage, 'total_tons_short')

    # DMM: To save time for testing and development, can read in saved csv with the following three lines
    # and comment out above two lines
    #dest = pd.read_csv(f'{top_dir}/data/total_tons.csv', dtype=object)
    #dest['Total Import'] = dest['Total Import'].astype('float')
    #dest['Total Export'] = dest['Total Export'].astype('float')

    # merged_dataframe = mergeShapefile(dest_with_tonnage, f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp')
    # saveShapefile(merged_dataframe, f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage.shp')
    
#    merged_dataframe = mergeShapefile(dest_with_tonnage, f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp')
#    saveShapefile(merged_dataframe, f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage.shp')

#    # Evaluate imports and exports to/from each individual region
#    dest_with_tonnage_by_region_dict = processDataByRegion(dest)
#
#    for region in dest_with_tonnage_by_region_dict:
#        merged_dataframe = mergeShapefile(dest_with_tonnage_by_region_dict[region], f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp', by_region=True)
#        saveShapefile(merged_dataframe, f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage_{region}.shp')
        
main()
