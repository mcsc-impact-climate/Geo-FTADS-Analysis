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
import pickle

# Conversion from pounds to tons
LB_TO_TONS = 1/2000.

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

top_dir = get_top_dir()

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
    df_vius = pd.read_csv(f'{top_dir}/data/VIUS_2002/bts_vius_2002_data_items.csv')
    df_vius = add_GREET_class(df_vius)
    df_vius = make_aggregated_df(df_vius)
    return df_vius
    
def make_basic_selections(df, commodity):
    '''
    Makes basic selections to be applied to the VIUS data for all analyses of loads carrying the given commodity
        
    Parameters
    ----------
    df (pandas.DataFrame): Dataframe containing the VIUS data

    Returns
    -------
    cSelection (pandas.Series): Series of booleans to specify which rows in the VIUS pandas dataframe will remain after the basic selections are applied
        
    NOTE: None.
    '''
    
    # Get the integer identifier associated with diesel in the VIUS data
    i_fuel = get_key_from_value(InfoObjects.fuels_dict, 'Diesel')
    if i_fuel is None:
        exit()
    
    cNoPassenger = (df['PPASSENGERS'].isna()) | (df['PPASSENGERS'] == 0)        # Only want to consider trucks loaded with commodities, not passengers
    cFuel = (df['FUEL'] == i_fuel)                                              # Currently only considering fuel
    cBaseline = (~df['GREET_CLASS'].isna()) & (~df['MILES_ANNL'].isna()) & (~df['WEIGHTEMPTY'].isna()) & (~df['FUEL'].isna()) & cNoPassenger
    
    cCommodity = True
    
    if not commodity == 'all':
        commodity_threshold=0
        cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
        
    cSelection = cCommodity&cBaseline&cFuel
    
    return cSelection

def make_class_fuel_dist(commodity='all'):
    '''
    Reads in the VIUS data, and produces a normalized distribution of ton-miles carried by the given commodity, with respect to GREET truck class (Heavy GVW, Medium GVW and Light GVW)
        
    Parameters
    ----------
    commodity (string): Commodity for which to evaluate ton-miles carried

    Returns
    -------
    class_fuel_dist (dictionary): Dictionary containing:
        - 'normalized distribution' (1D numpy.array): Distribution of ton-miles of the given commodity carried by each GREET class and fuel type, normalized to unit sum over all bins
        - 'statistical uncertainty' (1D numpy.array): Statistical uncertainty associated with the 'normalized distribution' array
        - 'names' (list): list of human-readable strings indicating the GREET glass for each element in the associated distribution
        
    NOTE: None.
    '''
    
    # Get the integer identifier associated with diesel in the VIUS data
    i_fuel = get_key_from_value(InfoObjects.fuels_dict, 'Diesel')
    if i_fuel is None:
        exit()
    
    # Read in the VIUS data as a pandas dataframe
    df = get_df_vius()
    
    # Make basic selections for the given commodity
    cSelection = make_basic_selections(df, commodity)
    
    # Dictionary to contain string identifier of each class+fuel combo ('names'), and the associated distribution and statistical uncertainty of ton-miles with respect to the class+fuel combos (normalized such that the distribution sums to 1)
    class_fuel_dist = {'class': [], 'normalized distribution': np.zeros(0), 'statistical uncertainty': np.zeros(0)}
    
    # Loop through all fuel types and GREET classes
    for greet_class in ['Heavy GVW', 'Medium GVW', 'Light GVW']:
        class_fuel_dist['class'].append(greet_class)
        
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
    
def make_commodities_list():
    commodities_list = list(InfoObjects.FAF5_VIUS_commodity_map)
    commodities_list.append('all')
    return commodities_list
    
def make_all_class_fuel_dists():
    commodities_list = make_commodities_list()
    all_class_fuel_dists = {}
    for commodity in commodities_list:
        all_class_fuel_dists[commodity] = make_class_fuel_dist(commodity)
    return all_class_fuel_dists
    
def calculate_payload_per_class(commodity='all'):

    # Read in the VIUS data as a pandas dataframe
    df = get_df_vius()
    
    # Make basic selections for the given commodity
    cSelection = make_basic_selections(df, commodity)
    
    # Dictionary to contain string identifier of each class ('class'), and the associated average payload and standard deviation (weighted by ton-miles) with respect to the class
    payload_class_dist = {'class': [], 'average payload': np.zeros(0), 'standard deviation': np.zeros(0)}
    
    for greet_class in ['Heavy GVW', 'Medium GVW', 'Light GVW']:
        # Get the integer identifier associated with the evaluated GREET class in the VIUS dataframe
        i_greet_class = get_key_from_value(InfoObjects.GREET_classes_dict, greet_class)
        
        if i_greet_class is None:
            exit()
    
        # Calculate the annual ton-miles reported carrying the given commodity by the given GREET truck class and fuel type for each truck passing cSelection
        annual_ton_miles = get_annual_ton_miles(df, cSelection=cSelection, truck_range='all', commodity=commodity, fuel='all', greet_class=i_greet_class)
        
        # Get the payloads for the given GREET class
        cGreetClass = True
        if not greet_class == 'all':
            cGreetClass = (~df['GREET_CLASS'].isna())&(df['GREET_CLASS'] == i_greet_class)
        payload = (df[cSelection&cGreetClass]['WEIGHTAVG'] - df[cSelection&cGreetClass]['WEIGHTEMPTY']) * LB_TO_TONS
        
        # Calculate the average payload and standard deviation for the given commodity and GREET class
        average_payload = np.average(payload, weights=annual_ton_miles)
        variance_payload = np.average((payload-average_payload)**2, weights=annual_ton_miles)
        std_payload = np.sqrt(variance_payload)
        
        # Fill in the payload distribution
        payload_class_dist['class'].append(greet_class)
        payload_class_dist['average payload'] = np.append(payload_class_dist['average payload'], average_payload)
        payload_class_dist['standard deviation'] = np.append(payload_class_dist['standard deviation'], std_payload)
        
    return payload_class_dist
        
def calculate_all_payloads_per_class():
    commodities_list = make_commodities_list()
    all_payloads_per_class = {}
    for commodity in commodities_list:
        all_payloads_per_class[commodity] = calculate_payload_per_class(commodity)
    return all_payloads_per_class
    
    
def calculate_payload_per_commodity(greet_class='all'):

    # Read in the VIUS data as a pandas dataframe
    df = get_df_vius()
    
    # Make basic selections for all commodities
    cBaseline = make_basic_selections(df, commodity='all')
    
    # Calculate mean payload and standard deviation for each commodity
    payload_dist = {
        'commodity': [],
        'average payload': np.zeros(0),
        'standard deviation': np.zeros(0)
    }
    
    if greet_class == 'all':
        i_greet_class = 'all'
    else:
        i_greet_class = get_key_from_value(InfoObjects.GREET_classes_dict, greet_class)
    
    commodities_list = list(InfoObjects.FAF5_VIUS_commodity_map)
    commodities_list.append('all')
    
    for commodity in commodities_list:
        cCommodity = True
    
        if not commodity == 'all':
            commodity_threshold=0
            cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
        
        cSelection = cCommodity&cBaseline
        
        cGreetClass = True
        if not greet_class == 'all':
            cGreetClass = (~df['GREET_CLASS'].isna())&(df['GREET_CLASS'] == i_greet_class)
        
        cSelection = cSelection&cGreetClass
        
        # Calculate the annual ton-miles reported carrying the given commodity passing cSelection
        annual_ton_miles = get_annual_ton_miles(df, cSelection=cSelection, truck_range='all', commodity=commodity, fuel='all', greet_class=i_greet_class)
        
        payload = (df[cSelection]['WEIGHTAVG'] - df[cSelection]['WEIGHTEMPTY']) * LB_TO_TONS
        
        # Calculate the mean payload, weighted by annual ton-miles carrying the given commodity
        average_payload = np.average(payload, weights=annual_ton_miles)
        variance_payload = np.average((payload-average_payload)**2, weights=annual_ton_miles)
        std_payload = np.sqrt(variance_payload)
        
        # Fill in the payload distribution
        payload_dist['commodity'].append(commodity)
        payload_dist['average payload'] = np.append(payload_dist['average payload'], average_payload)
        payload_dist['standard deviation'] = np.append(payload_dist['standard deviation'], std_payload)
    
    return payload_dist
        
    
def plot_bar(bar_heights, uncertainty, bin_names, title, str_save, bin_height_title='', horizontal_bars=False):
    '''
    Plots the given data as a bar plot, with error bars
        
    Parameters
    ----------
    distribution (1D numpy.array): Distribution to plot
    
    uncertainty (1D numpy.array): Uncertainty associated with the distribution to plot
    
    bin_names (list): Names to give each bin in the x-axis label
    
    title (string): Title of the plot
    
    str_save (string): Filename of the plot when saving as a pdf/png image
    
    bin_height_title (string): Optional label to describe the bin heights

    Returns
    -------
    df_vius (pd.DataFrame): A pandas dataframe containing the VIUS data
        
    NOTE: None.
    '''
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    
    if horizontal_bars:
        fig = plt.figure(figsize = (18, 12))
    else:
        fig = plt.figure(figsize = (10, 7))
    plt.title(title, fontsize=18)
    if horizontal_bars:
        plt.xlabel(bin_height_title, fontsize=18)
    else:
        plt.ylabel(bin_height_title, fontsize=18)
    
    if horizontal_bars:
        plt.barh(bin_names, bar_heights, xerr=uncertainty, ecolor='black', capsize=5)
    else:
        plt.bar(bin_names, bar_heights, yerr=uncertainty, width = 0.4, ecolor='black', capsize=5)
        
    if not horizontal_bars:
        plt.xticks(rotation=30, ha='right')
    
    plt.tight_layout()
    print(f'Saving figure to plots/{str_save}.png')
    plt.savefig(f'plots/{str_save}.png')
    plt.savefig(f'plots/{str_save}.pdf')
    plt.close()
    
def save_as_csv_per_class(all_class_dists, filename, info_name, unc_name):
    df_save = pd.DataFrame()
    
    # Make a column with the class names
    df_save['class'] = all_class_dists['all']['class']
    
    # Make a column for each commodity
    for commodity in all_class_dists:
        if commodity =='all':
            commodity_save = 'all commodities'
        else:
            commodity_save = commodity
        df_save[commodity_save] = all_class_dists[commodity][info_name]
        df_save[f'{commodity_save} (unc)'] = all_class_dists[commodity][unc_name]
    
    savePath = f'{top_dir}/data/VIUS_Results'
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    df_save.to_csv(f'{savePath}/{filename}_per_class.csv', index=False)
    print(f'Saving dataframe to {savePath}/{filename}_per_class.csv')

def main():
    # Evaluate and plot the distribution of ton-miles with respect to GREET class and fuel type for each commodity
    all_class_fuel_dists = make_all_class_fuel_dists()
    save_as_csv_per_class(all_class_fuel_dists, filename='norm_distribution', info_name='normalized distribution', unc_name='statistical uncertainty')

    for commodity in all_class_fuel_dists:
        if commodity=='all':
            str_save = f"norm_dist_greet_class_fuel_commodity_all"
            commodity_title='all commodities'
        else:
            str_save = f"norm_dist_greet_class_fuel_commodity_{InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name']}"
            commodity_title=commodity
        class_fuel_dist = all_class_fuel_dists[commodity]
        plot_bar(bar_heights=class_fuel_dist['normalized distribution'], uncertainty=class_fuel_dist['statistical uncertainty'], bin_names=class_fuel_dist['class'], title=f'Distribution of ton-miles carrying {commodity_title}\n(normalized to unit sum)', str_save=str_save)

    # Evaluate and plot the distribution of average payload with respect to GREET class for each commodity
    all_payloads_per_class = calculate_all_payloads_per_class()
    save_as_csv_per_class(all_payloads_per_class, filename='payload', info_name='average payload', unc_name='standard deviation')
    for commodity in all_payloads_per_class:
        if commodity=='all':
            str_save = f"average_payload_per_greet_class_commodity_all"
            commodity_title='all commodities'
        else:
            str_save = f"average_payload_per_greet_class_commodity_{InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name']}"
            commodity_title=commodity
        payload_class_dist = all_payloads_per_class[commodity]
        plot_bar(bar_heights=payload_class_dist['average payload'], uncertainty=payload_class_dist['standard deviation'], bin_names=payload_class_dist['class'], title=f'Average payload, weighted by ton-miles carrying {commodity}\nError bars are weighted standard deviation', str_save=str_save)

#    # Evaluate and plot the distribution of average payload (weighted by ton-miles carried) with respect to commodities
#    payload_per_commodity = calculate_payload_per_commodity()
#    plot_bar(bar_heights=payload_per_commodity['average payload'], uncertainty=payload_per_commodity['standard deviation'], bin_names=payload_per_commodity['commodity'], title=f'Average payload for each commodity, weighted by ton-miles carried\nError bars are weighted standard deviation', str_save='payload_per_commodity', bin_height_title='Average payload (tons)', horizontal_bars=True)
    
#    # Evaluate and plot the distribution of average payload (weighted by ton-miles carried) with respect to commodities within each class
#    for greet_class in ['Heavy GVW', 'Medium GVW', 'Light GVW']:
#        payload_per_commodity = calculate_payload_per_commodity(greet_class)
#        plot_bar(bar_heights=payload_per_commodity['average payload'], uncertainty=payload_per_commodity['standard deviation'], bin_names=payload_per_commodity['commodity'], title=f'Average payload for each commodity in the {greet_class} class, weighted by ton-miles carried\nError bars are weighted standard deviation', str_save=f"payload_per_commodity_{greet_class.replace(' ', '_')}", bin_height_title='Average payload (tons)', horizontal_bars=True)

main()
