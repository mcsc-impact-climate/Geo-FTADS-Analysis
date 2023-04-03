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
from ViusTools import get_top_dir, make_aggregated_df, add_GREET_class, get_annual_ton_miles, make_basic_selections
from scipy.stats import gaussian_kde
matplotlib.rc('xtick', labelsize=18)
matplotlib.rc('ytick', labelsize=18)

# Conversion from pounds to tons
LB_TO_TONS = 1/2000.

# Get the path to the top level of the git repo
top_dir = get_top_dir()

######################################### Functions defined here ##########################################
    
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
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
    # Bin the data according to the GREET vehicle class, and calculate the associated statistical uncertainty using root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
    fig = plt.figure(figsize = (10, 7))
    n, bins = np.histogram(df[cSelection]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_all)
    n_err = np.sqrt(np.histogram(df[cSelection]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_all**2)[0])
    plt.title(f'Commodity: {commodity_title}, Region: {region_pretty}\nRange: {range_title}', fontsize=20)
    plt.ylabel('Commodity flow (ton-miles)', fontsize=20)
    
    # Plot the total along with error bars (the bars themselves are invisible since I only want to show the error bars)
    plt.bar(InfoObjects.GREET_classes_dict.values(), n, yerr=n_err, width = 0.4, ecolor='black', capsize=5, alpha=0, zorder=1000)
    
    # Add in the distribution for each fuel, stacked on top of one another
    bottom = np.zeros(4)
    for i_fuel in [1,2,3,4]:
        cFuel = (df['FUEL'] == i_fuel) & cSelection
        
        annual_ton_miles_fuel = get_annual_ton_miles(df, cSelection=cSelection, truck_range=truck_range, commodity=commodity, fuel=i_fuel, greet_class='all')
        n, bins = np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel)
        n_err = np.sqrt(np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel**2)[0])
        plt.bar(InfoObjects.GREET_classes_dict.values(), n, width = 0.4, alpha=1, zorder=1, label=InfoObjects.fuels_dict[i_fuel], bottom=bottom)
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
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
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
        annual_ton_miles_fuel = get_annual_ton_miles(df, cSelection=cSelection, truck_range=truck_range, commodity=commodity, fuel='all', greet_class=i_class)
        n, bins = np.histogram(df[cClass]['ACQUIREYEAR']-1, bins=np.arange(18)-0.5, weights=annual_ton_miles_fuel)
        n_err = np.sqrt(np.histogram(df[cClass]['ACQUIREYEAR']-1, bins=np.arange(18)-0.5, weights=annual_ton_miles_fuel**2)[0])
        plt.bar(range(17), n, width = 0.4, alpha=1, zorder=1, label=InfoObjects.GREET_classes_dict[i_class], bottom=bottom)
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
    annual_ton_miles_all = get_annual_ton_miles(df, cSelection=cSelection, truck_range=truck_range, commodity=commodity, fuel='all', greet_class='all')
    
    # Bin the data according to the vehicle age, and calculate the associated statistical uncertainty using root sum of squared weights (see eg. https://www.pp.rhul.ac.uk/~cowan/stat/notes/errors_with_weights.pdf)
    payload = (df[cSelection]['WEIGHTAVG'] - df[cSelection]['WEIGHTEMPTY']) * LB_TO_TONS
    fig = plt.figure(figsize = (10, 7))
    n, bins = np.histogram(payload, weights=annual_ton_miles_all, bins=10)
    n_err = np.sqrt(np.histogram(payload, weights=annual_ton_miles_all**2, bins=10)[0])
    
    if greet_class == 'all':
        greet_class_title = 'all'
    else:
        greet_class_title = InfoObjects.GREET_classes_dict[greet_class]
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
        greet_class_str = (InfoObjects.GREET_classes_dict[greet_class]).replace(' ', '_').replace('-', '_')
    
    plt.tight_layout()
    print(f'Saving figure to plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.png')
    plt.savefig(f'plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.png')
    plt.savefig(f'plots/payload_distribution{aggregated_info}_range_{range_save}_commodity_{commodity_save}_region_{region_save}_greet_class_{greet_class_str}.pdf')
    #plt.show()
    plt.close()
    
def plot_mpg_scatter(df, x_var='gvw', nBins=30):
    '''
    Plots a scatterplot of miles per gallon (mpg) as a function of the given variable, and also plots the running average and standard deviation.
        
    Parameters
    ----------
    df (pd.DataFrame): A pandas dataframe containing the VIUS data
    
    x_car (string): String identifier of the variable to plot on the x-axis

    nBins (integer): Number of bins in the x-variable within which to evaluate the running average and standard deviation
    
    
    Returns
    -------
    None
        
    NOTE: None.
    '''
    fig = plt.figure(figsize = (10, 7))
    plt.ylabel('Miles per Gallon', fontsize=20)
    cSelection = make_basic_selections(df) & (~df['MPG'].isna()) & (~df['WEIGHTAVG'].isna()) & (~df['ACQUIREYEAR'].isna()) #& (df['WEIGHTAVG'] > 20000) & (df['WEIGHTAVG'] < 75000) #& (df['WEIGHTAVG'] > 8500)

    # Calculate the point density
    if x_var == 'gvw':
        x = df['WEIGHTAVG'][cSelection]
        x_nosel = df['WEIGHTAVG']
        plt.title('Vehicle weight dependence of mpg for diesel trucks', fontsize=20)
        plt.xlabel('Average Gross Vehicle Weight (lb)', fontsize=20)
        bin_title = 'lb'
        min_bin = min(x)
        max_gin = max(x)
    elif x_var == 'payload':
        x = (df['WEIGHTAVG'][cSelection] - df['WEIGHTEMPTY'][cSelection]) * LB_TO_TONS
        x_nosel = (df['WEIGHTAVG'] - df['WEIGHTEMPTY']) * LB_TO_TONS
        plt.title('Payload dependence of mpg for diesel trucks', fontsize=20)
        plt.xlabel('Average Payload (tons)', fontsize=20)
        bin_title = 'ton'
        min_bin = min(x)
        max_bin = max(x)
    elif x_var == 'age':
        x = df['ACQUIREYEAR'][cSelection] - 1
        nBins = 16
        x_nosel = df['ACQUIREYEAR'] - 1
        plt.title('Age dependence of mpg for diesel trucks', fontsize=20)
        plt.xlabel('Age Payload (years)', fontsize=20)
        bin_title = 'year'
        min_bin=0
        max_bin=16
        
        ticklabels = []
        for i in range(16):
            ticklabels.append(str(i))
        ticklabels.append('>15')
        plt.xticks(np.arange(17), ticklabels)
        
    mpg = df['MPG'][cSelection]/10.
    #xy = np.vstack([x, mpg])
    #z = gaussian_kde(xy)(xy)

    #plt.scatter(x, y, c=z, s=10)
    plt.plot(x, mpg, 'o', markersize=2)

    # Plot the average and standard deviation
    bins = np.linspace(min_bin, max_bin, nBins+1)
    bin_width = bins[1]-bins[0]
    bin_centers = bins[:-1] + 0.5*bin_width
    mpg_avs = np.zeros(0)
    mpg_stds = np.zeros(0)

    for i_bin in np.arange(nBins):
        mpg_bin = mpg[(x >= bins[i_bin])&(x < bins[i_bin+1])]
        if len(mpg_bin) < 5:
            mpg_avs = np.append(mpg_avs, np.nan)
            mpg_stds = np.append(mpg_stds, np.nan)
            continue
        annual_ton_miles = get_annual_ton_miles(df, cSelection=cSelection&(x_nosel >= bins[i_bin])&(x_nosel < bins[i_bin+1]), truck_range='all', commodity='all', fuel='all', greet_class='all')
        mpg_av = np.average(mpg_bin, weights=annual_ton_miles)
        mpg_variance = np.average((mpg_bin - mpg_av)**2, weights=annual_ton_miles)
        mpg_std = np.sqrt(mpg_variance)
        
        mpg_avs = np.append(mpg_avs, mpg_av)
        mpg_stds = np.append(mpg_stds, mpg_std)

    if x_var == 'age':
        x_plot = range(16)
    else:
        x_plot = bin_centers
        
    plt.plot(x_plot, mpg_avs, color='red', label = f'Average MPG per {int(bin_width)}-{bin_title} bin\n(weighted by average annual ton-miles)', linewidth=2)
    plt.fill_between(x_plot, mpg_avs+mpg_stds, mpg_avs-mpg_stds, color='orange', alpha=0.5, zorder=10, label='Standard deviation of the average')
    plt.legend(fontsize=16)
    
    print(f'Saving figure to plots/mpg_vs_{x_var}.png')
    plt.savefig(f'plots/mpg_vs_{x_var}.png')
    plt.savefig(f'plots/mpg_vs_{x_var}.pdf')

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
#plot_greet_class_hist(df_vius, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0)

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

# Make distributions of GREET truck class with respect to both commodity and range
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

#-----------------------------------------------------#


#######################################################################

###########################################################################################################


######################################### Plot some scatter plots #########################################
# Fuel efficiency (mpg) vs. gross vehicle weight
#plot_mpg_scatter(df_agg, x_var='gvw')

# Fuel efficiency (mpg) vs. payload
#plot_mpg_scatter(df_agg, x_var='payload')

# Fuel efficiency (mpg) vs. payload
#plot_mpg_scatter(df_agg, x_var='age')

###########################################################################################################
