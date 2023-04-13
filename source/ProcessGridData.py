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
from pathlib import Path

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


def readData(top_dir):
    '''
    Reads in the data file for the eGrids data
    
    Parameters
    ----------
    None

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2021 eGrid data for each subregion
        
    NOTE: None.

    '''
    

    # Read in the data associated with each eGrids subregion
    dataPath = f'{top_dir}/data/eGRID2021_data.xlsx'
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, 'SRL21', skiprows=[0])
    
    # Select the columns of interest
    # SUBRGN: eGRID sub-region acronym
    # SRCO2EQA: eGRID subregion annual CO2 equivalent emissions (tons)
    # SRC2ERTA: eGRID subregion annual CO2 equivalent total output emission rate (lb/MWh)
    data_df = data_df.filter(['SUBRGN', 'SRCO2EQA', 'SRC2ERTA'], axis=1)#, 'SRCLPR', 'SROLPR', 'SRGSPR', 'SRNCPR', 'SRHYPR', 'SRBMPR', 'SRWIPR', 'SRSOPR', 'SRGTPR', 'SROFPR', 'SROPPR'], axis=1)
    
    # Rename the subregion name to match the shapefile
    data_df = data_df.rename(columns={'SUBRGN': 'ZipSubregi'})

    return data_df
    
def mergeShapefile(data_df, shapefile_path):
    '''
    Merges the shapefile containing eGrid region borders with the dataframe containing the eGrids data

    Parameters
    ----------
    data_df (pd.DataFrame): A pandas dataframe containing the subregion names and emissions data for each subregion

    shapefile_path (string): Path to the shapefile to be joined with the dataframe

    Returns
    -------
    merged_Dataframe (pd.DataFrame): Joined dataframe
    '''
    shapefile = gpd.read_file(shapefile_path)
    
    # Merge the dataframes based on the subregion name
    merged_dataframe = shapefile.merge(data_df, on='ZipSubregi', how='left')
            
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

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Read in the eGrids metadata
    egrid_data = readData(top_dir)
    
    # Merge the eGrids data in with the shapefile with subregion borders
    merged_dataframe = mergeShapefile(egrid_data, f'{top_dir}/data/egrid2020_subregions/eGRID2020_subregions.shp')
    
    # Save the merged shapefile
    saveShapefile(merged_dataframe, f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp')
    
    
    
main()
