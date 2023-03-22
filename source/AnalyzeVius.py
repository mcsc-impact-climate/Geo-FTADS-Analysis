import numpy as np
import pandas as pd
from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('xtick', labelsize=20)
matplotlib.rc('ytick', labelsize=20)

LB_TO_TONS = 1/2000.

GREET_classes = ['Heavy Heavy-duty', 'Medium Heavy-duty', 'Light Heavy-duty', 'Light-duty']
fuels_dict = {
    1: 'Gasoline',
    2: 'Diesel',
    3: 'Natural gas',
    4: 'Propane',
    5: 'Alcohol fuels',
    6: 'Electricity',
    7: 'Gasoline and natural gas',
    8: 'Gasoline and propane',
    9: 'Gasoline and alcohol fuels',
    10: 'Gasoline and electricity',
    11: 'Diesel and natural gas',
    12: 'Diesel and propane',
    13: 'Diesel and alcohol fuels',
    14: 'Diesel and electricity',
    15: 'Not reported',
    16: 'Not applicable',
}
pretty_commodities_dict = {
    'PALCOHOLIC': 'Alcoholic Beverages',
    'PANIMALFEED': 'Animal Feed',
    'PBAKERYPROD': 'Bakery Products',
    'PBASEMETAL': 'Articles of Base Metal',
    'PCHEMICALS': 'Basic Chemicals',
    'PCOAL': 'Coal',
    'PCRUDEPETRLM': 'Crude Petroleum',
    'PELECTRONIC': 'Electronics',
    'PEMPCONTAIN': 'EShipping Containers',
    'PFERTILIZER': 'Fertilizer',
    'PFUELOIL': 'Fuel oil',
    'PFURNITURE': 'Furniture',
    'PGASOLINE': 'Gasoline',
    'PGRAINS': 'Cereal Grains',
    'PGRAVEL': 'Gravel',
    'PHAZWASTE': 'Hazardous waste',
    'PLIVEANIMAL': 'Live Animal',
    'PLOGS': 'Logs',
    'PMACHINERY': 'Machinery',
    'PMAIL': 'Mail',
    'PMEATS': 'Meats',
    'PMETALPRIM': 'Base Metal in Primary or Semifinished Forms',
    'PMISCPROD': 'Miscellaneous Manufactured Products',
    'PMIXFREIGHT': 'Mixed Freight (For-Hire Carriers Only)',
    'PNEWSPRINT': 'Pulp, Newsprint, Paper, and Paperboard',
    'PNONMETAL': 'Nonmetallic Mineral Products',
    'PORES': 'Metallic Ores and Concentrates',
    'POTHER': 'Products, Equipment, or Materials Not Elsewhere Classified',
    'POTHERAGRIC': 'All Other Agricultural Products',
    'POTHERCHEM': 'All Other Chemical Products and Preparations',
    'POTHERCOAL': 'All Other Coal and Refined Petroleum Products',
    'POTHERFOOD': 'All Other Prepared Foodstuffs',
    'POTHERMIN': 'All Other Nonmetallic Minerals',
    'POTHERTRANS': 'All Other Transportation Equipment',
    'POTHERWASTE': 'All Other Waste and Scrap',
    'PPAPER': 'Paper or Paperboard Articles',
    'PPHARMACEUT': 'Pharmaceutical Products',
    'PPLASTICS': 'Plastics and Rubber',
    'PPRECISION': 'Precision Instruments and Apparatus',
    'PPRINTPROD': 'Printed Products',
    'PRECYCLABLE': 'Recyclable Products',
}

FAF5_VIUS_commodity_map = {
    'Live animals/fish': {
        'VIUS': ['PLIVEANIMAL'],
        'FAF5': ['Live animals/fish'],
        'short name': 'live_animals_fish'
    },
    'Cereal grains': {
        'VIUS': ['PGRAINS'],
        'FAF5': ['Cereal grains'],
        'short name': 'cereal_grains'
    },
    'Other agricultural products': {
        'VIUS': ['POTHERAGRIC'],
        'FAF5': ['Other ag prods.', 'Tobacco prods.'],
        'short name': 'other_ag_prods'
    },
    'Animal feed': {
        'VIUS': ['PANIMALFEED'],
        'FAF5': ['Animal feed'],
        'short name': 'animal_feed'
    },
    'Meat/seafood': {
        'VIUS': ['PMEATS'],
        'FAF5': ['Meat/seafood'],
        'short name': 'meat_seafood'
    },
    'Milled grain prods.': {
        'VIUS': ['PBAKERYPROD'],
        'FAF5': ['Milled grain prods.'],
        'short name': 'milled_grain_prods'
    },
    'Other foodstuffs': {
        'VIUS': ['POTHERFOOD'],
        'FAF5': ['Other foodstuffs'],
        'short name': 'other_food'
    },
    'Alcoholic beverages': {
        'VIUS': ['PALCOHOLIC'],
        'FAF5': ['Alcoholic beverages'],
        'short name': 'alcohol'
    },
    'Nonmetallic mineral products': {
        'VIUS': ['PNONMETAL'],
        'FAF5': ['Building stone', 'Natural sands', 'Gravel', 'Nonmetallic minerals'],
        'short name': 'nonmetal_min_prods'
    },
    'Metallic ores': {
        'VIUS': ['PORES'],
        'FAF5': ['Metallic ores'],
        'short name': 'metal_ores'
    },
    'Coal': {
        'VIUS': ['PCOAL'],
        'FAF5': ['Coal'],
        'short name': 'coal'
    },
    'Crude petroleum': {
        'VIUS': ['PCRUDEPETRLM'],
        'FAF5': ['Crude petroleum'],
        'short name': 'crude_petroleum'
    },
    'Gasoline': {
        'VIUS': ['PGASOLINE'],
        'FAF5': ['Gasoline'],
        'short name': 'gasoline'
    },
    'Fuel oils': {
        'VIUS': ['PFUELOIL'],
        'FAF5': ['Fuel oils'],
        'short name': 'fuel_oils'
    },
    'All other coal and refined petroleum products': {
        'VIUS': ['POTHERCOAL'],
        'FAF5': ['Coal-n.e.c.'],
        'short name': 'other_coal_petrol'
    },
    'Basic chemicals': {
        'VIUS': ['PCHEMICALS'],
        'FAF5': ['Basic chemicals'],
        'short name': 'basic_chems'
    },
    'Pharmaceuticals': {
        'VIUS': ['PPHARMACEUT'],
        'FAF5': ['Pharmaceuticals'],
        'short name': 'pharmaceut'
    },
    'Fertilizers': {
        'VIUS': ['PFERTILIZER'],
        'FAF5': ['Fertilizers'],
        'short name': 'fertilizer'
    },
    'Chemical prodsucts': {
        'VIUS': ['POTHERCHEM'],
        'FAF5': ['Chemical prods.'],
        'short name': 'chem_prods'
    },
    'Plastics/rubber': {
        'VIUS': ['PPLASTICS'],
        'FAF5': ['Plastics/rubber'],
        'short name': 'plastics_rubber'
    },
    'Logs': {
        'VIUS': ['PLOGS'],
        'FAF5': ['Logs'],
        'short name': 'logs'
    },
    'Wood products': {
        'VIUS': ['PNEWSPRINT', 'PPAPER', 'PPRINTPROD'],
        'FAF5': ['Newsprint/paper', 'Wood prods.', 'Paper articles', 'Printed prods.'],
        'short name': 'wood_prods'
    },
    'Miscellaneous manufactured products': {
        'VIUS': ['PMISCPROD'],
        'FAF5': ['Textiles/leather', 'Misc. mfg. prods.', 'motorized vehicles'],
        'short name': 'misc_manuf_prods'
    },
    'Nonmetallic mineral products': {
        'VIUS': ['PNONMETAL'],
        'FAF5': ['Nonmetal min. prods.'],
        'short name': 'nonmetal_min_prods'
    },
    'Base metal in primary or semifinished forms': {
        'VIUS': ['PMETALPRIM'],
        'FAF5': ['Base metals'],
        'short name': 'base_metals'
    },
    'Articles of Base Metal': {
        'VIUS': ['PBASEMETAL'],
        'FAF5': ['Articles-base metal'],
        'short name': 'base_metal'
    },
    'Machinery': {
        'VIUS': ['PMACHINERY'],
        'FAF5': ['Machinery'],
        'short name': 'machinery'
    },
    'Electronics': {
        'VIUS': ['PELECTRONIC'],
        'FAF5': ['Electronics'],
        'short name': 'electronics'
    },
    'Transportation equipment': {
        'VIUS': ['POTHERTRANS'],
        'FAF5': ['Transport equip.'],
        'short name': 'transport_equip'
    },
    'Precision instruments': {
        'VIUS': ['PPRECISION'],
        'FAF5': ['Precision instruments'],
        'short name': 'precision_inst'
    },
    'Furniture': {
        'VIUS': ['PFURNITURE'],
        'FAF5': ['Furniture'],
        'short name': 'furniture'
    },
    'Waste/scrap': {
        'VIUS': ['POTHERWASTE', 'PHAZWASTE'],
        'FAF5': ['Waste/scrap'],
        'short name': 'waste_scrap'
    },
    'Mixed freight': {
        'VIUS': ['PMIXFREIGHT'],
        'FAF5': ['Mixed freight'],
        'short name': 'mixed_freight'
    },
}

FAF5_VIUS_range_map = {
    'Below 100 miles': {
        'VIUS': ['TRIP0_50', 'TRIP051_100'],
        'FAF5': ['Below 100'],
        'short name': 'below_100'
    },
    '100 to 250 miles': {
        'VIUS': ['TRIP101_200'],
        'FAF5': ['100 - 249'],
        'short name': '100_250'
    },
    '250 to 500 miles': {
        'VIUS': ['TRIP201_500'],
        'FAF5': ['250 - 499'],
        'short name': '250_500'
    },
    'Over 500 miles': {
        'VIUS': ['TRIP500MORE'],
        'FAF5': ['500 - 749', '750 - 999', '1,000 - 1,499', '1,500 - 2,000', 'Over 2,000'],
        'short name': 'over_500'
    },
}

FAF5_VIUS_range_map_coarse = {
    'Below 250 miles': {
        'VIUS': ['TRIP0_50', 'TRIP051_100', 'TRIP101_200'],
        'FAF5': ['Below 100', '100 - 249'],
        'short name': 'below_250'
    },
    '250 to 500 miles': {
        'VIUS': ['TRIP201_500', 'TRIP500MORE'],
        'FAF5': ['250 - 499', '500 - 749', '750 - 999', '1,000 - 1,499', '1,500 - 2,000', 'Over 2,000'],
        'short name': 'over_250'
    },
}


pretty_range_dict = {
    'TRIP0_50': 'Range <= 50 miles',
    'TRIP051_100': '51 miles <= Range <= 100 miles',
    'TRIP101_200': '101 miles <= Range <= 200 miles',
    'TRIP201_500': '201 miles <= Range <= 500 miles',
    'TRIP500MORE': 'Range >= 501 miles'
}

states_dict = {
    1: 'Alabama',
    2: 'Alaska',
    4: 'Arizona',
    5: 'Arkansas',
    6: 'California',
    8: 'Colorado',
    9: 'Connecticut',
    10: 'Delaware',
    11: 'District of Columbia',
    12: 'Florida',
    13: 'Georgia',
    15: 'Hawaii',
    16: 'Idaho',
    17: 'Illinois',
    18: 'Indiana',
    19: 'Iowa',
    20: 'Kansas',
    21: 'Kentucky',
    22: 'Louisiana',
    23: 'Maine',
    24: 'Maryland',
    25: 'Massachusetts',
    26: 'Michigan',
    27: 'Minnesota',
    28: 'Mississippi',
    29: 'Missouri',
    30: 'Montana',
    31: 'Nebraska',
    32: 'Nevada',
    33: 'New Hampshire',
    34: 'New Jersey',
    35: 'New Mexico',
    36: 'New York',
    37: 'North Carolina',
    38: 'North Dakota',
    39: 'Ohio',
    40: 'Oklahoma',
    41: 'Oregon',
    42: 'Pennsylvania',
    44: 'Rhode Island',
    45: 'South Carolina',
    46: 'South Dakota',
    47: 'Tennessee',
    48: 'Texas',
    49: 'Utah',
    50: 'Vermont',
    51: 'Virginia',
    53: 'Washington',
    54: 'West Virginia',
    55: 'Wisconsin',
    56: 'Wyoming'
}

# Get the path to the top level of the git repo
source_path = Path(__file__).resolve()
source_dir = source_path.parent
top_dir = os.path.dirname(source_dir)

######################################### Functions defined here ##########################################

# Make a new dataframe with commodity columns aggregated according to the rules defined in the FAF5_VIUS_commodity_map
def make_aggregated_df(df, range_map=FAF5_VIUS_range_map):
    
    # Make a deep copy of the VIUS dataframe
    df_agg = df.copy(deep=True)
    
    # Loop through all commodities in the VIUS dataframe and combine them as needed to produce the aggregated mapping defined in the FAF5_VIUS_commodity_map
    for commodity in FAF5_VIUS_commodity_map:
        vius_commodities = FAF5_VIUS_commodity_map[commodity]['VIUS']
        if len(vius_commodities) == 1:
            df_agg[commodity] = df[vius_commodities[0]]
        elif len(vius_commodities) > 1:
            i_comm = 0
            for vius_commodity in vius_commodities:
                if i_comm == 0:
                    df_agg_column = df[vius_commodity]
                else:
                    df_agg_column += df[vius_commodity]
                i_comm += 1
            df_agg[commodity] = df_agg_column
            
    # Loop through all the ranges in the VIUS dataframe and combine them as needed to produce the aggregated mapping defined in the FAF5_VIUS_range_map
    for truck_range in range_map:
        vius_ranges = range_map[truck_range]['VIUS']
        if len(vius_ranges) == 1:
            df_agg[truck_range] = df[vius_ranges[0]]
        elif len(vius_ranges) > 1:
            i_range = 0
            for vius_range in vius_ranges:
                if i_range == 0:
                    df_agg_column = df[vius_range]
                else:
                    df_agg_column += df[vius_range]
                i_range += 1
            df_agg[truck_range] = df_agg_column
                    
#    # Remove the columns with the original commodity names to save space
#    for column in df:
#        if column.startswith('P') and not column.startswith('P_'):
#            df_agg = df_agg.drop(columns=column)
    return df_agg

# Add a column to the dataframe that specifies the GREET truck class
def add_GREET_class(df):
    df['GREET_CLASS'] = df.copy(deep=False)['WEIGHTAVG']
    
    df.loc[df['WEIGHTAVG'] >= 33000, 'GREET_CLASS'] = 1
    df.loc[(df['WEIGHTAVG'] >= 19500)&(df['WEIGHTAVG'] < 33000), 'GREET_CLASS'] = 2
    df.loc[(df['WEIGHTAVG'] >= 8500)&(df['WEIGHTAVG'] < 19500), 'GREET_CLASS'] = 3
    df.loc[df['WEIGHTAVG'] < 8500, 'GREET_CLASS'] = 4
    return df
    
def get_annual_ton_miles(df, cSelection, cRange, cCommodity, truck_range, commodity, fuel='all', greet_class='all'):
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
    if commodity == 'all':
        commodity_pretty = 'All commodities'
    else:
        commodity_pretty = pretty_commodities_dict[commodity]
    return commodity_pretty
    
def get_region_pretty(region='US'):
    if region == 'US':
        region_pretty = 'US'
    else:
        region_pretty = states_dict[region]
    return region_pretty
    
def get_range_pretty(truck_range='all'):
    if truck_range == 'all':
        range_pretty = 'All Ranges'
    else:
        range_pretty = pretty_range_dict[truck_range]
    return range_pretty

# Print out the number of samples of each commodity in the VIUS, as well as the total number of commodities
def print_all_commodities(df):
    n_comm=0
    for column in df:
        if column.startswith('P') and not column.startswith('P_'):
            n_column = len(df[~df[column].isna()][column])
            print(f'Total number of samples for commodity {column}: {n_column}')
            n_comm += 1
    print(f'Total number of commodities: {n_comm}\n\n')
    
# Print out the number of samples for each state in the VIUS, as well as the total number of samples
def print_all_states(df):
    n_samples=0
    for state in range(1,57):
        if not state in states_dict: continue
        n_state = len(df[(~df['ADM_STATE'].isna())&(df['ADM_STATE']==state)]['ADM_STATE'])
        state_str = states_dict[state]
        print(f'Total number of samples in {state_str}: {n_state}')
        n_samples += n_state
    print(f'total number of samples: {n_samples}\n\n')
    
# Calculate and plot the distribution of vehicle types for each range,
# weighted by the average annual ton-miles driven for the given range
def plot_greet_class_hist(df, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title='default', set_commodity_save='default', set_range_title='default', set_range_save='default', aggregated=False):

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
    plt.bar(GREET_classes, n, yerr=n_err, width = 0.4, ecolor='black', capsize=5, alpha=0, zorder=1000)
    
    # Add in the distribution for each fuel, stacked on top of one another
    bottom = np.zeros(4)
    for i_fuel in [1,2,3,4]:
        cFuel = (df['FUEL'] == i_fuel) & cSelection
        
        annual_ton_miles_fuel = get_annual_ton_miles(df, cSelection=cSelection, cRange=cRange, cCommodity=cCommodity, truck_range=truck_range, commodity=commodity, fuel=i_fuel, greet_class='all')
        n, bins = np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel)
        n_err = np.sqrt(np.histogram(df[cFuel]['GREET_CLASS'], bins=[0.5,1.5,2.5,3.5,4.5], weights=annual_ton_miles_fuel**2)[0])
        plt.bar(GREET_classes, n, width = 0.4, alpha=1, zorder=1, label=fuels_dict[i_fuel], bottom=bottom)
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
        plt.bar(range(17), n, width = 0.4, alpha=1, zorder=1, label=GREET_classes[i_class-1], bottom=bottom)
        bottom += n
        
    # Also calculate the mean (+/-stdev) age and report it on the plot
#    mean_age = np.mean(df[cSelection]['ACQUIREYEAR']-1)
#    std_age = np.std(df[cSelection]['ACQUIREYEAR']-1)
#    plt.text(0.6, 0.7, f'mean age: %.1f±%.1f years'%(mean_age, std_age), transform=fig.axes[0].transAxes, fontsize=13)
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
        greet_class_title = GREET_classes[greet_class-1]
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
        greet_class_str = (GREET_classes[greet_class-1]).replace(' ', '_').replace('-', '_')
    
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
df_agg_coarse_range = make_aggregated_df(df_vius, range_map=FAF5_VIUS_range_map_coarse)

####################### Informational printouts #######################
## Print out the total number of samples of each commodity, and the total number of commodities
#print_all_commodities(df_vius)
#
## Print out the number of samples for each state in the VIUS, as well as the total number of samples
#print_all_states(df_vius)

## Print out the number of aggregated commodities
#n_aggregated_commodities = len(FAF5_VIUS_commodity_map)
#print(f'Number of aggregated commodities: {n_aggregated_commodities}')

#######################################################################


################### GREET truck class distributions ###################
## Make a distribution of GREET truck class for all regions, commodities, and vehicle range
#plot_greet_class_hist(df_vius, commodity='all', truck_range='all', region='US', range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each commodity
#for commodity in pretty_commodities_dict:
#    plot_greet_class_hist(df_vius, commodity=commodity, truck_range='all', region='US', range_threshold=0, commodity_threshold=0)
    
## Make distributions of GREET truck class and fuel types for each aggregated commodity
#for commodity in FAF5_VIUS_commodity_map:
#    plot_greet_class_hist(df_agg, commodity=commodity, truck_range='all', region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)

## Make distributions of GREET truck class and fuel types for each state
#for state in states_dict:
#    plot_greet_class_hist(df_vius, commodity='all', truck_range='all', region=state, range_threshold=0, commodity_threshold=0)

## Make distributions of GREET truck class and fuel types for each state and commodity
#for state in states_dict:
#    for commodity in pretty_commodities_dict:
#        plot_greet_class_hist(df_vius, region=state, commodity=commodity)

## Make distributions of GREET truck class and fuel types for each state and aggregated commodity
#for state in states_dict:
#    for commodity in FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg, commodity=commodity, truck_range='all', region=state, range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)


## Make distributions of GREET truck class with respect to both commodity and range
#for truck_range in pretty_range_dict:
#    for commodity in pretty_commodities_dict:
#        plot_greet_class_hist(df_vius, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0)
        
## Make distributions of GREET truck class with respect to both aggregated commodity and range
#for truck_range in FAF5_VIUS_range_map:
#    for commodity in FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], set_range_title = truck_range, set_range_save = FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)
#
## Make distributions of GREET truck class with respect to both aggregated commodity and coarsely-aggregated range
#for truck_range in FAF5_VIUS_range_map_coarse:
#    for commodity in FAF5_VIUS_commodity_map:
#        plot_greet_class_hist(df_agg_coarse_range, commodity=commodity, truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], set_range_title = truck_range, set_range_save = FAF5_VIUS_range_map_coarse[truck_range]['short name'], aggregated=True)

## Make distributions of GREET truck class and fuel types for each vehicle range
#for truck_range in pretty_range_dict:
#    plot_greet_class_hist(df_vius, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0)
    
## Make distributions of GREET truck class and fuel types for each aggregated vehicle range
#for truck_range in FAF5_VIUS_range_map:
#    plot_greet_class_hist(df_agg, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)
#######################################################################

################### Truck age distributions ###########################
## Make distributions of truck age for all regions, commodities, and vehicle range
#plot_age_hist(df_vius, region='US', commodity='all', truck_range='all', range_threshold=0, commodity_threshold=0)
#
## Make distributions of truck age and GREET class for each commodity
#for commodity in pretty_commodities_dict:
#    plot_age_hist(df_vius, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0)
    
## Make distributions of truck age and GREET class for each aggregated commodity
#for commodity in FAF5_VIUS_commodity_map:
#    plot_age_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)
#
## Make distributions of truck age and GREET class for each range
#for truck_range in pretty_range_dict:
#    plot_age_hist(df_vius, region='US', commodity='all', truck_range=truck_range, range_threshold=0, commodity_threshold=0)

## Make distributions of truck age and GREET class for each aggregated range
#for truck_range in FAF5_VIUS_range_map:
#    plot_age_hist(df_agg, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = FAF5_VIUS_range_map[truck_range]['short name'], aggregated=True)
#
## Make distributions of truck age and GREET class for each coarsely aggregated range
#for truck_range in FAF5_VIUS_range_map_coarse:
#    plot_age_hist(df_agg_coarse_range, commodity='all', truck_range=truck_range, region='US', range_threshold=0, commodity_threshold=0, set_range_title = truck_range, set_range_save = FAF5_VIUS_range_map_coarse[truck_range]['short name'], aggregated=True)
#######################################################################

################## Truck payload distributions ########################
## Make payload distributions of truck age for all regions, commodities, and vehicle range
#plot_payload_hist(df_vius, region='US', commodity='all', truck_range='all', range_threshold=0, commodity_threshold=0)

## Make distributions of payload for each aggregated commodity
#for commodity in FAF5_VIUS_commodity_map:
#    plot_payload_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True)
#
# Make distributions of payload for each aggregated commodity and truck class
for commodity in FAF5_VIUS_commodity_map:
    for greet_class in range(1,5):
        plot_payload_hist(df_agg, region='US', commodity=commodity, truck_range='all', range_threshold=0, commodity_threshold=0, set_commodity_title = commodity, set_commodity_save = FAF5_VIUS_commodity_map[commodity]['short name'], aggregated=True, greet_class=greet_class)

#######################################################################

###########################################################################################################


