#!/usr/bin/env python3
"""
Created on Thu Mar 9 15:41:00 2023

@author: danikam
"""
import csv
import os
import pandas as pd
from pathlib import Path
import InfoObjects

TONNES_TO_TONS = 1.10231    # tonnes per ton
KM_TO_MILES = 0.621371      # km per mile
PAYLOAD = 19.0402178166526  # Assumed payload for heavy duty truck, in tons (obtained from GREET default for combination long-haul truck)

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
    
    
# Get the path to the top level of the git repo
top_dir = get_top_dir()
    
def readGreetWtwTruck(csv_path, commodity='all'):
    '''
    Reads in a csv file containing GREET outputs for the trucking well-to-wheels (WTW) module, and reformats to match the rail module
    
    Parameters
    ----------
    csv_path (string): Path to csv file containing GREET outputs
    
    commodity (string): Indicates which commodity is being carried (currently just a placeholder, functionality not yet implemented to modify calculated emission rate based on commodity)

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu/ton-mile], fuel use [Gallons/ton-mile], or emissions p[g/ton-mile] for the trucking module
            
    NOTE: None
    
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
    
def get_aggregated_commodity(faf5_commodity):
    '''
    Gets the aggregated commodity associated with the given FAF5 commodity from the mapping specified in the FAF5_VIUS_commodity_map
    
    Parameters
    ----------
    faf5_commodity (string): Name of the FAF5 commodity whose associated aggregated commodity name we want to determine

    Returns
    -------
    aggregated_commodity (string): Name of the aggregated commodity associated with the input FAF5 commodity
            
    NOTE: If the FAF5 commodity isn't found in the FAF5_VIUS_commodity_map, the funtion prints our an error message and return None
    
    '''
    for aggregated_commodity in InfoObjects.FAF5_VIUS_commodity_map:
        if faf5_commodity in InfoObjects.FAF5_VIUS_commodity_map[aggregated_commodity]['FAF5']:
            return aggregated_commodity
    print(f'Could not find FAF5 commodity {faf5_commodity} in FAF5_VIUS_commodity_map')
    return None
    
def calculate_df_lca_weighted_average(df_lcas, weights, normalize_by_payload=False, payloads=None):
    '''
    Calculates the weighted average over a list of dataframes, for each column containing lifecycle stage emission intensities ('WTP', 'PTW' or 'WTW'), using a list of weights associated with each dataframe.
    
    Parameters
    ----------
    df_lcas (list of pd.DataFrames): List of pandas dataframes. Each list element corresponds to a different GREET truck class. Each dataframe contains lifecycle emissions at different stages (one column per stage) of various pollutants (one row per pollutant)
    
    weights (list of floats): List containing the weight associated with each GREET truck class
    
    normalize_by_payload (boolean): Flag to indicate whether to divide the emission intensities (in g / mile) by the average payload for each GREET class to obtain intensities in g / ton-mile
    
    payloads (listof floats): List containing the payload associated with each GREET truck class

    Returns
    -------
    df_lca_weighted_average (pd.DataFrame): Dataframe in the same format as those in the provided df_lcas list, but emission intensities in each column are weighted averages of the associated columns in each dataframe within df_lcas
            
    NOTE: None
    
    '''
    df_lca_weighted_average = df_lcas[0].copy(deep=True)
    
    sum_of_weights = {}
    for column in ['WTP', 'PTW', 'WTW']:
        df_lca_weighted_average[column].values[:] = 0.
    
    for column in ['WTP', 'PTW', 'WTW']:
        for i_class in range(len(df_lcas)):
            if normalize_by_payload:
                df_lca_weighted_average[column] += df_lcas[i_class][column] * weights[i_class] / payloads[i_class]
            else:
                df_lca_weighted_average[column] += df_lcas[i_class][column] * weights[i_class]
    
    return df_lca_weighted_average
    
def evaluateGreetWtwTruck(faf5_commodity='all'):
    '''
    Evaluates emission intensities for each commodity, using a weighted sum over emission intensities for each GREET truck class. The weights are given by the relative amount of ton-miles carried by each GREET truck class for the given commodity, based on the VIUS data. Emission intensities can also be normalized by the average payload evaluated for each commodity and GREET class.
    
    Parameters
    ----------
    faf5_commodity (string): FAF5 commodity for which to evaluate the overall emission intensities

    Returns
    -------
    df_lca_weighted_average: Dataframe containing the evaluated emission intensity for each pollutant (rows) and lifecycle stage (columns) for the given commodity
            
    NOTE: None
    
    '''
    
    # Get the name of the aggregated commodity associated with the given FAF5 commodity
    if faf5_commodity == 'all':
        aggregated_commodity = 'all commodities'
    else:
        aggregated_commodity = get_aggregated_commodity(faf5_commodity)
            
    # Read in distribution of vehicle classes for the given FAF5 commodity
    df_norm_distribution = pd.read_csv(f'{top_dir}/data/VIUS_Results/norm_distribution_per_class.csv')
    
    # Read in payload per vehicle class for the given commodity
    df_payload = pd.read_csv(f'{top_dir}/data/VIUS_Results/payload_per_class.csv')
    
    # Evaluate overall emission intensities (g / mile)
    df_lcas_dict = {'GREET class': ['Heavy GVW', 'Medium GVW', 'Light GVW'], 'df': [], 'weight': [], 'payload': []}
    for greet_class in df_lcas_dict['GREET class']:
        greet_class_info = greet_class.lower().replace(' ', '_')
        df_lca = readGreetWtwTruck(f'{top_dir}/data/GREET_LCA/truck_{greet_class_info}_diesel_wtw.csv')
        
        df_lcas_dict['df'].append(df_lca)
        df_lcas_dict['weight'].append(float(df_norm_distribution[aggregated_commodity][df_norm_distribution['class'] == greet_class]))
        df_lcas_dict['payload'].append(float(df_payload[aggregated_commodity][df_payload['class'] == greet_class]))
    
    # Evaluate the weighted average of LCAs with respect to the GREET class
    df_lca_weighted_average = calculate_df_lca_weighted_average(df_lcas_dict['df'], df_lcas_dict['weight'])
    
    # Evaluate overall payload-normalized emission intensities (g / ton-mile)
    df_lca_weighted_average_payload_normalized = calculate_df_lca_weighted_average(df_lcas_dict['df'], df_lcas_dict['weight'], normalize_by_payload=True, payload=df_lcas_dict['payload'])
    
    return df_lca_weighted_average, df_lca_weighted_average_payload_normalized
    
    
def plot_truck_emissions_per_class():
    '''
    Calculates and plots the CO2 emissions evaluated by GREET in each lifecycle stage (well-to-pump, pump-to-wheel and well-to-wheel) for each class of heavy-duty truck
    
    Parameters
    ----------
    None

    Returns
    -------
    None
            
    NOTE: None
    
    '''
    co2_emission_intensity = {'class': [], 'WTP': [], 'PTW': [], 'WTW': []}
    for greet_class in ['Heavy GVW', 'Medium GVW', 'Light GVW']:
        greet_class_info = greet_class.lower().replace(' ', '_')
        df_lca = readGreetWtwTruck(f'{top_dir}/data/GREET_LCA/truck_{greet_class_info}_diesel_wtw.csv')
        co2_emission_intensity['class'].append(greet_class)
        co2_emission_intensity['WTP'].append(float(df_lca['WTP'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
        co2_emission_intensity['PTW'].append(float(df_lca['PTW'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
        co2_emission_intensity['WTW'].append(float(df_lca['WTP'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
        
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    fig = plt.figure(figsize = (10, 7))
    plt.title('CO$_2$ emission intensity of each GREET truck class', fontsize=18)
    plt.ylabel('CO$_2$ emission intensity (g/mile)', fontsize=18)
    plt.bar(['Heavy GVW', 'Medium GVW', 'Light GVW'], co2_emission_intensity['WTP'], width = 0.4, label='Well to Pump')
    plt.bar(['Heavy GVW', 'Medium GVW', 'Light GVW'], co2_emission_intensity['PTW'], width = 0.4, label='Pump to Wheel', bottom=co2_emission_intensity['WTP'])
    plt.xticks(rotation=15, ha='right')
    plt.legend(fontsize=18)
    plt.tight_layout()
    
    print('Saving figure to plots/co2_emissions_per_class.png')
    plt.savefig('plots/co2_emissions_per_class.png')
    plt.savefig('plots/co2_emissions_per_class.pdf')
    
def plot_truck_emissions_per_commodity(normalize_by_payload = False):
    '''
    Calculates and plots the calculated CO2 emissions for each commodity
    
    Parameters
    ----------
    normalize_by_payload (boolean): Flag to indicate whether to plot emission rates normalized by payload ( to obtain g / ton-mile rather than g / mile)

    Returns
    -------
    None
            
    NOTE: None
    
    '''
    co2_emission_intensity = {'commodity': [], 'WTP': [], 'PTW': [], 'WTW': []}
    
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rc('xtick', labelsize=18)
    matplotlib.rc('ytick', labelsize=18)
    fig = plt.figure(figsize = (16, 13))
    plt.title('CO$_2$ emission intensity of each commodity', fontsize=18)
    
    if normalize_by_payload:
        plt.xlabel('CO$_2$ emission intensity (g/ton-mile)', fontsize=18)
    else:
        plt.xlabel('CO$_2$ emission intensity (g/mile)', fontsize=18)
    
    metaPath = f'{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx'
    meta = pd.ExcelFile(metaPath)
    commodities = list(pd.read_excel(meta, 'Commodity (SCTG2)')['Description'])
    commodities.append('all')
    
    co2_emission_intensity = {'commodity': [], 'WTP': [], 'PTW': [], 'WTW': []}
    
    for commodity in commodities:
        df_lca, df_lca_payload_normalized = evaluateGreetWtwTruck(commodity)
        co2_emission_intensity['commodity'].append(commodity)
        
        if normalize_by_payload:
            co2_emission_intensity['WTP'].append(float(df_lca_payload_normalized['WTP'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
            co2_emission_intensity['PTW'].append(float(df_lca_payload_normalized['PTW'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
            co2_emission_intensity['WTW'].append(float(df_lca_payload_normalized['WTW'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
        else:
            co2_emission_intensity['WTP'].append(float(df_lca['WTP'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
            co2_emission_intensity['PTW'].append(float(df_lca['PTW'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
            co2_emission_intensity['WTW'].append(float(df_lca['WTW'][df_lca['Item'] == 'CO2 (w/ C in VOC & CO)']))
        
    plt.barh(co2_emission_intensity['commodity'], co2_emission_intensity['WTP'], label='Well to Pump')
    plt.barh(co2_emission_intensity['commodity'], co2_emission_intensity['PTW'], label='Pump to Wheel', left=co2_emission_intensity['WTP'])
    xlim = plt.xlim()
    plt.xlim(0, xlim[1]*1.3)
    
    plt.legend(fontsize=18)
    plt.tight_layout()
    
    normalize_by_payload_str = ''
    if normalize_by_payload:
        normalize_by_payload_str = '_norm_by_payload'
    
    print(f'Saving figure to plots/co2_emissions_per_commodity{normalize_by_payload_str}.png')
    plt.savefig(f'plots/co2_emissions_per_commodity{normalize_by_payload_str}.png')
    plt.savefig(f'plots/co2_emissions_per_commodity{normalize_by_payload_str}.pdf')
    
def readGreetWtwRail(csv_path, commodity='all'):
    '''
    Read in a csv file containing GREET outputs for the rail well-to-wheels (WTW) module
    
    Parameters
    ----------
    csv_path (string): Path to csv containing GREET outputs
    
    commodity (string): Indicates which commodity is being carried (currently just a placeholder, functionality not yet implemented to modify calculated emission rate based on commodity)

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu], fuel use [Gallons], or emissions p[g/ton-mile] for the rail module
    
    NOTE: None
    
    '''
    
    # Read in the csv as a pandas dataframe
    df_lca = pd.read_csv(csv_path)
    #print(df_lca.columns)
    return df_lca
    
def readGreetWthShip(csv_path_feedstock, csv_path_conversion, csv_path_combustion, commodity='all'):
    '''
    Read in csv files containing GREET outputs for the ship well-to-hull (WTH) module
    
    Parameters
    ----------
    csv_path_feedstock (string): Path to csv file containing GREET outputs for marine fuel feedstock (emissions in g/million tonne-km)
    
    csv_path_conversion (string): Path to csv file containing GREET outputs for marine fuel conversion
    
    csv_path_combustion (string): Path to csv file containing GREET outputs for marine fuel combustion
    
    commodity (string): Indicates which commodity is being carried (currently just a placeholder, functionality not yet implemented to modify calculated emission rate based on commodity)

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing energy use [Btu], fuel use [Gallons], or emissions p[g/ton-mile] for the ship module
            
    NOTE: None
    
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
    
def readSesameWtwTruck(commodity='all'):
    '''
    Read in heavy duty vehicle fleet data for class 8 trucks from sesame-core submodule, with input parameters specified, and collect the CO2e emission rates
    
    Parameters
    ----------
    commodity (string): Indicates which commodity is being carried (currently just a placeholder, functionality not yet implemented to modify calculated emission rate based on commodity)

    Returns
    -------
    df_lca (pandas dataframe): dataframe containing CO2e for the sesame HDV module
            
    NOTE: None
    
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
    df_lca = pd.concat([pd.DataFrame({'Item': ['CO2e']}), pd.DataFrame({'WTP': [WTP]}), pd.DataFrame({'PTW': [PTW]}), pd.DataFrame({'WTW': [WTW]})], axis=1)
    
    # cd back out of the sesame-core module now that we're finished with it
    os.chdir(os.getcwd() + '/..')
        
    return df_lca
    
def fillLcaDf(df_dict, top_dir, commodity='all'):
    '''
    Fills the input dictionary with dataframes containing the calculated emission rates from GREET and SESAME for the given commodity
    
    Parameters
    ----------
    df_dict (dictionary): Dictionary to contain dataframes of emission rates for each mode and commodity
    
    commodity (string): Commodity for which to calculate emission rates and fill the dictionary
    
    top_dir (string): Path to the top level of the git repo

    Returns
    -------
    None
        
    NOTE: None.
    '''
    
    # Emission rates (g / ton-mile) from GREET outputs
    df_lca_truck, df_lca_truck_payload_normalized = evaluateGreetWtwTruck(faf5_commodity=commodity)
    df_dict['truck'][commodity] = df_lca_truck_payload_normalized
    df_dict['rail'][commodity] = readGreetWtwRail(f'{top_dir}/data/GREET_LCA/rail_freight_diesel_wtw.csv', commodity=commodity)
    df_dict['ship'][commodity] = readGreetWthShip(f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_feedstock.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_conversion.csv', f'{top_dir}/data/GREET_LCA/marine_msd_mdo_05sulfur_wth_combustion.csv', commodity=commodity)
    
    # From SESAME
    #df_dict['truck_sesame'][commodity] = readSesameWtwTruck(, commodity=commodity)
    
    
def main():
    
    #plot_truck_emissions_per_class()
    df_lca, df_lca_payload_normalized = evaluateGreetWtwTruck(faf5_commodity='all')
    
    plot_truck_emissions_per_commodity(normalize_by_payload = False)
    plot_truck_emissions_per_commodity(normalize_by_payload = True)

    # Initialize an empty dictionary to contain the LCA dataframes
    df_lca_dict = {'truck': {}, 'rail': {}, 'ship': {}}

    fillLcaDf(df_lca_dict, top_dir=top_dir, commodity='all')

    # Add commodity-specific emissions
    # **NOTE** For the moment, commodity-specificity isn't yet implemented in the emissions calculation, so currently all the commodity-specific emission rates are identical to the 'all' rates. The 'for' loop below is simply a placeholder to help prepare for commodity-specific evaluation of emission rates.
    metaPath = f'{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx'
    meta = pd.ExcelFile(metaPath)
    commodities = pd.read_excel(meta, 'Commodity (SCTG2)')['Description']

    for commodity in commodities:
        fillLcaDf(df_lca_dict, top_dir=top_dir, commodity=commodity)
    
    #print(df_lca_dict)
    
    
main()
                              




