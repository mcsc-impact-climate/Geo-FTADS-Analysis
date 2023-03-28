#!/usr/bin/env python3

"""
Created on Mon Mar 27 10:28:00 2023
@author: danikam
"""

# Import needed modules
import numpy as np
import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib
import InfoObjects
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)

# Conversion from pounds to tons
LB_TO_TONS = 1/2000.

# Get the path to the top level of the git repo
source_path = Path(__file__).resolve()
source_dir = source_path.parent
top_dir = os.path.dirname(source_dir)

######################################### Functions defined here ##########################################

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
    
    df.loc[df['WEIGHTAVG'] >= 33000, 'GREET_CLASS'] = 1
    df.loc[(df['WEIGHTAVG'] >= 19500)&(df['WEIGHTAVG'] < 33000), 'GREET_CLASS'] = 2
    df.loc[(df['WEIGHTAVG'] >= 8500)&(df['WEIGHTAVG'] < 19500), 'GREET_CLASS'] = 3
    df.loc[df['WEIGHTAVG'] < 8500, 'GREET_CLASS'] = 4
    return df
    
def get_annual_ton_miles(df, cSelection, cRange, cCommodity, truck_range, commodity, fuel='all', greet_class='all'):
    '''
    Calculates the annual ton-miles that each truck (row) in the VIUS dataframe satisfying requirements defined by cSelection carries the given commodity over the given trip range burning the given fuel
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    cSelection (pd.Series): Boolean criteria to apply basic selection to rows of the input dataframe
    
    cRange (pd.Series): Boolean criterion to select samples that report carrying out some percentage of loaded trips covering a range specifed by parameter truck_range
    
    cCommodity (pd.Series): Boolean criterion to select samples that report carrying out some percentage of loaded trips carrying the commodity given by parameter commodity
    
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
    if type(cRange) == bool and type(cCommodity) ==  bool:
        annual_ton_miles = annual_miles * avg_payload      # Convert average payload from
    # If we're considering a particular commodity, we do need to consider the average fraction of the given commodity carried
    elif type(cRange) == bool and (not type(cCommodity) ==  bool):
        f_commodity = df[cSelection][commodity] / 100.     # Divide by 100 to convert from percentage to fractional
        annual_ton_miles = annual_miles * avg_payload * f_commodity
    elif (not type(cRange) == bool) and (type(cCommodity) ==  bool):
        f_range = df[cSelection][truck_range] / 100.     # Divide by 100 to convert from percentage to fractional
        annual_ton_miles = annual_miles * avg_payload * f_range
    elif (not type(cRange) == bool) and (not type(cCommodity) ==  bool):
        f_range = df[cSelection][truck_range] / 100.     # Divide by 100 to convert from percentage to fractional
        f_commodity = df[cSelection][commodity] / 100.
        annual_ton_miles = annual_miles * avg_payload * f_range * f_commodity
    
    return annual_ton_miles
    
def get_commodity_pretty(commodity='all'):
    '''
    Gets a human-readable name of the input commodity column name, using the mapping specified in the dictionary pretty_commodities_dict
        
    Parameters
    ----------
    commodity (string): Column name of the given commodity

    Returns
    -------
    commodity_pretty (string): Human-readable version of the input column name
        
    NOTE: None.
    '''
    if commodity == 'all':
        commodity_pretty = 'All commodities'
    else:
        commodity_pretty = InfoObjects.pretty_commodities_dict[commodity]
    return commodity_pretty
    
def get_region_pretty(region='US'):
    '''
    Gets a human-readable name of the input column name associated with the truck's administrative state or region (a.k.a. region), using the mapping specified in the dictionary states_dict
        
    Parameters
    ----------
    region (string): Column name of the given administrative state or region

    Returns
    -------
    region_pretty (string): Human-readable version of the input column name
        
    NOTE: None.
    '''
    if region == 'US':
        region_pretty = 'US'
    else:
        region_pretty = InfoObjects.states_dict[region]
    return region_pretty
    
def get_range_pretty(truck_range='all'):
    '''
    Gets a human-readable name of the input column name associated with the truck's trip range window, using the mapping specified in the dictionary pretty_range_dict
        
    Parameters
    ----------
    truck_range (string): Column name of the given trip range window

    Returns
    -------
    range_pretty (string): Human-readable version of the input column name
        
    NOTE: None.
    '''
    if truck_range == 'all':
        range_pretty = 'All Ranges'
    else:
        range_pretty = InfoObjects.pretty_range_dict[truck_range]
    return range_pretty

def print_all_commodities(df):
    '''
    Prints out the number of samples of each commodity in the VIUS, as well as the total number of commodities
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data

    Returns
    -------
    None
        
    NOTE: None.
    '''
    n_comm=0
    for column in df:
        if column.startswith('P') and not column.startswith('P_'):
            n_column = len(df[~df[column].isna()][column])
            print(f'Total number of samples for commodity {column}: {n_column}')
            n_comm += 1
    print(f'Total number of commodities: {n_comm}\n\n')
    
def print_all_states(df):
    '''
    Prints out the number of samples for each state in the VIUS, as well as the total number of samples
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data

    Returns
    -------
    None
        
    NOTE: None.
    '''
    n_samples=0
    for state in range(1,57):
        if not state in InfoObjects.states_dict: continue
        n_state = len(df[(~df['ADM_STATE'].isna())&(df['ADM_STATE']==state)]['ADM_STATE'])
        state_str = InfoObjects.states_dict[state]
        print(f'Total number of samples in {state_str}: {n_state}')
        n_samples += n_state
    print(f'total number of samples: {n_samples}\n\n')
    
def plot_greet_class_hist(df, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title='default', set_commodity_save='default', set_range_title='default', set_range_save='default', aggregated=False):
    '''
    Calculates and plots the distributions of GREET class and fuel type for different commodities ('commmodity' parameter), trip range windows ('truck_range' parameter), and administrative states ('region' parameter). Samples used to produce the distributions are weighted by the average annual ton-miles reported carrying the given 'commodity' over the given 'truck_range', for the given administrative 'region'.
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    commodity (string): Name of the column of VIUS data containing the percentage of ton-miles carrying the given commodity

    truck_range (string): Name of the column of VIUS data containing the percentage of ton-miles carried over the given trip range
    
    region (string): Name of the column of VIUS data containing boolean data to indicate the truck's administrative state
    
    range_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the truck_range is not 'all'
    
    commodity_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the commodity is not 'all'
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted commodity to be shown in the plot title
    
    set_commodity_save (string): Allows the user to set the keyword for the plotted commodity to be included in the filenames of the saved plots
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted trip range to be shown in the plot title
    
    set_range_save (string): Allows the user to set the keyword for the plotted trip range to be included in the filenames of the saved plots
    
    aggregated (boolean): If set to True, adds an additional string '_aggregated' to the filenames of the saved plots to indicate that aggregation has been done to obtain common commodity and/or trip range definitions between FAF5 and VIUS data
    
    Returns
    -------
    None
        
    NOTE: None.
    '''

    region_pretty = get_region_pretty(region)
    
    if set_commodity_title == 'default':
        commodity_pretty = get_commodity_pretty(commodity)
        commodity_title = commodity_pretty
    else:
        commodity_title = set_commodity_title
    
    if set_commodity_save == 'default':
        commodity_save = commodity
    else:
        commodity_save = set_commodity_save
        
    if set_range_title == 'default':
        range_pretty = get_range_pretty(truck_range)
        range_title = range_pretty
    else:
        range_title = set_range_title
    
    if set_range_save == 'default':
        range_save = truck_range
    else:
        range_save = set_range_save

    cNoPassenger = (df['PPASSENGERS'].isna()) | (df['PPASSENGERS'] == 0)
    cBaseline = (~df['GREET_CLASS'].isna()) & (~df['MILES_ANNL'].isna()) & (~df['WEIGHTEMPTY'].isna()) & (~df['FUEL'].isna()) & cNoPassenger
    cRange = True
    cCommodity = True
    cRegion = True
    if not truck_range == 'all':
        cRange = (~df[truck_range].isna())&(df[truck_range] > range_threshold)
    if not commodity == 'all':
        cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
    if not region == 'US':
        cRegion = (~df['ADM_STATE'].isna())&(df['ADM_STATE'] == region)
        
    cSelection = cRange&cRegion&cCommodity&cBaseline
    
    # Get the annual ton miles for all fuels
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
    # Bin the data according to the GREET vehicle class, and calculate the associated statistical uncertainty using root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
    fig = plt.figure(figsize = (10, 7))
    n, bins = np.histogram(df[cSelection]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_all)
    n_err = np.sqrt(np.histogram(df[cSelection]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_all**2)[0])
    plt.title(f'Commodity: {commodity_title}, Region: {region_pretty}\nRange: {range_title}', fontsize=20)
    plt.ylabel('Commodity flow (ton-miles)', fontsize=20)
    
    # Plot the total along with error bars (the bars themselves are invisible since I only want to show the error bars)
    plt.bar(InfoObjects.GREET_classes, n, yerr=n_err, width = 0.4, ecolor='black', capsize=5, alpha=0, zorder=1000)
    
    # Add in the distribution for each fuel, stacked on top of one another
    bottom = np.zeros(4)
    for i_fuel in [1,2,3,4]:
        cFuel = (df['FUEL'] == i_fuel) & cSelection
        
        annual_ton_miles_fuel = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel=i_fuel, greet_class='all')
        n, bins = np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel)
        n_err = np.sqrt(np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel**2)[0])
        plt.bar(InfoObjects.GREET_classes, n, width = 0.4, alpha=1, zorder=1, label=InfoObjects.fuels_dict[i_fuel], bottom=bottom)
        bottom += n
    plt.legend(fontsize=18)
    
    region_save = region_pretty.replace(' ', '_')
    aggregated_info=''
    if aggregated:
        aggregated_info = '_aggregated'
        
    plt.xticks(rotation=15, ha='right')
    
    plt.tight_layout()
    print(f'Saving figure to plots/greet_truck_class_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.png')
    plt.savefig(f'plots/greet_truck_class_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.png')
    plt.savefig(f'plots/greet_truck_class_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.pdf')
    #plt.show()
    plt.close()
    
def plot_age_hist(df, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title='default', set_commodity_save='default', set_range_title='default', set_range_save='default', aggregated=False):
    '''
    Calculates and plots the distributions of truck age and GREET truck class for different commodities ('commmodity' parameter), trip range windows ('truck_range' parameter), and administrative states ('region' parameter). Samples used to produce the distributions are weighted by the average annual ton-miles reported carrying the given 'commodity' over the given 'truck_range', for the given administrative 'region'.
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    commodity (string): Name of the column of VIUS data containing the percentage of ton-miles carrying the given commodity

    truck_range (string): Name of the column of VIUS data containing the percentage of ton-miles carried over the given trip range
    
    region (string): Name of the column of VIUS data containing boolean data to indicate the truck's administrative state
    
    range_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the truck_range is not 'all'
    
    commodity_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the commodity is not 'all'
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted commodity to be shown in the plot title
    
    set_commodity_save (string): Allows the user to set the keyword for the plotted commodity to be included in the filenames of the saved plots
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted trip range to be shown in the plot title
    
    set_range_save (string): Allows the user to set the keyword for the plotted trip range to be included in the filenames of the saved plots
    
    aggregated (boolean): If set to True, adds an additional string '_aggregated' to the filenames of the saved plots to indicate that aggregation has been done to obtain common commodity and/or trip range definitions between FAF5 and VIUS data
    
    Returns
    -------
    None
        
    NOTE: None.
    '''

    region_pretty = get_region_pretty(region)
    
    if set_commodity_title == 'default':
        commodity_pretty = get_commodity_pretty(commodity)
        commodity_title = commodity_pretty
    else:
        commodity_title = set_commodity_title
    
    if set_commodity_save == 'default':
        commodity_save = commodity
    else:
        commodity_save = set_commodity_save
        
    if set_range_title == 'default':
        range_pretty = get_range_pretty(truck_range)
        range_title = range_pretty
    else:
        range_title = set_range_title
    
    if set_range_save == 'default':
        range_save = truck_range
    else:
        range_save = set_range_save
    
    cNoPassenger = (df['PPASSENGERS'].isna()) | (df['PPASSENGERS'] == 0)
    cBaseline = (~df['WEIGHTAVG'].isna()) & (~df['MILES_ANNL'].isna()) & (~df['WEIGHTEMPTY'].isna()) & (~df['FUEL'].isna()) & (~df['ACQUIREYEAR'].isna()) & cNoPassenger
    cCommodity = True
    cRange = True
    cRegion = True
    if not commodity == 'all':
        cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
    if not truck_range == 'all':
        cRange = (~df[truck_range].isna())&(df[truck_range] > range_threshold)
    if not region == 'US':
        cRegion = (~df['ADM_STATE'].isna())&(df['ADM_STATE'] == region)
        
    cSelection = cCommodity&cRange&cRegion&cBaseline
    
    # Get the annual ton miles for all classes
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
    # Bin the data according to the vehicle age, and calculate the associated statistical uncertainty using root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
    fig = plt.figure(figsize = (10, 7))
    n, bins = np.histogram(df[cSelection]['ACQUIREYEAR']-1, bins=np.arange(18)-0.5, weights=annual_ton_miles_all)
    n_err = np.sqrt(np.histogram(df[cSelection]['ACQUIREYEAR']-1, np.arange(18)-0.5, weights=annual_ton_miles_all**2)[0])
    plt.title(f'Commodity: {commodity_title}, Region: {region_pretty}\nRange: {range_title}', fontsize=20)
    plt.ylabel('Commodity flow (ton-miles)', fontsize=20)
    plt.xlabel('Age (years)', fontsize=20)
    
    ticklabels = []
    for i in range(16):
        ticklabels.append(str(i))
    ticklabels.append('>15')
    plt.xticks(np.arange(17), ticklabels)
    
    # Plot the total along with error bars (the bars themselves are invisible since I only want to show the error bars)
    plt.bar(range(17), n, yerr=n_err, width = 0.4, ecolor='black', capsize=5, alpha=0, zorder=1000)
    
    # Add in the distribution for each fuel, stacked on top of one another
    bottom = np.zeros(17)
    for i_class in range(1,5):
        cClass = (df['GREET_CLASS'] == i_class) & cSelection
        annual_ton_miles_fuel = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel='all', greet_class=i_class)
        n, bins = np.histogram(df[cClass]['ACQUIREYEAR']-1, bins=np.arange(18)-0.5, weights=annual_ton_miles_fuel)
        n_err = np.sqrt(np.histogram(df[cClass]['ACQUIREYEAR']-1, bins=np.arange(18)-0.5, weights=annual_ton_miles_fuel**2)[0])
        plt.bar(range(17), n, width = 0.4, alpha=1, zorder=1, label=InfoObjects.GREET_classes[i_class-1], bottom=bottom)
        bottom += n
        
    plt.legend(fontsize=18)
    
    region_save = region_pretty.replace(' ', '_')
    aggregated_info=''
    if aggregated:
        aggregated_info = '_aggregated'
        
    plt.tight_layout()
    print(f'Saving figure to plots/age_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.png')
    plt.savefig(f'plots/age_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.png')
    plt.savefig(f'plots/age_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}.pdf')
    #plt.show()
    plt.close()
    
def plot_payload_hist(df, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title='default', set_commodity_save='default', set_range_title='default', set_range_save='default', aggregated=False, greet_class='all'):
    '''
    Calculates and plots the distributions of truck payload for different commodities ('commmodity' parameter), trip range windows ('truck_range' parameter), and administrative states ('region' parameter). Samples used to produce the distributions are weighted by the average annual ton-miles reported carrying the given 'commodity' over the given 'truck_range', for the given administrative 'region'.
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    commodity (string): Name of the column of VIUS data containing the percentage of ton-miles carrying the given commodity

    truck_range (string): Name of the column of VIUS data containing the percentage of ton-miles carried over the given trip range
    
    region (string): Name of the column of VIUS data containing boolean data to indicate the truck's administrative state
    
    range_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the truck_range is not 'all'
    
    commodity_threshold (float): Threshold percentage of ton-miles carried over the given range required to include the a truck in the analysis, in cases where the commodity is not 'all'
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted commodity to be shown in the plot title
    
    set_commodity_save (string): Allows the user to set the keyword for the plotted commodity to be included in the filenames of the saved plots
    
    set_commodity_title (string): Allows the user to set the human-readable name for the plotted trip range to be shown in the plot title
    
    set_range_save (string): Allows the user to set the keyword for the plotted trip range to be included in the filenames of the saved plots
    
    aggregated (boolean): If set to True, adds an additional string '_aggregated' to the filenames of the saved plots to indicate that aggregation has been done to obtain common commodity and/or trip range definitions between FAF5 and VIUS data
    
    Returns
    -------
    None
        
    NOTE: None.
    '''
    region_pretty = get_region_pretty(region)
    
    if set_commodity_title == 'default':
        commodity_pretty = get_commodity_pretty(commodity)
        commodity_title = commodity_pretty
    else:
        commodity_title = set_commodity_title
    
    if set_commodity_save == 'default':
        commodity_save = commodity
    else:
        commodity_save = set_commodity_save
        
    if set_range_title == 'default':
        range_pretty = get_range_pretty(truck_range)
        range_title = range_pretty
    else:
        range_title = set_range_title
    
    if set_range_save == 'default':
        range_save = truck_range
    else:
        range_save = set_range_save
    
    cNoPassenger = (df['PPASSENGERS'].isna()) | (df['PPASSENGERS'] == 0)
    cBaseline = (~df['WEIGHTAVG'].isna()) & (~df['MILES_ANNL'].isna()) & (~df['WEIGHTEMPTY'].isna()) & (~df['FUEL'].isna()) & (~df['ACQUIREYEAR'].isna()) & cNoPassenger
    cCommodity = True
    cRange = True
    cRegion = True
    if not commodity == 'all':
        cCommodity = (~df[commodity].isna())&(df[commodity] > commodity_threshold)
    if not truck_range == 'all':
        cRange = (~df[truck_range].isna())&(df[truck_range] > range_threshold)
    if not region == 'US':
        cRegion = (~df['ADM_STATE'].isna())&(df['ADM_STATE'] == region)
        
    # Select the given truck class
    cGreetClass = True
    if not greet_class == 'all':
        cGreetClass = (~df['GREET_CLASS'].isna())&(df['GREET_CLASS'] == greet_class)
        
    cSelection = cCommodity&cRange&cRegion&cBaseline&cGreetClass
    if np.sum(cSelection) == 0:
        return
    
    # Get the annual ton miles for all classes
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
    # Bin the data according to the vehicle age, and calculate the associated statistical uncertainty using root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
    payload = (df[cSelection]['WEIGHTAVG'] - df[cSelection]['WEIGHTEMPTY']) * LB_TO_TONS
    fig = plt.figure(figsize = (10, 7))
    n, bins = np.histogram(payload, weights=annual_ton_miles_all, bins=10)
    n_err = np.sqrt(np.histogram(payload, weights=annual_ton_miles_all**2, bins=10)[0])
    
    if greet_class == 'all':
        greet_class_title = 'all'
    else:
        greet_class_title = InfoObjects.GREET_classes[greet_class-1]
    plt.title(f'Commodity: {commodity_title}\nGREET Class: {greet_class_title}', fontsize=20)
    plt.ylabel('Commodity flow (ton-miles)', fontsize=20)
    plt.xlabel('Payload (tons)', fontsize=20)
    
#    ticklabels = []
#    for i in range(16):
#        ticklabels.append(str(i))
#    ticklabels.append('>15')
#    plt.xticks(np.arange(17), ticklabels)
    
    # Plot the total along with error bars (the bars themselves are invisible since I only want to show the error bars)
    plt.bar(bins[:-1]+0.5*(bins[1]-bins[0]), n, yerr=n_err, width = bins[1]-bins[0], ecolor='black', capsize=5)
        
    # Also calculate the mean (+/- stdev) age and report it on the plot
    mean_payload = np.average(payload, weights=annual_ton_miles_all)
    variance_payload = np.average((payload-mean_payload)**2, weights=annual_ton_miles_all)
    std_payload = np.sqrt(variance_payload)
    plt.text(0.5, 0.7, f'mean payload: %.1f±%.1f tons'%(mean_payload, std_payload), transform=fig.axes[0].transAxes, fontsize=18)
#    plt.legend()
    
    region_save = region_pretty.replace(' ', '_')
    aggregated_info=''
    if aggregated:
        aggregated_info = '_aggregated'
        
    if greet_class == 'all':
        greet_class_str = 'all'
    else:
        greet_class_str = (InfoObjects.GREET_classes[greet_class-1]).replace(' ', '_').replace('-', '_')
    
    plt.tight_layout()
    print(f'Saving figure to plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.png')
    plt.savefig(f'plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.png')
    plt.savefig(f'plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.pdf')
    #plt.show()
    plt.close()

######################################### Plot some distributions #########################################

# Read in the VIUS data (from https://rosap.ntl.bts.gov/view/dot/42632) as a dataframe
df_vius = pd.read_csv(f'{top_dir}/data/VIUS_2002/bts_vius_2002_data_items.csv')
df_vius = add_GREET_class(df_vius)

df_agg = make_aggregated_df(df_vius)


df_agg_coarse_range = make_aggregated_df(df_vius, range_map=InfoObjects.FAF5_VIUS_range_map_coarse)

## Basic sanity checks to make sure sum of aggregated column is equal to combined sum of its constituent columns
#df_agg_wood_sum = np.sum(df_agg['Wood products'])
#df_vius_wood_sum = np.sum(df_vius['PPAPER']) + np.sum(df_vius['PNEWSPRINT']) + np.sum(df_vius['PPRINTPROD'])
#print(f'Sum of wood product percentages from df_agg: {df_agg_wood_sum}\nSum of wood product percentages from df_vius: {df_vius_wood_sum}')
#
#df_agg_coarse_below_250 = np.sum(df_agg_coarse_range['Below 250 miles'])
#df_agg_below_250 = np.sum(df_agg['Below 100 miles']) + np.sum(df_agg['100 to 250 miles'])
#df_vius_below_250 = np.sum(df_vius['TRIP0_50']) + np.sum(df_vius['TRIP051_100']) + np.sum(df_vius['TRIP101_200'])
#print(f'Sum of trip range percentages below 250 miles from df_agg_coarse_range: {df_agg_coarse_below_250}\nSum of trip range percentages below 250 miles from df_agg: {df_agg_below_250}\nSum of trip range percentages below 250 miles from df_vius: {df_vius_below_250}')

####################### Informational printouts #######################
## Print out the total number of samples of each commodity, and the total number of commodities
#print_all_commodities(df_vius)
#
## Print out the number of samples for each state in the VIUS, as well as the total number of samples
#print_all_states(df_vius)

## Print out the number of aggregated commodities
#n_aggregated_commodities = len(InfoObjects.FAF5_VIUS_commodity_map)
#print(f'Number of aggregated commodities: {n_aggregated_commodities}')

#######################################################################


################### GREET truck class distributions ###################

#------- Without aggregated commodities/ranges -------#

# Make a distribution of GREET truck class for all regions, commodities, and vehicle range
plot_greet_class_hist(df_vius, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each commodity
#for commodity in InfoObjects.pretty_commodities_dict:
#    plot_greet_class_hist(df_vius, commodity=commodity, truck_range='all', region='US', range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each state
#for state in InfoObjects.states_dict:
#    plot_greet_class_hist(df_vius, commodity='all', truck_range='all', region=state, range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each state and commodity
#for state in InfoObjects.states_dict:
#    for commodity in InfoObjects.pretty_commodities_dict:
#        plot_greet_class_hist(df_vius, region=state, commodity=commodity)

## Make distributions of GREET truck class with respect to both commodity and range
#for truck_range in InfoObjects.pretty_range_dict:
#    for commodity in InfoObjects.pretty_commodities_dict:
#        plot_greet_class_hist(df_vius, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each vehicle range
#for truck_range in InfoObjects.pretty_range_dict:
#    plot_greet_class_hist(df_vius, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0)

#-----------------------------------------------------#
    
#-------- With aggregated commodities/ranges ---------#

## Make distributions of GREET truck class and fuel types for each aggregated commodity
#for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#    plot_greet_class_hist(df_agg, commodity=commodity, truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)

## Make distributions of GREET truck class and fuel types for each state and aggregated commodity
#for state in InfoObjects.states_dict:
#    for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg, commodity=commodity, truck_range='all', region=state, range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)
        
## Make distributions of GREET truck class with respect to both aggregated commodity and range
#for truck_range in InfoObjects.FAF5_VIUS_range_map:
#    for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], set_range_title = truck_range, set_range_save = InfoObjects.FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)

## Make distributions of GREET truck class with respect to both aggregated commodity and coarsely-aggregated range
#for truck_range in InfoObjects.FAF5_VIUS_range_map_coarse:
#    for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg_coarse_range, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], set_range_title = truck_range, set_range_save = InfoObjects.FAF5_VIUS_range_map_coarse[truck_range]['short name'], aggregated=True)
    
## Make distributions of GREET truck class and fuel types for each aggregated vehicle range
#for truck_range in InfoObjects.FAF5_VIUS_range_map:
#    plot_greet_class_hist(df_agg, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = InfoObjects.FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)

#-----------------------------------------------------#

#######################################################################

################### Truck age distributions ###########################

#------- Without aggregated commodities/ranges -------#

## Make distributions of truck age for all regions, commodities, and vehicle range
#plot_age_hist(df_vius, region='US', commodity='all', truck_range='all', range_threshold=0, commodity_threshold=0)
#
## Make distributions of truck age and GREET class for each commodity
#for commodity in InfoObjects.pretty_commodities_dict:
#    plot_age_hist(df_vius, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0)

## Make distributions of truck age and GREET class for each range
#for truck_range in InfoObjects.pretty_range_dict:
#    plot_age_hist(df_vius, region='US', commodity='all', truck_range=truck_range, range_threshold=0, commodity_threshold=0)

#-----------------------------------------------------#

#-------- With aggregated commodities/ranges ---------#
    
## Make distributions of truck age and GREET class for each aggregated commodity
#for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#    plot_age_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)

## Make distributions of truck age and GREET class for each aggregated range
#for truck_range in InfoObjects.FAF5_VIUS_range_map:
#    plot_age_hist(df_agg, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = InfoObjects.FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)
#
## Make distributions of truck age and GREET class for each coarsely aggregated range
#for truck_range in InfoObjects.FAF5_VIUS_range_map_coarse:
#    plot_age_hist(df_agg_coarse_range, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = InfoObjects.FAF5_VIUS_range_map_coarse[truck_range]['short name'], aggregated=True)

#-----------------------------------------------------#

#######################################################################

################## Truck payload distributions ########################

#------- Without aggregated commodities/ranges -------#
## Make payload distributions of truck age for all regions, commodities, and vehicle range
#plot_payload_hist(df_vius, region='US', commodity='all', truck_range='all', range_threshold=0, commodity_threshold=0)

#-----------------------------------------------------#

#------- Without aggregated commodities/ranges -------#
## Make distributions of payload for each aggregated commodity
#for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#    plot_payload_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)

## Make distributions of payload for each aggregated commodity and truck class
#for commodity in InfoObjects.FAF5_VIUS_commodity_map:
#    for greet_class in range(1,5):
#        plot_payload_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = InfoObjects.FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True, greet_class=greet_class)

#-----------------------------------------------------#ls


#######################################################################

###########################################################################################################


