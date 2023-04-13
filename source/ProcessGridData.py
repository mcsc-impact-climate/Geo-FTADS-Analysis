#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 09:24:00 2023

@author: danikam
"""
# Import needed modules

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


def readMeta():
    '''
    Reads in the metadata file for the eGrids data
    
    Parameters
    ----------
    None

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2021 eGrid data for each subregion
        
    NOTE: None.

    '''

    # Read in Meta Data
    metaPath = f'{top_dir}/data/eGRID2021_data.xlsx'
    meta = pd.ExcelFile(metaPath)
    
    #tradeType = pd.read_excel(meta, 'Trade Type')
    dest = pd.read_excel(meta, 'FAF Zone (Domestic)')
    dest.head()
    # print(origin)
    # geocode(origin.iloc[1, 1])
    
    # print('Meta read succesfully')

    return dest

def main():
    top_dir = get_top_dir()
    
    egrid_data = readMeta()
    
    
main()
