export let selectedGradientTypes = {
  'Truck Imports and Exports': 'color',
  'Grid Emission Intensity': 'color',
  'Commercial Electricity Price': 'color',
  'Maximum Demand Charge (utility-level)': 'color',
  'Maximum Demand Charge (state-level)': 'color',
  'Highway Flows (SU)': 'size',
  'Highway Flows (CU)': 'size',
  'Highway Flows (Interstate)': 'size',
  'Operational Electrolyzers': 'size',
  'Installed Electrolyzers': 'size',
  'Planned Electrolyzers': 'size',
  'Hydrogen from Refineries': 'size',
  'State-Level Incentives and Regulations': 'color',
  'Truck Stop Charging': 'size',
  'Lifecycle Truck Emissions': 'color',
  'Total Cost of Truck Ownership': 'color',
}

export const availableGradientAttributes = {
  'Truck Imports and Exports': ['Tmil Tot D', 'Tmil Imp D', 'Tmil Exp D', 'E Tot Den', 'E Imp Den', 'E Exp Den'],
  'Grid Emission Intensity': ['CO2_rate'],
  'Commercial Electricity Price': ['Cents_kWh'],
  'Maximum Demand Charge (utility-level)': ['MaxDemCh'],
  'Maximum Demand Charge (state-level)': ['Average Ma', 'Median Max', 'Max Maximu'],
  'Highway Flows (SU)': ['Tot Tons', 'Tot Trips'],
  'Highway Flows (CU)': ['Tot Tons', 'Tot Trips'],
  'Highway Flows (Interstate)': ['Tot Tons', 'Tot Trips'],
  'Operational Electrolyzers': ['Power_kW'],
  'Installed Electrolyzers': ['Power_kW'],
  'Planned Electrolyzers': ['Power_kW'],
  'Hydrogen from Refineries': ['Cap_MMSCFD'],
  'State-Level Incentives and Regulations': ['all', 'Biodiesel', 'Ethanol', 'Electricit', 'Hydrogen', 'Natural Ga', 'Propane', 'Renewable'],// 'Emissions'],
  'Truck Stop Charging': ['Tot Trips', 'CPD', 'Half_CPD', 'Min_Charge', 'Half_Charg', 'Min_Ratio', 'Half_Ratio', 'Col_Save'],
  'Lifecycle Truck Emissions': ['C_mi_tot', 'C_mi_grid'],
  'Total Cost of Truck Ownership': ['$_mi_tot', '$_mi_el'],
};

export let selectedGradientAttributes = {
  'Truck Imports and Exports': 'Tmil Tot D',
  'Grid Emission Intensity': 'CO2_rate',
  'Commercial Electricity Price': 'Cents_kWh',
  'Maximum Demand Charge (utility-level)': 'MaxDemCh',
  'Maximum Demand Charge (state-level)': 'Average Ma',
  'Highway Flows (SU)': 'Tot Tons',
  'Highway Flows (CU)': 'Tot Tons',
  'Highway Flows (Interstate)': 'Tot Tons',
  'Operational Electrolyzers': 'Power_kW',
  'Installed Electrolyzers': 'Power_kW',
  'Planned Electrolyzers': 'Power_kW',
  'Hydrogen from Refineries': 'Cap_MMSCFD',
  'State-Level Incentives and Regulations': 'all',
  'Truck Stop Charging': 'Tot Trips',
  'Lifecycle Truck Emissions': 'C_mi_tot',
  'Total Cost of Truck Ownership': '$_mi_tot'
};

export const legendLabels = {
  'Truck Imports and Exports': {
    'Tmil Tot D': 'Imports+Exports (ton-miles / sq mile)',
    'Tmil Imp D': 'Imports (ton-miles / sq mile)',
    'Tmil Exp D': 'Exports (ton-miles / sq mile)',
    'E Tot Den': 'Import+Export Emissions (tons CO2 / sq mile)',
    'E Imp Den': 'Import Emissions (tons CO2 / sq mile)',
    'E Exp Den': 'Export Emissions (tons CO2 / sq mile)'},
  'Grid Emission Intensity': {'CO2_rate': 'CO2 intensity of power grid (lb/MWh)'},
  'Commercial Electricity Price': {'Cents_kWh': 'Electricity rate (cents/kWh)'},
  'Maximum Demand Charge (utility-level)': {'MaxDemCh': 'Maximum Demand Charge by Utility ($/kW)'},
  'Maximum Demand Charge (state-level)': {'Average Ma': 'Average of Max Demand Charges over Utilities ($/kW)', 'Median Max': 'Median of Max Demand Charges over Utilities ($/kW)', 'Max Maximu': 'Maximum of Max Demand Charges over Utilities  ($/kW)'},
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
    
  'Lifecycle Truck Emissions': {
    'C_mi_tot': 'Total Emissions (g CO2e / mile)',
    'C_mi_grid': 'Emissions from Charging (g CO2e / mile)',
    'C_mi_man': 'Emissions from Battery Manufacturing (g CO2e / mile)',
    },
    
  'Total Cost of Truck Ownership': {
    '$_mi_tot': 'Total Cost ($ / mile)',
    '$_mi_cap': 'Capital Cost ($ / mile)',
    '$_mi_el': 'Electricity Cost ($ / mile)',
    '$_mi_lab': 'Labor Cost ($ / mile)',
    '$_mi_op': 'Operating Cost ($ / mile)',
    },
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

export const tcoOptions = {
  'Average Payload': {
    '0 lb': '0',
    '10,000 lb': '10000',
    '20,000 lb': '20000',
    '30,000 lb': '30000',
    '40,000 lb': '40000',
    '50,000 lb': '50000'
    },
  'Average VMT': {
    '40,000 miles': '40000',
    '70,000 miles': '70000',
    '100,000 miles': '100000',
    '130,000 miles': '130000',
    '160,000 miles': '160000',
    '190,000 miles': '190000',
    },
    'Max Charging Power': {
      '100 kW': '100',
      '200 kW': '200',
      '400 kW': '400',
      '800 kW': '800',
      },
};

export let selectedTcoOptions = {
    'Average Payload': '40000',
    'Average VMT': '100000',
    'Max Charging Power': '400'
};

export const emissionsOptions = {
  'Average Payload': {
    '0 lb': '0',
    '10,000 lb': '10000',
    '20,000 lb': '20000',
    '30,000 lb': '30000',
    '40,000 lb': '40000',
    '50,000 lb': '50000'
    },
  'Average VMT': {
    '40,000 miles': '40000',
    '70,000 miles': '70000',
    '100,000 miles': '100000',
    '130,000 miles': '130000',
    '160,000 miles': '160000',
    '190,000 miles': '190000',
    },
    'Visualize By': {
        'State': 'state_',
        'Balancing Authority': 'ba_'
    }
};

export let selectedEmissionsOptions = {
    'Average Payload': '40000',
    'Average VMT': '100000',
    'Visualize By': 'State'
};

export const gridEmissionsOptions = {
  'Visualize By': {
    'State': 'eia2022_state',
    'Balancing authority': 'egrid2022_subregions'
    }
};

export let selectedGridEmissionsOptions = {
    'Visualize By': 'State'
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
  'Direct Current Fast Chargers': 'red',
  'Hydrogen Stations': 'green',
  'LNG Stations': 'orange',
  'CNG Stations': 'purple',
  'LPG Stations': 'cyan',
  'Truck Stop Charging': 'red',
  'Principal Ports': 'purple',
};

// Key: geojson name, Value: either 'area' (indicating it's an area feature) or [feature type: category], where each feature type can be divided into several categories
export const geojsonTypes = {
  'Truck Imports and Exports': 'area',
  'Grid Emission Intensity': 'area',
  'Commercial Electricity Price': 'area',
  'Maximum Demand Charge (utility-level)': 'area',
  'Maximum Demand Charge (state-level)': 'area',
  'State-Level Incentives and Regulations': 'area',
  'Highway Flows (Interstate)': ['highway', 'flow'],
  'Highway Flows (SU)': ['highway', 'flow'],
  'Highway Flows (CU)': ['highway', 'flow'],
  'Operational Electrolyzers': ['point', 'h2prod'],
  'Installed Electrolyzers': ['point', 'h2prod'],
  'Planned Electrolyzers': ['point', 'h2prod'],
  'Hydrogen from Refineries': ['point', 'h2prod'],
  'Direct Current Fast Chargers': ['point', 'refuel'],
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
  'Truck Stop Charging': ['point', 'other'],
  'Lifecycle Truck Emissions': 'area',
  'Total Cost of Truck Ownership': 'area',
};

export const dataInfo = {
  'Truck Imports and Exports': "Freight flow data from the FWHA's <a href='https://ops.fhwa.dot.gov/freight/freight_analysis/faf/'>Freight Analysis Framework</a> (<a href='https://opendata.arcgis.com/api/v3/datasets/e3bcc5d26e5e42709e2bacd6fc37ab43_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1'>link to download shapefile used for FAF5 region boundaries</a>). Emissions attributes are evaluated by incorporating data from the <a href='https://rosap.ntl.bts.gov/view/dot/42632/dot_42632_DS2.zip'>2002 Vehicle Inventory and Use Survey</a> and the <a href='https://greet.anl.gov/'>GREET lifecycle emissions tool</a> maintained by Argonne National Lab.",
  'Grid Emission Intensity': "Emission intensity data is obtained from the <a href='https://www.epa.gov/egrid/download-data'>eGRID database</a> (<a href='https://www.epa.gov/system/files/documents/2023-01/eGRID2021_data.xlsx'>link to download</a>). eGRID subregion boundaries are obtained from <a href='https://hub.arcgis.com/datasets/fedmaps::subregions-of-the-emissions-generation-resource-integrated-database-egrid/'>this ArcGIS Hub page</a> (<a href='https://opendata.arcgis.com/api/v3/datasets/23e16f24702948ac9e2032bfa0526a8f_1/downloads/data?format=shp&spatialRefId=4326&where=1%3D1'>link to download</a>)",
  'Commercial Electricity Price': "Data is obtained from the <a href='https://www.eia.gov/electricity/data.php'>EIA's Electricity database</a> (<a href='https://www.eia.gov/electricity/data/state/sales_annual_a.xlsx'>link to download</a>).",
  'Maximum Demand Charge (state-level)': "The maximum historical demand charge in each utility region is evaluated using historical demand charge data compiled by the National Renewable Energy Lab (NREL) in <a href='https://data.nrel.gov/submissions/74'>this NREL Data Catalog</a> (<a href='https://data.nrel.gov/system/files/74/Demand%20charge%20rate%20data.xlsm'>link to download</a>).",
  'Maximum Demand Charge (utility-level)': "Maximum historical demand charges for each state are evaluated using historical demand charge data compiled by the National Renewable Energy Lab (NREL) in <a href='https://data.nrel.gov/submissions/74'>this NREL Data Catalog</a> (<a href='https://data.nrel.gov/system/files/74/Demand%20charge%20rate%20data.xlsm'>link to download</a>).",
  'State-Level Incentives and Regulations': "This data was collected by manually combing through the DOE AFDC's <a href='https://afdc.energy.gov/laws/state'>State Laws and Incentives Database</a> and collecting relevant information about laws and incentives that could be relevant for heavy duty trucking.",
  'Highway Flows (Interstate)': "This layer was obtained by combining the <a href='https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links'>FAF5 network links</a> (<a href='https://opendata.arcgis.com/api/v3/datasets/cbfd7a1457d749ae865f9212c978c645_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1'>link to download</a>) with the 2022 FAF5 Highway Network Assignments from the <a href='https://ops.fhwa.dot.gov/freight/freight_analysis/faf/'>FAF5 website</a> (<a href='https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2022_HighwayAssignmentResults_04_07_2022.zip'>link to download</a>), and selecting for links on the interstate system.",
  'Operational Electrolyzers': "Data on operational electrolyzers was extracted from a <a href='https://www.hydrogen.energy.gov/docs/hydrogenprogramlibraries/pdfs/23003-electrolyzer-installations-united-states.pdf?Status=Master'>DOE Hydrogen program record</a> entitled 'Electrolyzer Installations in the United States' and dated June 2, 2023.",
  'Installed Electrolyzers': "Data on installed electrolyzers was extracted from a <a href='https://www.hydrogen.energy.gov/docs/hydrogenprogramlibraries/pdfs/23003-electrolyzer-installations-united-states.pdf?Status=Master'>DOE Hydrogen program record</a> entitled 'Electrolyzer Installations in the United States' and dated June 2, 2023.",
  'Planned Electrolyzers': "Data on planned electrolyzers was extracted from a <a href='https://www.hydrogen.energy.gov/docs/hydrogenprogramlibraries/pdfs/23003-electrolyzer-installations-united-states.pdf?Status=Master'>DOE Hydrogen program record</a> entitled 'Electrolyzer Installations in the United States' and dated June 2, 2023.",
  'Hydrogen from Refineries': "Locations and production rates of hydrogen from refineries are obtained from the following two complementary datasets on the <a href='https://h2tools.org'>Hydrogen Tools Portal</a>:<br> 1) <a href='https://h2tools.org/hyarc/hydrogen-data/captive-purpose-refinery-hydrogen-production-capacities-individual-us'>Captive, On-Purpose, Refinery Hydrogen Production Capacities at Individual U.S. Refineries<a> (<a href='https://h2tools.org/file/9338/download?token=0IWTving'>link to download</a>), and <br>2) <a href='https://h2tools.org/hyarc/hydrogen-data/merchant-hydrogen-plant-capacities-north-america'>Merchant Hydrogen Plant Capacities in North America</a> (<a href='https://h2tools.org/file/196/download?token=BNg4dM46'>link to download</a>)",
  'Direct Current Fast Chargers': "Locations of Direct Current Fast Chargers with at least 4 ports and an output of at least 150 kW. Includes passenger vehicle charging stations. Obtained from the DOE AFDC's <a href='https://afdc.energy.gov/corridors'>Station Data for Alternative Fuel Corridors</a>",
  'Hydrogen Stations': "Locations of retail hydrogen fueling stations. Includes passenger vehicle refueling stations. Obtained from the DOE AFDC's <a href='https://afdc.energy.gov/corridors'>Station Data for Alternative Fuel Corridors</a>",
  'LNG Stations': "Locations of liquified natural gas (LNG) fueling stations. Includes passenger vehicle refueling stations. Obtained from the DOE AFDC's <a href='https://afdc.energy.gov/corridors'>Station Data for Alternative Fuel Corridors</a>",
  'CNG Stations': "Locations of fast-fill compressed natural gas (CNG) fueling stations. Includes passenger vehicle refueling stations. Obtained from the DOE AFDC's <a href='https://afdc.energy.gov/corridors'>Station Data for Alternative Fuel Corridors</a>",
  'LPG Stations': "Locations of primary liquified petroleum gas (LPG) fueling stations. Includes passenger vehicle refueling stations. Obtained from the DOE AFDC's <a href='https://afdc.energy.gov/corridors'>Station Data for Alternative Fuel Corridors</a>",
  'East Coast ZEV Corridor': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will launch an intensive strategic planning effort to spur the deployment of commercial medium- and heavy-duty (MHD) zero-emission vehicle (ZEV) infrastructure through the development of an East Coast Commercial ZEV Corridor along the I-95 freight corridor from Georgia to New Jersey.",
  'Midwest ZEV Corridor': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will develop an extensive two-phase MD-HD EV Charging and H2 Fueling Plan for the Midwest I-80 corridor serving Indiana, Illinois, and Ohio, to support 30% of the MD-HD fleet using ZEV technologies by 2035.",
  'Houston to LA H2 Corridor': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will develop a flexible and scalable blueprint plan for an investment-ready hydrogen fueling and heavy-duty freight truck network from Houston to LA (H2LA) along I-10, including the Texas Triangle region, and in the process develop methodology for future corridor plans across the country. ",
  'I-710 EV Corridor': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will create a plan for innovative infrastructure solutions at industrial facilities and commercial zones along critical freight arteries feeding into Southern California’s I-710 freeway. The project will explore how private sector fleets can establish an integrated network that leverages existing industrial and commercial real estate assets while providing greatest benefit to municipalities and communities.",
  'Northeast EV Corridor': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will forecast electric charging demand at traffic stops on freight corridors across Maine, Massachusetts, New Hampshire, Vermont, Rhode Island, Connecticut, New York, Pennsylvania, and New Jersey to help inform a blueprint for future large-scale, least-cost deployment of commercial EV charging and serve as an exemplar for other regions.",
  'Bay Area EV Roadmap': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will create a roadmap for charging infrastructure to support the full electrification of three key trucking market segments – drayage, regional haul, and long-haul – in the Bay Area of California. ",
  'Salt Lake City Region EV Plan': "Shows the highway corridor targeted for one of 7 heavy duty vehicle infrastructure projects funded by the Biden-Harris administration (<a href='https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle'>link to announcement</a> from Feb. 15, 2023). <br>This project will develop a community, state and industry supported action plan that will improve air quality in the underserved communities most impacted by high-density medium- and heavy-duty traffic in the greater Salt Lake City region. ",
  'Truck Stop Locations': "Locations of truck stops parking facilities in the U.S. Obtained from the DOT Bureau of Transportation Statistics's <a href='https://geodata.bts.gov/datasets/usdot::truck-stop-parking'>Truck Stop Parking database</a> (<a href='https://opendata.arcgis.com/api/v3/datasets/0849b1bd4a5e4b4e831877b7c25d6062_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1'>link to download</a>)",
  'Principal Ports': "Locations of principal ports in the US. Obtained from <a href='https://geodata.bts.gov/datasets/usdot::principal-ports/'>USDOT BTS</a> (<a href='https://opendata.arcgis.com/api/v3/datasets/e3b6065cce144be8a13a59e03c4195fe_1/downloads/data?format=shp&spatialRefId=4326&where=1%3D1'>link to download</a>).",
  'Truck Stop Charging': "These layers are used to visualize an analysis of theoretical savings from pooled investment in charging infrastructure at selected U.S. truck stops. The analysis integrates truck stop locations in the U.S. (see 'Truck Stop Locations' layer for details), along with highway freight flow data from the Freight Analysis Framework - see 'Highway Flows (Interstate)' layer for details.",
  'Lifecycle Truck Emissions': "Estimated lifecycle emissions per mile for the Tesla Semi due to charging and battery manufacturing. Charging emissions are based on the CO2e emission intensity of the grid balancing authority region. Emissions are calculated using the model developed by <a href='https://chemrxiv.org/engage/chemrxiv/article-details/656e4691cf8b3c3cd7c96810'>Sader et al.</a>, calibrated to <a href='https://runonless.com/run-on-less-electric-depot-reports/'>NACFE Run on Less data</a> for the Tesla Semi from the 2023 PepsiCo Semi pilot.<br><br><a href='https://github.com/mcsc-impact-climate/Green_Trucking_Analysis'>Link to Git repo with code used to produce these layers</a>",
  'Total Cost of Truck Ownership': "Estimated lifecycle total cost of ownership per mile for the Tesla Semi due to truck purchase, charging, labor, maintenance, insurance and other operating costs. Charging costs are evaluated using state-level commercial electricity price and demand charge. Costs are calculated using the model developed by <a href='https://chemrxiv.org/engage/chemrxiv/article-details/656e4691cf8b3c3cd7c96810'>Sader et al.</a>, calibrated to <a href='https://runonless.com/run-on-less-electric-depot-reports/'>NACFE Run on Less data</a> for the Tesla Semi from the 2023 PepsiCo Semi pilot.<br><br><a href='https://github.com/mcsc-impact-climate/Green_Trucking_Analysis'>Link to Git repo with code used to produce these layers</a>",
};

