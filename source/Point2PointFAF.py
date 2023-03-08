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
top_dir = os.path.dirname(path)
                              
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
    data = pd.read_csv(dataPath)
    
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
    return dest


def saveFile(file, name):
    savePath = f'{top_dir}/data/'
    file.to_csv(savePath + f'{name}.csv', index=False)
    print(f'file has been saved as a csv')
            

def main ():
    # Load FAF5 Regional Metadata
    dest = readMeta()
    saveFile(processData(dest), 'total_tons')
    
main()