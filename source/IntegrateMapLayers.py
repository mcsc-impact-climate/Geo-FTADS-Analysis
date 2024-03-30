#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 2024

@author: micahborrero
"""

import geopandas as gpd
import networkx as nx
import pandas as pd


import ExtractHighways as eh
from CommonTools import get_top_dir


top_dir = get_top_dir()


def applyAreaLayer(location, pathLoc):
    '''
    Add attributes of various area layers to desired corridor of interest.

    Parameters
    ----------
    location : str
        String describing the path to the desired area layer shapefile.
    pathLoc : str
        String describing the path to the desired corridor shapefile.

    Returns
    -------
    mergedData : Geopandas DataFrame
        DataFrame containing the an updated corridor with area layer attributes merged.

    '''
    toMerge = eh.loadShapefile(location)
    pathOfInterest = eh.loadShapefile(pathLoc)
    
    mergedData = gpd.sjoin(pathOfInterest, toMerge, how='left', predicate='within')
    
    return mergedData

def averageValues(gdf, column):
    # TODO: average values over corridor
    mean = gdf[column].mean()
    
    name = column + ' Average'
    
    gdf[name] = mean
    
    return gdf
    
    
def applyPointLayer():
    # TODO: Integrate application of point layers
    pass


def combineToSingle(corridors, name):
    name = name + ' Combined'
    
    combined = pd.concat(corridors, ignore_index=True)
        
    combined.to_file(f"{top_dir}/data/paths_of_interest/{name}.shp")
    
if __name__ == "__main__":
    # change 'location' based on shapefile of interest
    location = f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp'
    
    filename = 'pathgraph'
    # pathLoc = [f'{top_dir}/data/paths_of_interest/{filename}.shp' ]
    pathLocS = [f'{top_dir}/data/paths_of_interest/CrossCountry.shp', f'{top_dir}/data/paths_of_interest/BayToSea.shp', f'{top_dir}/data/paths_of_interest/WesFlo.shp' ]
    
    # change 'column' based on column of interest
    column = 'SRCO2EQA'
    
    corridors = []
    
    for path in pathLocS:
        applied = applyAreaLayer(location, path)
        averaged = averageValues(applied, column)
        
        corridors.append(averaged)
        
    combineToSingle(corridors, 'CrossBayFlo')
    
    # return corridors

# corridors = main()
    
    