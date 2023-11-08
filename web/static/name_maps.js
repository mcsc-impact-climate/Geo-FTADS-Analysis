export let selectedGradientTypes = {
  'Truck Imports and Exports': 'color',
  'Grid Emission Intensity': 'color',
  'Commercial Electricity Price': 'color',
  'Maximum Demand Charge': 'color',
  'Highway Flows (SU)': 'size',
  'Highway Flows (CU)': 'size',
  'Highway Flows (Interstate)': 'size',
  'Operational Electrolyzers': 'size',
  'Installed Electrolyzers': 'size',
  'Planned Electrolyzers': 'size',
  'Hydrogen from Refineries': 'size',
  'State-Level Incentives and Regulations': 'color',
  'Truck Stop Charging': 'size',
}

export const availableGradientAttributes = {
  'Truck Imports and Exports': ['Tmil Tot D', 'Tmil Imp D', 'Tmil Exp D', 'E Tot Den', 'E Imp Den', 'E Exp Den'],
  'Grid Emission Intensity': ['SRC2ERTA'],
  'Commercial Electricity Price': ['Cents_kWh'],
  'Maximum Demand Charge': ['MaxDemCh'],
  'Highway Flows (SU)': ['Tot Tons', 'Tot Trips'],
  'Highway Flows (CU)': ['Tot Tons', 'Tot Trips'],
  'Highway Flows (Interstate)': ['Tot Tons', 'Tot Trips'],
  'Operational Electrolyzers': ['Power_kW'],
  'Installed Electrolyzers': ['Power_kW'],
  'Planned Electrolyzers': ['Power_kW'],
  'Hydrogen from Refineries': ['Cap_MMSCFD'],
  'State-Level Incentives and Regulations': ['all', 'Biodiesel', 'Ethanol', 'Electricit', 'Hydrogen', 'Natural Ga', 'Propane', 'Renewable'],// 'Emissions'],
  'Truck Stop Charging': ['Tot Trips', 'CPD', 'Half_CPD', 'Min_Charge', 'Half_Charg', 'Min_Ratio', 'Half_Ratio', 'Col_Save'],
};

export let selectedGradientAttributes = {
  'Truck Imports and Exports': 'Tmil Tot D',
  'Grid Emission Intensity': 'SRC2ERTA',
  'Commercial Electricity Price': 'Cents_kWh',
  'Maximum Demand Charge': 'MaxDemCh',
  'Highway Flows (SU)': 'Tot Tons',
  'Highway Flows (CU)': 'Tot Tons',
  'Highway Flows (Interstate)': 'Tot Tons',
  'Operational Electrolyzers': 'Power_kW',
  'Installed Electrolyzers': 'Power_kW',
  'Planned Electrolyzers': 'Power_kW',
  'Hydrogen from Refineries': 'Cap_MMSCFD',
  'State-Level Incentives and Regulations': 'all',
  'Truck Stop Charging': 'Tot Trips',
};

export const legendLabels = {
  'Truck Imports and Exports': {
    'Tmil Tot D': 'Imports+Exports (ton-miles / sq mile)',
    'Tmil Imp D': 'Imports (ton-miles / sq mile)',
    'Tmil Exp D': 'Exports (ton-miles / sq mile)',
    'E Tot Den': 'Import+Export Emissions (tons CO2 / sq mile)',
    'E Imp Den': 'Import Emissions (tons CO2 / sq mile)',
    'E Exp Den': 'Export Emissions (tons CO2 / sq mile)'},
  'Grid Emission Intensity': {'SRC2ERTA': 'CO2e intensity of power grid (lb/MWh)'},
  'Commercial Electricity Price': {'Cents_kWh': 'Electricity rate (cents/kWh)'},
  'Maximum Demand Charge': {'MaxDemCh': 'Maximum Demand Charge by Utility ($/kW)'},
  'Highway Flows (Interstate)': {
    'Tot Tons': 'Highway Freight Flows (annual tons/link)',
    'Tot Trips': 'Highway Freight Flows (daily trips/link)'},
  'Highway Flows (SU)': {
    'Tot Tons': 'Single-unit Highway Freight Flows (annual tons/link)',
    'Tot Trips': 'Single-unit Highway Freight Flows (daily trips/link)'},
  'Highway Flows (CU)': {
    'Tot Tons': 'Combined-unit Highway Freight Flows (annual tons/link)',
    'Tot Trips': 'Combined-unit Highway Freight Flows (daily trips/link)'},
  'Operational Electrolyzers': {'Power_kW': 'Operational Hydrogen Electrolyzer Facility Capacity (kW)'},
  'Installed Electrolyzers': {'Power_kW': 'Installed Hydrogen Electrolyzer Facility Capacity (kW)'},
  'Planned Electrolyzers': {'Power_kW': 'Planned Hydrogen Electrolyzer Facility Capacity (kW)'},
  'Hydrogen from Refineries': {'Cap_MMSCFD': 'Hydrogen Production Capacity from Refinery (million standard cubic feet per day)'},
  'State-Level Incentives and Regulations': {
    'all': 'Incentives and Regulations (All Fuels)',
    'Biodiesel': 'Incentives and Regulations (Biodiesel)',
    'Ethanol': 'Incentives and Regulations (Ethanol)',
    'Electricit': 'Incentives and Regulations (Electricity)',
    'Hydrogen': 'Incentives and Regulations (Hydrogen)',
    'Natural Ga': 'Incentives and Regulations (Natural Gas)',
    'Propane': 'Incentives and Regulations (Propane)',
    'Renewable': 'Incentives and Regulations (Renewable Diesel)',
//    'Emissions': 'Incentives and Regulations (Emissions)',
 },
  'Truck Stop Charging': {
    'Tot Trips': 'Trucks Passing Per Day',
    'CPD': 'Truck Charges Per Day (Full Fleet)',
    'Half_CPD': 'Truck Charges Per Day (Half Fleet)',
    'Min_Charge': 'Min Chargers (Full Fleet)',
    'Half_Charg': 'Min Chargers (Half Fleet)',
    'Min_Ratio': 'Min Charger-to-truck Ratio (Full Fleet)',
    'Half_Ratio': 'Min Charger-to-truck Ratio (Half Fleet)',
    'Col_Save': 'Infra Savings from Pooled Investment (%)'},
};

export const fuelLabels = {
    'all': 'All Fuels',
    'Biodiesel': 'Biodiesel',
    'Ethanol': 'Ethanol',
    'Electricit': 'Electricity',
    'Hydrogen': 'Hydrogen',
    'Natural Ga': 'Natural Gas',
    'Propane': 'Propane',
    'Renewable': 'Renewable Diesel',
    'Emissions': 'Emissions',
}

export const truckChargingOptions = {
  'Range': {
    '150 miles': '100.0',
    '250 miles': '200.0',
    '350 miles': '300.0',
    '450 miles': '400.0'
    },
  'Charging Time': {
    '30 minutes': '0.5',
    '1 hour': '1.0',
    '2 hours': '2.0',
    '4 hours': '4.0'
    },
   'Max Allowed Wait Time': {
     '15 minutes': '0.25',
     '30 minutes': '0.5',
     '1 hour': '1.0',
     '2 hours': '2.0'
    }
};

export let selectedTruckChargingOptions = {
    'Range': '200.0',
    'Charging Time': '4.0',
    'Max Allowed Wait Time': '0.5'
};

export const stateSupportOptions = {
  'Support Type': {
    'Incentives and Regulations': 'incentives_and_regulations',
    'Incentives only': 'incentives',
    'Regulations only': 'regulations'
    },
  'Support Target': {
    'All Targets': 'all',
//    'Emissions only': 'emissions',
    'Fuel use only': 'fuel_use',
    'Infrastructure only': 'infrastructure',
    'Vehicle purchase only': 'vehicle_purchase'
    },
};

export let selectedStateSupportOptions = {
    'Support Type': 'incentives_and_regulations',
    'Support Target': 'all'
};

// Key: geojson name, Value: color to use
export const geojsonColors = {
  'Truck Imports and Exports': 'red',
  'Commercial Electricity Price': 'blue',
  'Highway Flows (SU)': 'cyan',
  'Highway Flows (Interstate)': 'black',
  'Operational Electrolyzers': 'DarkGreen',
  'Installed Electrolyzers': 'LimeGreen',
  'Planned Electrolyzers': 'GreenYellow',
  'Hydrogen from Refineries': 'grey',
  'East Coast ZEV Corridor': 'orange',
  'Midwest ZEV Corridor': 'purple',
  'Houston to LA H2 Corridor': 'green',
  'I-710 EV Corridor': 'magenta',
  'Northeast EV Corridor': 'cyan',
  'Bay Area EV Roadmap': 'yellow',
  'Salt Lake City Region EV Plan': 'red',
  'DCFC Chargers': 'red',
  'Hydrogen Stations': 'green',
  'LNG Stations': 'orange',
  'CNG Stations': 'purple',
  'LPG Stations': 'cyan',
  'Truck Stop Charging': 'red',
  'Principal Ports': 'purple',
};

// Key: geojson name, Value: color to use
export const geojsonTypes = {
  'Truck Imports and Exports': 'area',
  'Grid Emission Intensity': 'area',
  'Commercial Electricity Price': 'area',
  'Maximum Demand Charge': 'area',
  'State-Level Incentives and Regulations': 'area',
  'Highway Flows (Interstate)': ['highway', 'flow'],
  'Highway Flows (SU)': ['highway', 'flow'],
  'Highway Flows (CU)': ['highway', 'flow'],
  'Operational Electrolyzers': ['point', 'h2prod'],
  'Installed Electrolyzers': ['point', 'h2prod'],
  'Planned Electrolyzers': ['point', 'h2prod'],
  'Hydrogen from Refineries': ['point', 'h2prod'],
  'DCFC Chargers': ['point', 'refuel'],
  'Hydrogen Stations': ['point', 'refuel'],
  'LNG Stations': ['point', 'refuel'],
  'CNG Stations': ['point', 'refuel'],
  'LPG Stations': ['point', 'refuel'],
  'East Coast ZEV Corridor': ['highway', 'infra'],
  'Midwest ZEV Corridor': ['highway', 'infra'],
  'Houston to LA H2 Corridor': ['highway', 'infra'],
  'I-710 EV Corridor': ['highway', 'infra'],
  'Northeast EV Corridor': 'area',
  'Bay Area EV Roadmap': 'area',
  'Salt Lake City Region EV Plan': 'area',
  'Truck Stop Locations': ['point', 'other'],
  'Principal Ports': ['point', 'other'],
  'Truck Stop Charging': ['point', 'other']
};
