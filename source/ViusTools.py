#!/usr/bin/env python3

"""
Created on Tue Mar 28 16:28:00 2023
@author: danikam
"""

import InfoObjects
import pandas as pd
import os
from pathlib import Path
import numpy as np

# Conversion from pounds to tons
LB_TO_TONS = 1/2000.

# function to return key for any value
def get_key_from_value(dict, value):
    '''
    Gets the first key associated with the specified value in the given dictionary
        
    Parameters
    ----------
    dict (dictionary): Dictionary in which to find the provided value
    
    value (any type): value to find the first associated key for in the dictionary

    Returns
    -------
    this_key (any type): First key in the dictionary associated with the provided value
        
    NOTE: In case the value isn't present, an error message is printed and the function returns 'None'
    '''
    for this_key, this_value in dict.items():
        if this_value == value:
            return this_key
 
    print(f'Value {value} does not exist in the provided dataframe')
    return None

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

def make_aggregated_df(df, range_map=InfoObjects.FAF5_VIUS_range_map):
    '''
    Makes a new dataframe with trip range and commodity columns aggregated according to the rules defined in the FAF5_VIUS_commodity_map and the provided range_map
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    range_map (dictionary): A python dictionary containing the mapping of FAF5 trip ranges to VIUS trip ranges. This is used to determine how to aggregate the trip range columns in the VIUS dataframe to produce the new trip range colunns in the output dataframe.

    Returns
    -------
    df_agg (pd.DataFrame): A pandas dataframe containing the VIUS data, with additional columns to: 1) contain percentages of ton-miles carried over aggregated trip range, and 2) contain percentages of loaded ton-miles spent carrying aggregated commodity categories.
        
    NOTE: None.
    '''
    
    # Make a deep copy of the VIUS dataframe
    df_agg = df.copy(deep=True)
    
    # Loop through all commodities in the VIUS dataframe and combine them as needed to produce the aggregated mapping defined in the FAF5_VIUS_commodity_map
    for commodity in InfoObjects.FAF5_VIUS_commodity_map:
        vius_commodities = InfoObjects.FAF5_VIUS_commodity_map[commodity]['VIUS']
        if len(vius_commodities) == 1:
            df_agg[commodity] = df[vius_commodities[0]]
        elif len(vius_commodities) > 1:
            i_comm = 0
            for vius_commodity in vius_commodities:
                if i_comm == 0:
                    df_agg_column = df[vius_commodity].fillna(0)
                else:
                    df_agg_column += df[vius_commodity].fillna(0)
                i_comm += 1
            df_agg[commodity] = df_agg_column.replace(0, float('NaN'))

            
    # Loop through all the ranges in the VIUS dataframe and combine them as needed to produce the aggregated mapping defined in the FAF5_VIUS_range_map
    for truck_range in range_map:
        vius_ranges = range_map[truck_range]['VIUS']
        if len(vius_ranges) == 1:
            df_agg[truck_range] = df[vius_ranges[0]]
        elif len(vius_ranges) > 1:
            i_range = 0
            for vius_range in vius_ranges:
                if i_range == 0:
                    df_agg_column = df[vius_range].fillna(0)
                else:
                    df_agg_column += df[vius_range].fillna(0)
                i_range += 1
            df_agg[truck_range] = df_agg_column.replace(0, float('NaN'))
                
    return df_agg

def add_GREET_class(df):
    '''
    Adds a column to the dataframe that specifies the GREET truck class, determined by a mapping of averaged loaded gross vehicle weight to weight classes
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data

    Returns
    -------
    df: The pandas dataframe containing the VIUS data, with an additional column containing the GREET class of each truck
        
    NOTE: None.
    '''
    df['GREET_CLASS'] = df.copy(deep=False)['WEIGHTAVG']
    
    df.loc[df['WEIGHTAVG'] >= 33000, 'GREET_CLASS'] = get_key_from_value(InfoObjects.GREET_classes_dict, 'Heavy GVW')
    df.loc[(df['WEIGHTAVG'] >= 19500)&(df['WEIGHTAVG'] < 33000), 'GREET_CLASS'] = get_key_from_value(InfoObjects.GREET_classes_dict, 'Medium GVW')
    df.loc[(df['WEIGHTAVG'] >= 8500)&(df['WEIGHTAVG'] < 19500), 'GREET_CLASS'] = get_key_from_value(InfoObjects.GREET_classes_dict, 'Light GVW')
    df.loc[df['WEIGHTAVG'] < 8500, 'GREET_CLASS'] = get_key_from_value(InfoObjects.GREET_classes_dict, 'Light-duty')
    return df
    
def get_annual_ton_miles(df, cSelection, truck_range, commodity, fuel='all', greet_class='all'):
    '''
    Calculates the annual ton-miles that each truck (row) in the VIUS dataframe satisfying requirements defined by cSelection carries the given commodity over the given trip range burning the given fuel
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    cSelection (pd.Series): Boolean criteria to apply basic selection to rows of the input dataframe
    
    truck_range (string): Name of the column of VIUS data containing the percentage of ton-miles carried over the given trip range
    
    commodity (string): Name of the column of VIUS data containing the percentage of ton-miles carrying the given commodity
    
    fuel (string): Name of the column of the VIUS data containing an integier identifier of the fuel used by the truck
    
    greet_class (string): Name of the column of the VIUS data containing an integer identifier of the GREET truck class

    Returns
    -------
    df: The pandas dataframe containing the VIUS data, with an additional column containing the GREET class of each truck
        
    NOTE: None.
    '''
    # Add the given fuel to the selection
    if not fuel=='all':
        cSelection = (df['FUEL'] == fuel) & cSelection
    
    if not greet_class=='all':
        cSelection = (df['GREET_CLASS'] == greet_class) & cSelection
            
    greet_class = df[cSelection]['GREET_CLASS']        # Truck class used by GREET
    annual_miles = df[cSelection]['MILES_ANNL']        # Annual miles traveled by the given truck
    avg_payload = (df[cSelection]['WEIGHTAVG'] - df[cSelection]['WEIGHTEMPTY']) * LB_TO_TONS    # Average payload (difference between average vehicle weight with payload and empty vehicle weight). Convert from pounds to tons.

    # If we're considering all commodities, no need to consider the average fraction of different commodities carried
    if truck_range=='all' and commodity=='all':
        annual_ton_miles = annual_miles * avg_payload      # Convert average payload from
    # If we're considering a particular commodity, we do need to consider the average fraction of the given commodity carried
    elif truck_range=='all' and (not commodity=='all'):
        f_commodity = df[cSelection][commodity] / 100.     # Divide by 100 to convert from percentage to fractional
        annual_ton_miles = annual_miles * avg_payload * f_commodity
    elif (not truck_range=='all') and (commodity=='all'):
        f_range = df[cSelection][truck_range] / 100.     # Divide by 100 to convert from percentage to fractional
        annual_ton_miles = annual_miles * avg_payload * f_range
    elif (not truck_range=='all') and (not commodity=='all'):
        f_range = df[cSelection][truck_range] / 100.     # Divide by 100 to convert from percentage to fractional
        f_commodity = df[cSelection][commodity] / 100.
        annual_ton_miles = annual_miles * avg_payload * f_range * f_commodity
    
    return annual_ton_miles

def get_df_vius():
    '''
    Reads in the VIUS data as a pandas dataframe
        
    Parameters
    ----------
    None

    Returns
    -------
    df_vius (pd.DataFrame): A pandas dataframe containing the VIUS data
        
    NOTE: None.
    '''
    top_dir = get_top_dir()
    df_vius = pd.read_csv(f'{top_dir}/data/VIUS_2002/bts_vius_2002_data_items.csv')
    df_vius = add_GREET_class(df_vius)
    df_vius = make_aggregated_df(df_vius)
    return df_vius

def make_class_fuel_dist(commodity='all'):
    '''
    Reads in the VIUS data, and produces a normalized distribution of ton-miles carried by the given commodity, with respect to GREET truck class (Heavy GVW, Medium GVW and Light GVW) and fuel type (diesel or gasoline)
        
    Parameters
    ----------
    commodity (string): Commodity for which to evaluate ton-miles carried

    Returns
    -------
    class_fuel_dist (dictionary): Dictionary containing:
        - 'normalized distribution' (1D numpy.array): Distribution of ton-miles of the given commodity carried by each GREET class and fuel type, normalized to unit sum over all bins
        - 'statistical uncertainty' (1D numpy.array): Statistical uncertainty associated with the 'normalized distribution' array
        - 'names' (list): list of human-readable strings indicating the GREET glass and fuel type for each element in the associated distribution
        
    NOTE: None.
    '''
    
    # Read in the VIUS data as a pandas dataframe
    df = get_df_vius()
    
    # Apply basic selections
    cNoPassenger = (df['PPASSENGERS'].isna()) | (df['PPASSENGERS'] == 0)
    cBaseline = (~df['GREET_CLASS'].isna()) & (~df['MILES_ANNL'].isna()) & (~df['WEIGHTEMPTY'].isna()) & (~df['FUEL'].isna()) & cNoPassenger
    
    cCommodity = True
    
    if not commodity == 'all':
        commodity_threshold=0
        cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
        
    cSelection = cCommodity&cBaseline
    
    # Dictionary to contain string identifier of each class+fuel combo ('names'), and the associated distribution and statistical uncertainty of ton-miles with respect to the class+fuel combos (normalized such that the distribution sums to 1)
    class_fuel_dist = {'names': [], 'normalized distribution': np.zeros(0), 'statistical uncertainty': np.zeros(0)}
    
    # Loop through all fuel types and GREET classes
    for fuel in ['Diesel', 'Gasoline']:
        for greet_class in ['Heavy GVW', 'Medium GVW', 'Light GVW']:
            class_fuel_dist['names'].append(f'{greet_class} ({fuel})')
            
            # Get the integer identifier associated with the given fuel in the VIUS data
            i_fuel = get_key_from_value(InfoObjects.fuels_dict, fuel)
            if i_fuel is None:
                exit()
            
            # Get the integer identifier associated with the evaluated GREET class in the VIUS dataframe
            i_greet_class = get_key_from_value(InfoObjects.GREET_classes_dict, greet_class)
            if i_greet_class is None:
                exit()
            
            # Calculate the annual ton-miles reported carrying the given commodity by the given GREET truck class and fuel type for each truck passing cSelection
            annual_ton_miles = get_annual_ton_miles(df, cSelection=cSelection, truck_range='all', commodity=commodity, fuel=i_fuel, greet_class=i_greet_class)
            
            # Sum over all trucks passing cSelection
            class_fuel_dist['normalized distribution'] = np.append(class_fuel_dist['normalized distribution'], np.sum(annual_ton_miles))
            
            # Calculate the associated statistical uncertainty using the root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
            class_fuel_dist['statistical uncertainty'] = np.append(class_fuel_dist['statistical uncertainty'], np.sqrt(np.sum(annual_ton_miles**2)))
            

    # Normalize the distribution of annual ton miles and associated stat uncertainty such that the distribution of annual ton miles sums to 1
    class_fuel_dist_sum = np.sum(class_fuel_dist['normalized distribution'])
    class_fuel_dist['normalized distribution'] = class_fuel_dist['normalized distribution'] / class_fuel_dist_sum
    class_fuel_dist['statistical uncertainty'] = class_fuel_dist['statistical uncertainty'] / class_fuel_dist_sum
    
    return class_fuel_dist
    
def plot_distribution(distribution, uncertainty, bin_names, title, str_save, bin_height_title=''):
    '''
    Plots the given distribution, with error bars
        
    Parameters
    ----------
    distribution (1D numpy.array): Distribution to plot
    
    uncertainty (1D numpy.array): Uncertainty associated with the distribution to plot
    
    bin_names (list): Names to give each bin in the x-axis label
    
    title (string): Title of the plot
    
    str_save (string): Filename of the plot when saving as a pdf/png image
    
    bin_height_title (string): Optional y-axis label to describe the bin heights

    Returns
    -------
    df_vius (pd.DataFrame): A pandas dataframe containing the VIUS data
        
    NOTE: None.
    '''
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    
    fig = plt.figure(figsize = (10, 7))
    plt.title(title, fontsize=18)
    plt.ylabel(bin_height_title, fontsize=18)
    
    plt.bar(bin_names, distribution, yerr=uncertainty, width = 0.4, ecolor='black', capsize=5)
    plt.xticks(rotation=30, ha='right')
    
    plt.tight_layout()
    plt.savefig(f'plots/{str_save}.png')
    plt.savefig(f'plots/{str_save}.pdf')
    plt.close()

def main():
    commodities_list = list(InfoObjects.FAF5_VIUS_commodity_map)
    commodities_list.append('all')
    for commodity in commodities_list:
        if commodity=='all':
            str_save = f"norm_dist_greet_class_fuel_commodity_all"
        else:
            str_save = f"norm_dist_greet_class_fuel_commodity_{InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name']}"
        class_fuel_dist = make_class_fuel_dist(commodity)
        plot_distribution(distribution=class_fuel_dist['normalized distribution'], uncertainty=class_fuel_dist['statistical uncertainty'], bin_names=class_fuel_dist['names'], title=f'Distribution of ton-miles carrying {commodity}\n(normalized to unit sum)', str_save=str_save)

main()
