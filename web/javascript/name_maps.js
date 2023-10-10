export const geojsonLabels = {
  'Truck Imports and Exports': 'Imports+Exports (ton-miles / sq mile)',
  'Grid Emission Intensity': 'CO2e intensity of power grid (lb/MWh)',
  'Commercial Electricity Price': 'Electricity rate (cents/kWh)',
  'Maximum Demand Charge': 'Maximum Demand Charge by Utility ($/kW)',
  'Highway Flows (Interstate)': 'Highway Freight Flows (annual tons/link)',
  'Highway Flows (SU)': 'Single-unit Highway Freight Flows (annual tons/link)',
  'Highway Flows (CU)': 'Combined-unit Highway Freight Flows (annual tons/link)',
  'Operational Electrolyzers': 'Operational Hydrogen Electrolyzer Facility Capacity (kW)',
  'Installed Electrolyzers': 'Installed Hydrogen Electrolyzer Facility Capacity (kW)',
  'Planned Electrolyzers': 'Planned Hydrogen Electrolyzer Facility Capacity (kW)',
  'Hydrogen from Refineries': 'Hydrogen Production Capacity from Refinery (million standard cubic feet per day)',
  'State-Level Incentives and Regulations': 'Total Number of Incentives and Regulations',
};

export const gradientAttributes = {
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
};

// Key: geojson name, Value: color to use
export const geojsonColors = {
  'Truck Imports and Exports': 'red',
  'Commercial Electricity Price': 'blue',
  'Highway Flows (SU)': 'cyan',
  'Highway Flows (Interstate)': 'black',
  'Operational Electrolyzers': 'red',
  'Installed Electrolyzers': 'blue',
  'Planned Electrolyzers': 'green',
  'Hydrogen from Refineries': 'purple',
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
  'Principal Ports': ['point', 'other']
};