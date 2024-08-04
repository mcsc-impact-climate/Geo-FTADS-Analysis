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
    toMerge = eh.loadShapefile(location, isgeojson)
    pathOfInterest = eh.loadShapefile(pathLoc)

    return toMerge, pathOfInterest


def applyAreaLayer(location, isgeojson, pathLoc):
    """
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

    mergedData = gpd.sjoin(pathOfInterest, toMerge, how="left", predicate="within")

    return mergedData


def averageValues(gdf, column):
    # TODO: average values over corridor
    mean = gdf[column].mean()

    name = column + "_Average"

    gdf[name] = mean

    return gdf


def applyPointLayer(
    location: str, isgeojson: bool, pathLoc: str, distanceThreshold: int, colName: str
):
    toMerge, pathOfInterest = loadFiles(location, isgeojson, pathLoc)

    # distanceThreshold is divided by 111139 to convert from decimal degrees to meters
    threshold = distanceThreshold / 111139

    filtered = atsc.filter_points_by_distance(toMerge, pathOfInterest, threshold)

    count = len(filtered)
    length = sum(pathOfInterest["LENGTH"])
    # Number of point layer item averaged according to the length of the entire corridor (in miles)
    pathOfInterest[colName] = count / length

    return pathOfInterest


def combineToSingle(corridors, name):
    name = name + "_Combined"

    combined = pd.concat(corridors, ignore_index=True)

    combined.to_file(f"{top_dir}/data/paths_of_interest/{name}.shp")


if __name__ == "__main__":
    # change 'location' based on shapefile of interest
    # location = f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp'
    # location = f'{top_dir}/costs_per_mile.geojson'
    # isgeojson = True

    # location = f'{top_dir}/data/Truck_Stop_Parking/truck_stop_parking_ds_truck_parking_2019_04_09.shp'
    location = f"{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer_operational.shp"
    isgeojson = False

    filename = "pathgraph"
    # pathLoc = [f'{top_dir}/data/paths_of_interest/{filename}.shp' ]
    # pathLoc = f'{top_dir}/data/paths_of_interest/BayToSea.shp'
    pathLocS = [
        f"{top_dir}/data/paths_of_interest/CrossCountry.shp",
        f"{top_dir}/data/paths_of_interest/BayToSea.shp",
        f"{top_dir}/data/paths_of_interest/WesFlo.shp",
    ]

    # change 'column' based on column of interest
    # SRC2ERTA: eGRID subregion annual CO2 equivalent total output emission rate (lb/MWh)
    # column = 'SRC2ERTA'

    column = "$_mi_tot"

    corridors = []

    for path in pathLocS:
        # applied = applyAreaLayer(location, isgeojson, path)
        # applied = applyPointLayer(location=location, isgeojson=isgeojson, pathLoc=path, distanceThreshold=100, colName='Truck_Stops')
        # 965606 = 600mi
        applied = applyPointLayer(
            location=location,
            isgeojson=isgeojson,
            pathLoc=path,
            distanceThreshold=(965606 / 2),
            colName="Operational_Electrolyzers",
        )

        # averaged = averageValues(applied, column)

        # corridors.append(averaged)
        corridors.append(applied)

    combineToSingle(corridors, "CrossBayFlo_hydrogen")

    # applied = applyPointLayer(location=location, isgeojson=isgeojson, pathLoc=pathLoc, distanceThreshold=100, colName='Truck Stops')
    # applied.to_file(f"{top_dir}/data/paths_of_interest/BayToSea_Tester.shp")

    # return corridors

# corridors = main()
