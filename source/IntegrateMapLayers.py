#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 2024

@author: micahborrero
"""

import geopandas as gpd
import pandas as pd


import ExtractHighways as eh
from CommonTools import get_top_dir
import AnalyzeTruckStopCharging as atsc


top_dir = get_top_dir()


def loadFiles(location, isgeojson, pathLoc):
    '''
    Loads the relevant GeoDataFrames

    Parameters
    ----------
    location : str
        Directory path of the layer of interest.
    isgeojson : bool
        Boolean describing whether or not the layer of interest is formatted as a geojson.
    pathLoc : str
        Directory location of the corridors of interest.

    Returns
    -------
    pathOfInterest : Geopandas DataFrame
        Corridors of interest.
    toMerge : Geopandas DataFrame
        Layer of interest.

    '''
    toMerge = eh.loadShapefile(location, isgeojson)
    pathOfInterest = eh.loadShapefile(pathLoc)
    
    return pathOfInterest, toMerge


def applyAreaLayer(location, isgeojson, pathLoc, column, doInvert=False):
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

    """
    pathOfInterest, toMerge = loadFiles(location, isgeojson, pathLoc)
    
    toMerge = toMerge.fillna(0)
    maxVal = toMerge[column].max()
    
    if doInvert:
        toMerge[column] = toMerge[column].apply(lambda x: maxVal - x)
    
    # Normalize the Area Layer column
    new_col_name = column + '_Normalized'
    toMerge[new_col_name] = toMerge[column].apply(lambda x: x / maxVal)
    
    if location == f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp':
        print('This is the area function: ', toMerge[new_col_name], 'This is the length: ', len(toMerge[new_col_name]), new_col_name)

    mergedData = gpd.sjoin(pathOfInterest, toMerge, how='left', predicate='within')
    
    return mergedData


def averageValues(gdf, column, weight):
    # TODO: average values over corridor
    mean = gdf[column].mean()
    
    name = column + '_Weighted_Average'
    
    weighted_avg = (mean * weight)
    gdf[name] = weighted_avg
    
    
    if column == 'SRC2ERTA_Normalized':
        print(gdf[column])
        print (weighted_avg, mean, weight)
        
    return gdf, weighted_avg
    
    
def applyPointLayer(location: str, isgeojson: bool, pathLoc: str, distanceThreshold: int, colName: str, weight: int):
    pathOfInterest, toMerge = loadFiles(location, isgeojson, pathLoc)
        
    # distanceThreshold is divided by 111319 to convert from decimal degrees to meters
    threshold = distanceThreshold/111319
    
    
    filtered = atsc.filter_points_by_distance(toMerge, pathOfInterest, threshold)

    count = len(filtered)
    length = sum(pathOfInterest["LENGTH"])
    # Number of point layer item averaged according to the length of the entire corridor (in miles)
    name = colName + '_Weighted'
    
    weighted_points = (count/length) * weight
    pathOfInterest[name] = weighted_points
    
    return pathOfInterest, weighted_points


def combineToSingle(corridors, name):
    name = name + "_Combined"

    combined = pd.concat(corridors, ignore_index=True)

    combined.to_file(f"{top_dir}/data/paths_of_interest/{name}.shp")


if __name__ == "__main__":
    '''
    change 'location' based on shapefile of interest
    Electrification Area Layers
    '''
    # location = f'{top_dir}/costs_per_mile.geojson' #TCO
    
    isArea = True
    isgeojson = True
    doInvert = True

    # path, isarealayer, column of interest/point layer name, rank, max point consideration distance
    electrification_locations = [(f'{top_dir}/costs_per_mile.geojson', isArea, '$_mi_tot', 1, doInvert),
                                  (f'{top_dir}/data_paper/trucking_energy_demand.geojson', isArea, 'Perc Gen', 2, doInvert),
                                  (f'{top_dir}/data_paper/Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_400.0_chargingtime_4.0_maxwait_2.0.geojson', False, 'Chargers', 3, 1113190),
                                  (f'{top_dir}/data_paper/fuel_use_incentives.geojson', isArea, 'Electricit', 4, False),
                                  (f'{top_dir}/emissions_per_mile.geojson', isArea, 'C_mi_tot', 5, doInvert)
                                  ]
    
    
    
    # (f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp', True, 'SRC2ERTA1', 1), 

    # location = f'{top_dir}/data/Truck_Stop_Parking/truck_stop_parking_ds_truck_parking_2019_04_09.shp'
    # 965606 = 600mi   
    # SRC2ERTA: eGRID subregion annual CO2 equivalent total output emission rate (lb/MWh)
    # (f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp', isArea, 'SRC2ERTA', 4, doInvert),

    # column = 'SRC2ERTA' # life cycle assesment
    # (f'{top_dir}/emissions_per_mile.geojson', isArea, 'C_mi_tot', 4, False)
    # electrification_locations = [(f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer_operational.shp', False, 'Operational_Electrolyzers', 1, 107316262956),
    #                               (f'{top_dir}/data_paper/US_hy.geojson', False, 'Hydrogen_Stations', 2, 11131900),
    #                               (f'{top_dir}/data_paper/fuel_use_incentives.geojson', isArea, 'Hydrogen', 3, False),
    #                               (f'{top_dir}/data_paper/eia2022_state_merged.geojson', isArea, 'CO2_rate', 4, doInvert),
    #                               ]
    

    
    # filename = 'pathgraph'
    # pathLoc = [f'{top_dir}/data/paths_of_interest/{filename}.shp' ]
    # pathLoc = f'{top_dir}/data/paths_of_interest/BayToSea.shp'
    # pathLocS = [f'{top_dir}/data/paths_of_interest/CrossCountry.shp', f'{top_dir}/data/paths_of_interest/BayToSea.shp', f'{top_dir}/data/paths_of_interest/WesFlo.shp' ]
    corridor_paths = [f'{top_dir}/data/paths_of_interest/TXCA.shp', f'{top_dir}/data/paths_of_interest/UTMN.shp', f'{top_dir}/data/paths_of_interest/MAFL.shp' ]

    
    # change 'column' based on column of interest

    
    # column = '$_mi_tot' #TCO
    
    corridors = []
    weights = []
    denom = 0
    N = len(electrification_locations)
    
    for i in electrification_locations:
        denom += N - i[3] + 1
        
    corridor_values = []
    # Note, there is a present inefficiency in iterating over the path rather than the data itself
    for path in corridor_paths:
        values = []
        for location in electrification_locations:
            if location[0].endswith('.geojson'):
                isgeojson = True # false for point layers
                            
            weight = (N - location[3] + 1)/denom
            weights.append(weight) # for data testing only 
    
            # For truck stops
            # applied = applyPointLayer(location=location, isgeojson=isgeojson, pathLoc=path, distanceThreshold=100, colName='Truck_Stops')
            # applied = applyPointLayer(location=location, isgeojson=isgeojson, pathLoc=path, distanceThreshold=(965606/2), colName='Operational_Electrolyzers')
            
            if location[1]:
                applied = applyAreaLayer(location[0], isgeojson, path, location[2], location[4])
                normalized_column = location[2] + '_Normalized'
                if normalized_column == 'SRC2ERTA_Normalized':
                    print(applied)
                averaged, weighted_avg = averageValues(applied, normalized_column, weight)
                values.append(weighted_avg)
                corridors.append(averaged)
            else:   
                applied, weighted_points = applyPointLayer(location[0], isgeojson, path, location[4], location[2], weight)
                values.append(weighted_points)
                corridors.append(applied)
        corridor_values.append(sum(values))
        
    # combineToSingle(corridors, 'trucking_paper_lifecycle')
    
    # applied = applyPointLayer(location=location, isgeojson=isgeojson, pathLoc=pathLoc, distanceThreshold=100, colName='Truck Stops')
    # applied.to_file(f"{top_dir}/data/paths_of_interest/BayToSea_Tester.shp")

    # return corridors

# corridors = main()
