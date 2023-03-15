#!/usr/bin/env python3
"""
Created on Thu Mar 9 15:41:00 2023

@author: danikam
"""
import csv
import os
import pandas as pd
from pathlib import Path

TONNES_TO_TONS = 1.10231    # tonnes per ton
KM_TO_MILES = 0.621371      # km per mile
PAYLOAD = 19.0402178166526  # Assumed payload for heavy duty truck, in tons (obtained from GREET default for comination long-haul truck)


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
    
def readSesameWtwTruck():
    '''
    Read in heavy duty vehicle fleet data for class 8 trucks from sesame-core submodule, with input parameters specified, and collect the CO2e emission rates
    
    Parameters
    ----------
    None

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing CO2e for the sesame HDV module
    
    '''
    import sys
    
    # Temporarily cd into the sesame-core module
    sys.path.append(os.getcwd() + '/sesame-core')
    os.chdir(os.getcwd() + '/sesame-core')
    
    # Import the fleet_HDV_stable python script to access its functions
    from analysis.system.fleet_HDV import fleet_HDV_stable as flt_hdv
    
    # Create an input set for the heavy-duty fleet model (currently using the same input as in fleet_HDV_stable.py)
    input_set = flt_hdv.InputSet(flt_hdv.FleetModel.inputs(), {
        #'region': 'US',
        'msps2': 'User',
        'growth_curve':'s curve',
        'msps1': 'Static',
        'size_share': '',
        'spp': 'AEO20',
        'delta_spp': '',
        'fuel_int': 'User',
        'delta_fuel': '',
        'h2_prod': 'SMR',
        'fgi': 'Yes',
        'cips': 'AEO20',
        'delta_I': '',
        'evmethod': '',
        'O': '',
        'D': '',
        'fhw': '',
        'fh': '',
        'fw': '',
        'Hd': '',
        'ap_gas': '',
        'car_longevity': 'Static',
        'delta_hl': '',
        'mode': '50',
        'd_future': 'Static',
        'delta_d_future': '',
        'd_a_future': 'Static',
        'delta_d_a_future': '',
        'pps': 'AEO20',
        'delta_p': '',
        'fuel_price_source': 'User',
        'gasoline_price_change': '0',
        'diesel_price_change': '0',
        'electricity_price_change': '0',
        'biofuel_price_change': '0',
        'biofuel_perc_vol_2050': 10,
        'bio_fuel_prod_e': 51,
        'h2_price_change': '0',
        'powertrain_size_share': {
            'class8': [100, 0, 0, 0, 0, 0]
        },
        'yp_BEV': 2030,
        'yp_FCEV': 2040,
    })
    
    #print(input_set['fuel_int'])
    input_set.validate()
    fleet = flt_hdv.FleetModel()
    fleet.prepare(input_set)
    results = fleet.compute_outputs()
    
    # Create a dataframe to contain the emission rates
    df_lca = pd.DataFrame(columns=['Item','WTP','PTW','WTW'])
    
    # Get the fuel production (WTP), tailpipe (PTW), and car production (PROD) emissions from the results, in g/mile CO2e, and divide by the typical payload to convert to g / ton-mile
    WTP = results['e_class8_2020']['ICED']['fuel production'] / PAYLOAD
    PTW = results['e_class8_2020']['ICED']['tailpipe'] / PAYLOAD
    WTW = WTP + PTW
    PROD = results['e_class8_2020']['ICED']['car production'] / PAYLOAD  # NOTE: This currently isn't being used, but I plan to once I get vehicle manufacturing emissions outputs from GREET
    
    # Save the emissions of interest to the dataframe
    df_lca = df_lca.append({'Item': 'CO2e', 'WTP': WTP, 'PTW': PTW, 'WTW': WTW}, ignore_index=True)
    
    # cd back out of the sesame-core module now that we're finished with it
    os.chdir(os.getcwd() + '/..')
        
    return df_lca
    
def main():
    # Get the path to the top level of the git repo
    source_path = Path(__file__).resolve()
    source_dir = source_path.parent
    top_dir = os.path.dirname(source_dir)

    # Initialize an empty dictionary to contain the LCA dataframes
    df_lca_dict = {}
    
    # From GREET outputs
    df_lca_dict['truck'] = readGreetWtwTruck(f'{top_dir}/data/GREET_LCA/truck_combination_long_haul_diesel_wtw.csv')
    df_lca_dict['rail'] = readGreetWtwRail(f'{top_dir}/data/GREET_LCA/rail_freight_diesel_wtw.csv')
    df_lca_dict['ship'] = readGreetWthShip(f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_feedstock.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_conversion.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_combustion.csv')

    # From SESAME
    df_lca_dict['truck_sesame'] = readSesameWtwTruck()
    
    # print(df_lca_dict['truck'])
    # print(df_lca_dict['truck_sesame'])
    
main()
                              




