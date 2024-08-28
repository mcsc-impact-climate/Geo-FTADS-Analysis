#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 09:24:00 2023
Last updated: Fri Jun 28 10:21:00 2023

@author: danikam
"""

# Import needed modules

import pandas as pd
from CommonTools import get_top_dir, mergeShapefile, saveShapefile, state_names_to_abbr
import os

LB_PER_KG = 2.20462
HOURS_PER_YEAR = 365 * 24
KWH_PER_MWH = 1000
G_PER_LB = 453.592
MW_PER_GW = 1000
MWH_PER_GWH = 1000


def read_ba_emissions_data(top_dir):
    """
    Reads in grid emission intensities by balancing authorities from eGRIDS

    Parameters
    ----------
    top_dir (string): path to the top level of the git repo

    Returns
    -------
    egrid_data (pd.DataFrame): A pandas dataframe containing the 2022 eGrid data for each subregion (lb CO2 / MWh)

    """

    # Read in the data associated with each eGrids subregion
    dataPath = f"{top_dir}/data/egrid2022_data.xlsx"
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, "SRL22", skiprows=[0])

    # Select the columns of interest
    # SUBRGN: eGRID sub-region acronym
    # SRCO2RTA: eGRID subregion annual CO2 emission rate (lb CO2 / MWh)
    data_df = data_df.filter(
        ["SUBRGN", "SRCO2RTA"], axis=1
    )  # , 'SRCLPR', 'SROLPR', 'SRGSPR', 'SRNCPR', 'SRHYPR', 'SRBMPR', 'SRWIPR', 'SRSOPR', 'SRGTPR', 'SROFPR', 'SROPPR'], axis=1)

    # Rename SRCO2RTA in the merged dataframe to a more generic descriptor
    # Note: SUBRGN naming needed to match associated column name in shapefile
    data_df = data_df.rename(columns={"SRCO2RTA": "CO2_rate", "SUBRGN": "ZipSubregi"})

    return data_df
    
def read_iso_emissions_data(top_dir):
    '''
    Reads in grid emission intensities by ISO from https://www.electricitymaps.com/data-portal (processed by Noman Bashir)
    
    Parameters
    ----------
    top_dir (string): path to the top level of the git repo

    Returns
    -------
    iso_emissions_data_df (pd.DataFrame): Dataframe containing the emissions data for each US ISO, converted from units of gCO2eq / kWh to lb CO2eq / MWh
    '''
    columns = ['zoneName']
    for hour in range(24):
        columns.append(f'mean_{hour}')
        columns.append(f'std_{hour}')
    
    data_df = pd.DataFrame(columns=columns)
    
    # Read in the data associated with each eGrids subregion
    dataDir = f'{top_dir}/data/daily_carbon_intensity_data_usa'
    for filename in os.listdir(dataDir):
        filepath = os.path.join(dataDir, filename)
        
        # Confirm that it's a file and not a directory
        if os.path.isfile(filepath) and filename.endswith('.csv'):
            data_iso_df = pd.read_csv(filepath)
            row_dict = {
                'zoneName': filename.split('_')[0]
            }
            
            for hour in range(24):
                row_dict[f'mean_{hour}'] = data_iso_df['mean'].iloc[hour]
                row_dict[f'std_{hour}'] = data_iso_df['std'].iloc[hour]
        
            # Convert row_dict to a DataFrame
            new_row_df = pd.DataFrame([row_dict])

            # Append new_row_df to data_df
            data_df = pd.concat([data_df, new_row_df], ignore_index=True)

    return data_df

def read_state_emissions_data(top_dir):
    """
    Reads in grid emission intensities by state from EIA

    Parameters
    ----------
    top_dir (string): path to the top level of the git repo

    Returns
    -------
    data_df (pd.DataFrame): A pandas dataframe containing the 2022 emission intensity data (lb CO2 / MWh)

    """

    # Read in the data associated with each eGrids subregion
    dataPath = f"{top_dir}/data/emissions_region2022.xlsx"
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, "State", skiprows=[0])

    # Select the columns of interest
    data_df = data_df.filter(
        [
            "Year",
            "Census Division and State",
            "Kilograms of CO2 per Megawatthour of Generation",
        ],
        axis=1,
    )

    # Rename the long columns
    data_df = data_df.rename(
        columns={
            "Census Division and State": "STUSPS",
            "Kilograms of CO2 per Megawatthour of Generation": "CO2_rate",
        }
    )

    # Convert the CO2 rate from kg / MWh to lb / MWh
    data_df["CO2_rate"] = data_df["CO2_rate"] * LB_PER_KG

    # Select rows corresponding to year 2022
    data_df = data_df[data_df["Year"] == 2022]

    # Update the state name to its associated abbreviation
    data_df = state_names_to_abbr(data_df, "STUSPS")

    # Remove NaN rows that aren't associated with states
    data_df = data_df.dropna()

    return data_df


def read_state_capacity_data(top_dir):
    """
    Reads in grid generating capacity by state

    Parameters
    ----------
    top_dir (string): path to the top level of the git repo

    Returns
    -------
    state_capacity_data_df (pd.DataFrame): A pandas dataframe containing the 2022 electricity generating capacity (MW) for each state
    """

    # Read in the data associated with each eGrids subregion
    dataPath = f"{top_dir}/data/existcapacity_annual.xlsx"
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, "Existing Capacity", skiprows=[0])
    state_capacity_data_df = data_df[
        (data_df["Year"] == 2022)
        & (data_df["Producer Type"] == "Total Electric Power Industry")
        & (data_df["Fuel Source"] == "All Sources")
    ]

    state_capacity_data_df = state_capacity_data_df.drop(
        columns=[
            "Fuel Source",
            "Generators",
            "Facilities",
            "Nameplate Capacity (Megawatts)",
            "Producer Type",
            "Year",
        ]
    )

    state_capacity_data_df = state_capacity_data_df.rename(
        columns={"State Code": "STUSPS", "Summer Capacity (Megawatts)": "Cap_MW"}
    )
    state_capacity_data_df["Cap_GW"] = (
        state_capacity_data_df["Cap_MW"].astype("float") / MW_PER_GW
    )

    return state_capacity_data_df


def read_state_generation_data(top_dir):
    """
    Reads in annual grid electricity generation by state

    Parameters
    ----------
    top_dir (string): path to the top level of the git repo

    Returns
    -------
    state_generation_data_df (pd.DataFrame): A pandas dataframe containing electricity generated (GWh) in each state for 2022
    """

    # Read in the data associated with each eGrids subregion
    dataPath = f"{top_dir}/data/annual_generation_state.xls"
    data = pd.ExcelFile(dataPath)
    data_df = pd.read_excel(data, skiprows=[0])
    state_generation_data_df = data_df[
        (data_df["YEAR"] == 2022)
        & (data_df["TYPE OF PRODUCER"] == "Total Electric Power Industry")
        & (data_df["ENERGY SOURCE"] == "Total")
    ]

    state_generation_data_df = state_generation_data_df.drop(
        columns=["TYPE OF PRODUCER", "ENERGY SOURCE", "YEAR"]
    )

    state_generation_data_df = state_generation_data_df.rename(
        columns={"STATE": "STUSPS", "GENERATION (Megawatthours)": "Ann_Gen"}
    )
    state_generation_data_df["Ann_Gen"] = (
        state_generation_data_df["Ann_Gen"].astype("float") / MWH_PER_GWH
    )  # Convert from MWh to GWh

    # Remove the US total
    state_generation_data_df = state_generation_data_df[
        state_generation_data_df["STUSPS"] != "US-Total"
    ]

    return state_generation_data_df


def combine_gen_cap_data(state_capacity_data_df, state_generation_data_df):
    """
    Combines generating and capacity data into a single dataframe, and also estimates the difference between the annual generating capacity and actual energy generated.

    Parameters
    ----------
    state_capacity_data_df (DataFrame): A pandas dataframe containing the 2022 electricity generating capacity (MW) for each state

    state_generation_data_df (pd.DataFrame): A pandas dataframe containing electricity generated in each state for 2022

    Returns
    -------
    state_gen_cap_data_df (pd.DataFrame): A pandas dataframe containing summary info
    """

    # Combine the two dataframes
    state_gen_cap_data_df = state_capacity_data_df.merge(
        state_generation_data_df, on="STUSPS", how="left"
    ).dropna()

    # Add a column with the theoretical annual generating capacity (GWh)
    state_gen_cap_data_df["Ann_Cap"] = state_gen_cap_data_df["Cap_GW"] * HOURS_PER_YEAR

    # Calculate the difference between theoretical and actual annual generation
    state_gen_cap_data_df["Ann_Diff"] = (
        state_gen_cap_data_df["Ann_Cap"] - state_gen_cap_data_df["Ann_Gen"]
    )

    # Calculate the ratio between theoretical maximum and actual annual generation
    state_gen_cap_data_df["Ann_Rat"] = (
        state_gen_cap_data_df["Ann_Cap"] / state_gen_cap_data_df["Ann_Gen"]
    )

    return state_gen_cap_data_df


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    # Read in the grid CO2 intensity by balancing authority from eGRIDS
    egrid_data = read_ba_emissions_data(top_dir)

    # Read in the state-level CO2 intensity from EIA
    eia_data = read_state_emissions_data(top_dir)

    # Read in the 2022 state-level generating capacity from EIA
    state_capacity_data = read_state_capacity_data(top_dir)

    # Read in 2022 state-level annual electricity generated from EIA
    state_generation_data = read_state_generation_data(top_dir)

    # Read in ISO emission rate data for 2022
    iso_emissions_data = read_iso_emissions_data(top_dir)
    
    # Combine the capacity and generation data
    state_gen_cap_data = combine_gen_cap_data(
        state_capacity_data, state_generation_data
    )

    # Merge the eGrids data in with the shapefile with subregion borders
    merged_dataframe_egrid = mergeShapefile(
        egrid_data,
        f"{top_dir}/data/eGRID2022_subregions/eGRID2022_Subregions.shp",
        "ZipSubregi",
    )

    # Merge the state-level CO2 intensity data with the state borders shapefile
    merged_dataframe_eia = mergeShapefile(
        eia_data, f"{top_dir}/data/state_boundaries/tl_2012_us_state.shp", "STUSPS"
    )
    merged_dataframe_eia = merged_dataframe_eia.drop(
        columns=["AWATER", "ALAND", "Shape_Area"]
    )

    # Merge the state-level 2022 capacity and generation data with the state borders shapefile
    merged_dataframe_gen_cap = mergeShapefile(
        state_gen_cap_data,
        f"{top_dir}/data/state_boundaries/tl_2012_us_state.shp",
        "STUSPS",
    )
    merged_dataframe_gen_cap = merged_dataframe_gen_cap.drop(
        columns=["AWATER", "ALAND", "Shape_Area"]
    )

    # Merge the iso emission rate data for 2022 with the shapefile containing borders for the data source
    merged_dataframe_iso_emissions = mergeShapefile(iso_emissions_data, f'{top_dir}/data/world.geojson', 'zoneName').dropna().drop(columns=['countryKey', 'countryName'])

    # Save the merged shapefiles
    saveShapefile(
        merged_dataframe_egrid,
        f"{top_dir}/data/egrid2022_subregions_merged/egrid2022_subregions_merged.shp",
    )

    saveShapefile(
        merged_dataframe_eia,
        f"{top_dir}/data/eia2022_state_merged/eia2022_state_merged.shp",
    )

    saveShapefile(
        merged_dataframe_gen_cap,
        f"{top_dir}/data/eia2022_state_merged/gen_cap_2022_state_merged.shp",
    )
    
    saveShapefile(
      merged_dataframe_iso_emissions, 
      f"{top_dir}/data/emission_rate_by_iso.shp"
    )

main()
