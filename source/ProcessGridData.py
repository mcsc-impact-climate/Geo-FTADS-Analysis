#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 09:24:00 2023

@author: danikam
"""

# Import needed modules
import sys

import numpy as np
import pandas as pd

import geopandas as gpd
import geopy
from tqdm import tqdm, trange
from CommonTools import get_top_dir, mergeShapefile, saveShapefile


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

def main():

    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()
    
    # Read in the eGrids metadata
    egrid_data = readData(top_dir)
    
    # Merge the eGrids data in with the shapefile with subregion borders
    merged_dataframe = mergeShapefile(egrid_data, f'{top_dir}/data/egrid2020_subregions/eGRID2020_subregions.shp', 'ZipSubregi')
    
    # Save the merged shapefile
    saveShapefile(merged_dataframe, f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp')
    
main()
