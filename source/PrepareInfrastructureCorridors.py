#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 14:44:00 2023

@author: danikam
"""

# Import needed modules
import numpy as np
import pandas as pd
import geopandas as gpd
from CommonTools import get_top_dir, saveShapefile


def get_highway_corridor(df_roads, df_states, highway_name, in_states):
    """
    Reads in the roads and states shapefiles and filters for the East Coast I-95 HD ZEV corridor between Georgia and New Jersey

    Parameters
    ----------
    df_shapefile (pd.DataFrame): A pandas dataframe containing the shapefile info

    df_roads (string): Name of the column to be filtered on

    Returns
    -------
        df_highway (pd.DataFrame): Filtered shapefile
    """

    # Filter for the highway of interest
    df_highway = df_roads[df_roads["FULLNAME"] == highway_name]

    # Filter for the highway in the specified states
    bool_in_states = df_states["STUSPS"] == in_states[0]
    for state in in_states[1:]:
        bool_in_states = bool_in_states | (df_states["STUSPS"] == state)

    # Select the boundaries for the states of interest
    df_in_states = df_states[bool_in_states]

    # Convert the state boundaries to EPSG:4269 to match the roads shapefile
    df_in_states = df_in_states.to_crs(4269)

    # Get the spatial join of the highway and the states we want it to pass through
    df_highway = gpd.sjoin(df_highway, df_in_states)

    return df_highway


def get_longs(frame):
    """
    Gets the longitude coordinates associated with each row of a dataframe obtained from a shapefile

    Parameters
    ----------
    frame (pd.Series): Row of a geopandas dataframe obtained from a shapefile

    Returns
    -------
    longs (np.array): Array of longitudes for all geometric objects in the given row of the shapefile
    """
    xy = frame.geometry.xy
    longs = np.asarray(xy[0])
    return longs


def get_lats(frame):
    """
    Gets the latitude coordinates associated with each row of a dataframe obtained from a shapefile

    Parameters
    ----------
    frame (pd.Series): Row of a geopandas dataframe obtained from a shapefile

    Returns
    -------
    longs (np.array): Array of latitudes for all geometric objects in the given row of the shapefile
    """
    xy = frame.geometry.xy
    return np.asarray(xy[1])


def get_H2LA_corridor(df_roads):
    """
    Reads in the roads and states shapefiles and filters for the H2LA corridor connecting Houston to LA, including the Texas triangle

    Parameters
    ----------
    df_roads (pd.DataFrame): A pandas dataframe representing the U.S. roads shapefile

    Returns
    -------
    df_h2la (pd.DataFrame): Geospatial shapefile of highway sections constituting the H2LA corridor
    """

    # Filter for the highways of interest
    df_i10 = df_roads[df_roads["FULLNAME"] == "I- 10"]
    df_i35 = df_roads[df_roads["FULLNAME"] == "I- 35"]
    df_i45 = df_roads[df_roads["FULLNAME"] == "I- 45"]

    # Select sections of the I-10 with longitude between Houston and LA
    HOUSTON_LONG = -95.3698
    LA_LONG = -118.2437
    df_i10_longs = df_i10.apply(get_longs, axis=1)
    df_i10 = df_i10[df_i10_longs.apply(np.max) > LA_LONG]  # East of LA
    df_i10 = df_i10[df_i10_longs.apply(np.min) < HOUSTON_LONG]  # West of Houston

    # Select sections of the I-35 with latitude between San Antonio and Dallas
    SAN_ANTONIO_LAT = 29.4252
    DALLAS_LAT = 32.779167

    df_i35_longs = df_i35.apply(get_lats, axis=1)

    # North of San Antonio
    df_i35 = df_i35.loc[df_i35_longs.apply(np.max) > SAN_ANTONIO_LAT]

    # South of Dallas
    df_i35 = df_i35.loc[df_i35_longs.apply(np.min) < DALLAS_LAT]

    # Select sections of the I-45 with latitude between Houston and Dallas
    HOUSTON_LAT = 29.749907
    DALLAS_LAT = 32.779167

    df_i45_longs = df_i45.apply(get_lats, axis=1)

    # North of San Antonio
    df_i45 = df_i45.loc[df_i45_longs.apply(np.max) > HOUSTON_LAT]

    # South of Dallas
    df_i45 = df_i45.loc[df_i45_longs.apply(np.min) < DALLAS_LAT]

    df_h2la = pd.concat([df_i10, df_i35, df_i45])

    return df_h2la


def get_bay_area(top_dir):
    """
    Reads in a shapefile with the Bay Area county boundaries, and merge the counties together to get one boundary for all the counties

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_bay (pd.DataFrame): Geospatial dataframe represening the Bay Area boundary
    """

    df_bay = gpd.read_file(
        f"{top_dir}/data/bay_area_counties/bayarea_county.shp",
        columns=["geometry"],
    )

    # Combine all the county boundaries into one shapefile
    df_bay = df_bay.dissolve()
    return df_bay


def get_salt_lake_county(top_dir):
    """
    Reads in a shapefile with the Utah county boundaries, and get the boundary for the Salt Lake City boundary

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_salt_lake (pd.DataFrame): Geospatial dataframe represening the Salt Lake City boundary
    """

    df_utah_counties = gpd.read_file(
        f"{top_dir}/data/utah_counties/Counties.shp",
        columns=["geometry", "NAME"],
    )

    # Select the Salt Lake county
    df_salt_lake = df_utah_counties[df_utah_counties["NAME"] == "SALT LAKE"]

    return df_salt_lake


def get_northeast(top_dir):
    """
    Reads in a shapefile with the U.S. state boundaries, and get the combined boundary for the northeastern states

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_northeast (pd.DataFrame): Geospatial dataframe representing the combined boundary of the northeastern states
    """

    df_states = read_states_shapefile(top_dir)
    in_states = ["ME", "MA", "NH", "VT", "RI", "CT", "NY", "PA", "NJ"]

    # Filter for the states in the specified list
    bool_in_states = df_states["STUSPS"].isin(in_states)

    # Select the boundaries for the states of interest
    df_in_states = df_states[bool_in_states]

    # Combine all the state boundaries into one shapefile
    df_northeast = df_in_states.dissolve()

    return df_northeast


def read_states_shapefile(top_dir):
    """
    Reads in a shapefile with the U.S. state boundaries

    Parameters
    ----------
    top_dir (string): Path to the top level directory of the repository

    Returns
    -------
    df_states (pd.DataFrame): Geospatial dataframe represening the U.S. state boundaries
    """

    df_states = gpd.read_file(f"{top_dir}/data/state_boundaries/tl_2012_us_state.shp")
    df_states = df_states.filter(["STUSPS", "Shape_Area", "geometry"], axis=1)
    return df_states


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the US primary national roads shapefile as a pandas dataframe
    df_roads = gpd.read_file(
        f"{top_dir}/data/tl_2019_us_primaryroads/tl_2019_us_primaryroads.shp",
        columns=["FULLNAME"],
    )

    df_states = read_states_shapefile(top_dir)

    # Initialize a dictionary to contain geo dataframes for highway infrastructure projects
    dict_infrastructure = {}

    # Populate the dictionary with sections of the highway that HD ZEV projects are planned on
    dict_infrastructure["East Coast"] = get_highway_corridor(
        df_roads,
        df_states,
        highway_name="I- 95",
        in_states=["GA", "SC", "NC", "VA", "MD", "NJ", "DE", "PA"],
    )
    dict_infrastructure["Midwest"] = get_highway_corridor(
        df_roads, df_states, highway_name="I- 80", in_states=["IN", "IL", "OH"]
    )
    dict_infrastructure["LA"] = get_highway_corridor(
        df_roads, df_states, highway_name="I- 710", in_states=["CA"]
    )
    dict_infrastructure["H2LA"] = get_H2LA_corridor(df_roads)
    dict_infrastructure["BayArea"] = get_bay_area(top_dir)
    dict_infrastructure["SaltLake"] = get_salt_lake_county(top_dir)
    dict_infrastructure["Northeast"] = get_northeast(top_dir)

    # Save the shapefile for each corridor
    savepaths = {
        "East Coast": "eastcoast.shp",
        "Midwest": "midwest.shp",
        "LA": "la_i710.shp",
        "H2LA": "h2la.shp",
        "BayArea": "bayarea.shp",
        "SaltLake": "saltlake.shp",
        "Northeast": "northeast.shp",
    }

    for corridor in savepaths:
        df_save = dict_infrastructure[corridor][["geometry"]]
        saveShapefile(df_save, f"{top_dir}/data/hd_zev_corridors/{savepaths[corridor]}")


main()
