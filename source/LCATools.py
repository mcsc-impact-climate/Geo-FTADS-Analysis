#!/usr/bin/env python3
"""
Created on Thu Mar 9 15:41:00 2023

@author: danikam
"""
import csv
import os
import pandas as pd

TONNES_TO_TONS = 1.10231
KM_TO_MILES = 0.621371


def getDir():
    '''
    Get the top level directory of the GitHub repo
    
    Parameters
    ----------
    None

    Returns
    -------
    Path to top level of GitHub
    
    '''
    path = os.getcwd()
    #print("Current Directory", path)
 
    # prints parent directory
    #print('Parent Directory', os.path.abspath(os.path.join(path, os.pardir)))
    top_dir = os.path.dirname(path)
    return top_dir
    
def readGreetWtwTruck(csv_path):
    '''
    Read in a csv file containing GREET outputs for the trucking well-to-wheels (WTW) module, and reformats to match the rail module
    
    Parameters
    ----------
    csv_path (string): Path to csv file containing GREET outputs

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu/ton-mile], fuel use [Gallons/ton-mile], or emissions p[g/ton-mile] for the trucking module
    
    '''
    # Read in the csv as a pandas dataframe
    df_lca = pd.read_csv(csv_path)
    
    # Reformat columns into well-to-pump (WTP) and pump-to-wheel (PTW)
    df_lca = df_lca.rename(columns={'Vehicle Operation': 'PTW'})
    df_lca = df_lca.rename(columns={'Total': 'WTW'})
    df_lca['WTP'] = df_lca['Feedstock'] + df_lca['Fuel']
    df_lca = df_lca.drop(['Feedstock', 'Fuel'], axis=1)
    #print(df_lca.columns)
    
    return df_lca
    
def readGreetWtwRail(csv_path):
    '''
    Read in a csv file containing GREET outputs for the rail well-to-wheels (WTW) module
    
    Parameters
    ----------
    csv_path (string): Path to csv containing GREET outputs

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu], fuel use [Gallons], or emissions p[g/ton-mile] for the rail module
    
    '''
    
    # Read in the csv as a pandas dataframe
    df_lca = pd.read_csv(csv_path)
    #print(df_lca.columns)
    return df_lca
    
def readGreetWthShip(csv_path_feedstock, csv_path_conversion, csv_path_combustion):
    '''
    Read in csv files containing GREET outputs for the ship well-to-hull (WTH) module
    
    Parameters
    ----------
    csv_path_feedstock (string): Path to csv file containing GREET outputs for marine fuel feedstock (emissions in g/million tonne-km)
    
    csv_path_conversion (string): Path to csv file containing GREET outputs for marine fuel conversion
    
    csv_path_combustion (string): Path to csv file containing GREET outputs for marine fuel combustion

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu], fuel use [Gallons], or emissions p[g/ton-mile] for the ship module
    
    '''
    
    # Read in the csv as a pandas dataframe and convert the emissions from g/million tonne-km to g/ton-mile
    df_lca_feedstock = pd.read_csv(csv_path_feedstock)
    df_lca_feedstock['Trip'] = df_lca_feedstock['Trip'] * (1./1e6) * (1./TONNES_TO_TONS) * (1./KM_TO_MILES)
    
    df_lca_conversion = pd.read_csv(csv_path_conversion)
    df_lca_conversion['Trip'] = df_lca_conversion['Trip'] * (1./1e6) * (1./TONNES_TO_TONS) * (1./KM_TO_MILES)
    
    df_lca_combustion = pd.read_csv(csv_path_combustion)
    df_lca_combustion['Trip'] = df_lca_combustion['Trip'] * (1./1e6) * (1./TONNES_TO_TONS) * (1./KM_TO_MILES)
    
    # Combine the dataframes into a single dataframe with the WTP / PTH / WTH structure
    df_lca = pd.DataFrame([df_lca_feedstock['Item']]).transpose()
    df_lca['WTP'] = df_lca_feedstock['Trip'] + df_lca_conversion['Trip']
    df_lca['PTH'] = df_lca_combustion['Trip']
    df_lca['WTH'] = df_lca['WTP'] + df_lca['PTH']
    
    #print(df_lca['WTH'])
    return df_lca
    
    
def main():
    top_dir = getDir()
    df_lca_dict = {}
    df_lca_dict['truck'] = readGreetWtwTruck(f'{top_dir}/data/GREET_LCA/truck_combination_long_haul_diesel_wtw.csv')
    df_lca_dict['rail'] = readGreetWtwRail(f'{top_dir}/data/GREET_LCA/rail_freight_diesel_wtw.csv')
    df_lca_dict['ship'] = readGreetWthShip(f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_feedstock.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_conversion.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_combustion.csv')
    
main()
                              




