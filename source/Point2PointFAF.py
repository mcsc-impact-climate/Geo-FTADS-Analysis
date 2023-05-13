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
import LCATools as LCAT
from CommonTools import get_top_dir
import argparse


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
    #data = pd.read_csv(dataPath, nrows=1000)  # DMM: This line is just for testing/development, to reduce processing time
    
    if cols is not None: data = data[cols]
    
    return data


def filterLCA(item='CO2 (w/ C in VOC & CO)', comm='all'):
    '''
    The purpose of this method is to import the LCA data and filter it in a
        manner that is easily readable for processing

    Parameters
    ----------
    item : String, optional
        The pollutant modifier in which things will be filtered by.
            The default is 'CO2 (w/ C in VOC & CO)'.
    comm : String, optional
        The commodity in which all things will be filtered by. In the event
            that the input is None, it will include all commodities.
            The default is 'all'.

    Returns
    -------
    lca_filt : DataFrame
        DataFrame based on the LCA data containing the relevant rows based on 
            the filters.

    '''
    emit = LCAT.df_lca_dict
    lca_filt = pd.DataFrame()
    commodities = []
    modes = []
    
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
    
    return lca_filt


# No longer used
# =============================================================================
# # The method will be modified to incorporate the below calculation of emissions in 
# #   completeOD() for simplification purposes
# def emissions_OD(dest, mode, comm=None):
#     '''
#     Assigns a net ton (either import or export) to each FAF5 region
#     
#     Parameters
#     ----------
#     dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata
# 
#     Returns
#     -------
#     None
#         
#     NOTE: dms_dest -> index 2; dms_orig -> index 1; tons_2020 -> index 12
# 
#     '''
#     data = readData(["dms_orig", "dms_dest", "tons_2020", "dms_mode", 'tmiles_2020', 'sctg2'])
#     
#     # This is dest*mode based on the idea that we account for all possible 
#     #   values (excluding the finer commodity ones)
#     tot_len = len(dest)*len(mode)
#     
#     tons_in = np.zeros(tot_len)
#     tons_out = np.zeros(tot_len)
#     ton_miles = np.zeros(tot_len)
#     
#     emissions = np.zeros(tot_len)
#     
#     emissions_data = filterLCA()
#     
#     # Currently the algorithm works by iterating through the values in the meta
#     #   data follows by iterating over the entirety of the data
#     # The new goal is to break things down by mode utilizing the "dms_mode" key
#     i = 0
#     for row in tqdm(dest.values):
#         # 0 will be truck, 1 will be rail, 2 will be water
#         #   for momo in mode.values:        
#         for line in data.values:           
#             if line[3] == mode['Numeric Label'][0]:
#                 j = i
#                 eMult = emissions_data['WTW'][0]
#             elif line[3] == mode['Numeric Label'][1]:
#                 j = i+1
#                 eMult = emissions_data['WTW'][1]
#             elif line[3] == mode['Numeric Label'][2]:
#                 j = i+2
#                 eMult = emissions_data['WTH'][2]
#             else:
#                 # This continue exists as we only want to consider truck, rail,
#                 #   or water
#                 continue
#             
#             if line[1] == row[0]:
#                 tons_in[j] += line[2]
#                 ton_miles[j] += line[4]
#                 emissions[j] += line[4] * eMult
#                 
#             if line[0] == row[0]:
#                 tons_out[j] += line[2]
#         
#         i+=1
#     
#     dest['Total Import'] = tons_in
#     dest['Total Export'] = tons_out
#     dest['FAF_Zone'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
#     dest['Mode'] = pd.concat([mode['Description']]*tot_len, ignore_index=True)
#     dest['Ton-Miles'] = ton_miles
#     dest['Emissions'] = emissions
#     
#     return dest
# =============================================================================


def completeOD(mode, commodity, selected_mode=None, selected_commodity=None, selected_origin=None, selected_destination=None):
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
    emissions_data = filterLCA(comm=None)

    # Remove rows with dms_mode > 3
    if (not selected_origin is None) and (not selected_origin=='all'):
        data = data.drop(data[data.dms_orig != int(selected_origin)].index)
    if (not selected_destination is None) and (not selected_destination=='all'):
        data = data.drop(data[data.dms_dest != int(selected_destination)].index)
                
    data = data.drop(data[data.dms_mode > 3].index)
    data['emissions'] = data['sctg2']
    data['commodity'] = data['sctg2']
    data['mode'] = data['sctg2']

    for this_mode in mode['Numeric Label']:
        for this_commodity in commodity['Numeric Label']:
            cCommodity_mode = (data['dms_mode'] == this_mode) & (data['sctg2'] == this_commodity)

            commodity_sp = commodity.loc[commodity['Numeric Label'] == this_commodity].values[0][1]
            data['commodity'][cCommodity_mode] = commodity_sp

            mode_sp = mode.loc[mode['Numeric Label'] == this_mode].values[0][1].lower()
            if mode_sp == 'water':
                w2 = 'WTH'
                mode_sp = 'ship'
            else:
                w2 = 'WTW'

            data['mode'][cCommodity_mode] = mode_sp
            emissions_modifier = emissions_data.loc[(emissions_data['Modes'] == mode_sp) & (emissions_data['Commodity'] == commodity_sp)][w2].values[0]
            data['emissions'][cCommodity_mode] = data['tmiles_2020'][cCommodity_mode] * emissions_modifier
            
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


def filterDataMC(data, mode, commodity):
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


def filterOD(dest, data, direction=True):
    data_filtered = pd.DataFrame()
    
    tot_len = len(dest)
    
    tons_in = np.zeros(tot_len)
    tons_out = np.zeros(tot_len)
    tons_tot = np.zeros(tot_len)
    
    ton_miles_in = np.zeros(tot_len)
    ton_miles_out = np.zeros(tot_len)
    ton_miles_tot = np.zeros(tot_len)
    
    emissions_in = np.zeros(tot_len)
    emissions_out = np.zeros(tot_len)
    emissions_tot = np.zeros(tot_len)
    
    i = 0
    for row in tqdm(dest.values):
        for line in data.values:
            if line[1] == row[0] or line[0] == row[0]:
                tons_tot[i] += line[2]
                ton_miles_tot[i] += line[4]
                emissions_tot[i] += line[-3]
            if line[1] == row[0]: # Import
                tons_in[i] += line[2]
                ton_miles_in[i] += line[4]
                emissions_in[i] += line[-3]
#                    if direction:
#                        ton_miles[i] += line[3]
#                        emissions[i] += line[-3]
                
            if line[0] == row[0]: # Export
                tons_out[i] += line[2]
                ton_miles_out[i] += line[4]
                emissions_out[i] += line[-3]
                    
#                    if not direction:
#                        ton_miles[i] += line[3]
#                        emissions[i] += line[-3]
            
        i+=1
    
    data_filtered['FAF_Zone'] = dest['Numeric Label'].apply(str).apply(lambda x: x.zfill(3))
    data_filtered['Tons Import'] = tons_in
    data_filtered['Tons Export'] = tons_out
    data_filtered['Tons Total'] = tons_tot
    
    data_filtered['Tmiles Import'] = ton_miles_in
    data_filtered['Tmiles Export'] = ton_miles_out
    data_filtered['Tmiles Total'] = ton_miles_tot

    data_filtered['E Import'] = emissions_in
    data_filtered['E Export'] = emissions_out
    data_filtered['E Total'] = emissions_tot
    
    return data_filtered


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
    dest_filtered = dest.filter(['FAF_Zone', 'Tons Import', 'Tons Export', 'Tons Total', 'Tmiles Import', 'Tmiles Export', 'Tmiles Total', 'E Import', 'E Export', 'E Total'], axis=1)
    
    merged_dataframe = shapefile_filtered.merge(dest_filtered, on='FAF_Zone', how='left')
    
    # Add columns with imports and exports per unit area (km^2)
    meters_per_mile = 1609.34
    merged_dataframe['Tons Imp Den'] = merged_dataframe['Tons Import'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tons Exp Den'] = merged_dataframe['Tons Export'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tons Tot Den'] = merged_dataframe['Tons Total'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tmil Imp Den'] = merged_dataframe['Tmiles Import'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tmil Exp Den'] = merged_dataframe['Tmiles Export'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['Tmil Tot Den'] = merged_dataframe['Tmiles Total'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['E Imp Den'] = merged_dataframe['E Import'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['E Exp Den'] = merged_dataframe['E Export'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    merged_dataframe['E Tot Den'] = merged_dataframe['E Total'] / ( merged_dataframe['ShapeSTAre'] * (1./meters_per_mile)**2 )
    
    dest_filtered = merged_dataframe.filter(['FAF_Zone', 'Tons Import', 'Tons Export', 'Tons Total', 'Tmiles Import', 'Tmiles Export', 'Tmiles Total', 'E Import', 'E Export', 'E Total', 'Tons Imp Den', 'Tons Exp Den', 'Tons Tot Den', 'Tmil Imp Den', 'Tmil Exp Den', 'Tmil Tot Den', 'E Imp Den', 'E Exp Den', 'E Tot Den'], axis=1)
    
    return merged_dataframe, dest_filtered


def saveFile(file, name):
    savePath = f'{top_dir}/data/Point2Point_outputs/'
    if not os.path.exists(savePath):
        os.makedirs(savePath)
        
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

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mode', default='truck')
parser.add_argument('-c', '--commodity', default='all')
parser.add_argument('-o', '--origin', default='all')
parser.add_argument('-d', '--dest', default='all')

def main ():
    args = parser.parse_args()

    # filterLCA()
    
    # Load FAF5 Regional Metadata
    dest, mode, comm = readMeta()
    #print(dest, mode, comms)
    
    dataOD = completeOD(mode, comm, selected_origin=args.origin, selected_destination=args.dest)#, selected_modes, selected_commodities, origin_region=11, dest_region='all')#, origin_region='all', dest_region='all')
    
    # Apply selections
    cBaseline = (dataOD['dms_orig'] > -9999)
    if args.mode == 'all':
        cMode = True
    else:
        cMode = (dataOD['mode'] == args.mode)
    
    if args.commodity == 'all':
        cCommodity = True
    else:
        cCommodity = (dataOD['commodity'] == args.commodity)

    if args.origin == 'all':
        cOrigin = True
    else:
        cOrigin = (dataOD['dms_orig'] == int(args.origin))
        
    if args.dest == 'all':
        cDest = True
    else:
        cDest = (dataOD['dms_dest'] == int(args.dest))
    
    dataOD_selected = dataOD[cBaseline&cMode&cCommodity&cOrigin&cDest]
    
    # Sum emissions and ton-miles over all trips
    data_filtered = filterOD(dest, dataOD_selected, direction=True)
        
    commodity_save = args.commodity.replace(' ', '_').replace('/', '_')

#    with pd.option_context('display.max_rows', None,):
#        print(data_filtered)


    # print(comms.loc[comms['Numeric Label'] == 1].values[0][1])
    # print(mode.loc[mode['Numeric Label'] == 1].values[0][1])
    # print(mode[mode.Numeric_Label=='1'].Description.item())
    # print(dataOD)
    
    #print(mode.loc[mode['Description']=='Truck'])
    #datfil1 = filterDataMC(dataOD, mode, comms)
    #print(datafil1)
    
    #saveFile(dataOD, 'completeOD')

    
    # dest_with_tonnage = emissions_OD(dest, mode)
    # saveFile(dest_with_tonnage, 'total_tons_short')

    # DMM: To save time for testing and development, can read in saved csv with the following three lines
    # and comment out above two lines
    #dest = pd.read_csv(f'{top_dir}/data/total_tons.csv', dtype=object)
    #dest['Total Import'] = dest['Total Import'].astype('float')
    #dest['Total Export'] = dest['Total Export'].astype('float')

    merged_dataframe, data_filtered = mergeShapefile(data_filtered, f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp')
    saveFile(data_filtered, f'mode_{args.mode}_commodity_{commodity_save}_origin_{args.origin}_dest_{args.dest}')
    saveShapefile(merged_dataframe, f'{top_dir}/data/Point2Point_outputs/mode_{args.mode}_commodity_{commodity_save}_origin_{args.origin}_dest_{args.dest}.shp')
    
    
main()
