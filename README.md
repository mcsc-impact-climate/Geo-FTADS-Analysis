# Interactive geospatial decision support tool for trucking fleet decarbonization

This repo contains code to produce and interactively visualize publicly available geospatial data to support trucking fleets in navigating the transition to alternative energy carriers. The tool uses data from the "freight analysis framework" (FAF5) database and other public data sources.

## Pre-requisites
* python3

## Setup

```bash
git clone git@github.com:mcsc-impact-climate/FAF5-Analysis.git
```

Install python requirements
```bash
pip install -r requirements.txt
```

## Downloading the data

Cd into the data directory
```bash
cd data
```

### FAF5 Regions
```bash
# from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-regions
wget "https://opendata.arcgis.com/api/v3/datasets/e3bcc5d26e5e42709e2bacd6fc37ab43_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_regions.zip
unzip FAF5_regions.zip -d FAF5_regions
rm FAF5_regions.zip
```

### FAF5 Network Links
```bash
# from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links
wget "https://opendata.arcgis.com/api/v3/datasets/cbfd7a1457d749ae865f9212c978c645_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_network_links.zip
unzip FAF5_network_links.zip -d FAF5_network_links
rm FAF5_network_links.zip
```

### FAF5 Highway Network Assignments
```bash
# from https://ops.fhwa.dot.gov/freight/freight_analysis/faf/

mkdir -p FAF5_Highway_Assignment_Results
cd FAF5_Highway_Assignment_Results
wget https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2017_HighwayAssignmentResults_04_07_2022.zip
unzip FAF5_2017_HighwayAssignmentResults_04_07_2022.zip -d FAF5_2017_Highway_Assignment_Results
rm FAF5_2017_HighwayAssignmentResults_04_07_2022.zip

wget https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2022_HighwayAssignmentResults_04_07_2022.zip
unzip FAF5_2022_HighwayAssignmentResults_04_07_2022.zip -d FAF5_2022_Highway_Assignment_Results
rm FAF5_2022_HighwayAssignmentResults_04_07_2022.zip

wget https://ops.fhwa.dot.gov/freight/freight_analysis/faf/faf_highway_assignment_results/FAF5_2050_HighwayAssignmentResults_09_17_2022.zip
unzip FAF5_2050_HighwayAssignmentResults_04_07_2022.zip -d FAF5_2050_Highway_Assignment_Results
rm FAF5_2050_HighwayAssignmentResults_04_07_2022.zip

cd ..
```

### FAF5 regional database 
```bash
# FAF5 regional database of tonnage and value by origin-destination pair, commodity type, and mode from 2018-2022 (from https://www.bts.gov/faf)
wget "https://faf.ornl.gov/faf5/data/download_files/FAF5.5.1_2018-2022.zip" -O FAF5_regional_od.zip
unzip FAF5_regional_od.zip -d FAF5_regional_flows_origin_destination
rm FAF5_regional_od.zip
```

### Vehicle Inventory and Use Survey (VIUS) data
```bash
# from https://www.bts.gov/faf
wget "https://rosap.ntl.bts.gov/view/dot/42632/dot_42632_DS2.zip" -O VIUS_2002.zip
unzip VIUS_2002.zip -d VIUS_2002
rm VIUS_2002.zip
```

### Subregions for eGRID grid intensity data
```bash
# from ls
wget https://www.epa.gov/system/files/other-files/2023-05/eGRID2021_subregions_shapefile.zip
unzip eGRID2021_subregions_shapefile.zip -d eGRID2021_subregions
rm eGRID2021_subregions_shapefile.zip
```

### eGRID grid intensity data
```bash
# from https://www.epa.gov/egrid/download-data
wget "https://www.epa.gov/system/files/documents/2024-01/egrid2022_data.xlsx"
```

### EIA grid emission intensity by state
```bash
# from https://www.eia.gov/electricity/data/emissions/
wget "https://www.eia.gov/electricity/data/emissions/xls/emissions_region2022.xlsx"
```

### EIA net summer capacity by state (MW)
```bash
# from https://www.eia.gov/electricity/data/state/
wget "https://www.eia.gov/electricity/data/state/existcapacity_annual.xlsx"
```
### EIA proposed additions to net summer capacity by state: 2023-2027 (MW)
```bash
# from https://www.eia.gov/electricity/data/state/
wget "https://www.eia.gov/electricity/data/state/plancapacity_annual.xlsx"
```

### EIA net annual generation by state (MWh)
```bash
# from https://www.eia.gov/electricity/annual/
wget "https://www.eia.gov/electricity/data/state/annual_generation_state.xls"
```

### US zip code boundaries
```bash
# from https://hub.arcgis.com/datasets/d6f7ee6129e241cc9b6f75978e47128b
wget "https://opendata.arcgis.com/api/v3/datasets/d6f7ee6129e241cc9b6f75978e47128b_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O zip_code_regions.zip
unzip zip_code_regions.zip -d zip_code_regions
rm zip_code_regions.zip
```

### US state boundaries
```bash
# from https://www.sciencebase.gov/catalog
wget "https://www.sciencebase.gov/catalog/file/get/52c78623e4b060b9ebca5be5?facet=tl_2012_us_state" -O state_boundaries.zip
unzip state_boundaries.zip -d state_boundaries
rm state_boundaries.zip
```

### Electricity rate data per state
```bash
# from https://www.eia.gov/electricity/data.php
mkdir -p electricity_rates
wget "https://www.eia.gov/electricity/data/state/sales_annual_a.xlsx" -O electricity_rates/sales_annual_a.xlsx
```

### Electricity rate data per zip code
```bash
# from https://catalog.data.gov/dataset/u-s-electric-utility-companies-and-rates-look-up-by-zipcode-2020
mkdir -p electricity_rates
wget "https://data.openei.org/files/5650/iou_zipcodes_2020.csv" -O electricity_rates/iou_zipcodes_2020.csv
```

### Maximum demand charge data (compiled by NREL in 2017)
```bash
# from https://data.nrel.gov/submissions/74
wget "https://data.nrel.gov/system/files/74/Demand%20charge%20rate%20data.xlsm" -O Demand_charge_rate_data.xlsm
```

### Electricity utility boundaries
```bash
# from https://atlas.eia.gov/datasets/f4cd55044b924fed9bc8b64022966097_0
wget "https://opendata.arcgis.com/api/v3/datasets/f4cd55044b924fed9bc8b64022966097_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O utility_boundaries.zip
unzip utility_boundaries.zip -d utility_boundaries
rm utility_boundaries.zip
```

### Electricity balancing authority boundaries
```bash
# from https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::electric-planning-areas/about
wget "https://opendata.arcgis.com/api/v3/datasets/7d35521e3b2c48ab8048330e14a4d2d1_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O balancing_authority_boundaries.zip
unzip balancing_authority_boundaries.zip -d balancing_authority_boundaries
rm balancing_authority_boundaries.zip
```

### Power demand by balancing authority
```bash
# from https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48
mkdir -p power_demand_by_balancing_authority
wget "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jul_Dec.csv" -O power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jul_Dec.csv
wget "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jan_Jun.csv" -O power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jan_Jun.csv
```

### Power demand by state
```bash
# from https://www.eia.gov/electricity/data/state/
wget https://www.eia.gov/electricity/data/state/existcapacity_annual.xlsx
```

### U.S. Primary Roads National Shapefile
```bash
# from https://catalog.data.gov/dataset/tiger-line-shapefile-2019-nation-u-s-primary-roads-national-shapefile
wget https://www2.census.gov/geo/tiger/TIGER2019/PRIMARYROADS/tl_2019_us_primaryroads.zip
unzip tl_2019_us_primaryroads.zip -d tl_2019_us_primaryroads
rm tl_2019_us_primaryroads.zip
```

### Bay area county boundaries
```bash
# from https://geodata.lib.berkeley.edu/catalog/ark28722-s7hs4j
wget https://spatial.lib.berkeley.edu/public/ark28722-s7hs4j/data.zip
unzip data.zip -d bay_area_counties
rm data.zip
```

### Counties in Utah
```bash
# from https://gis.utah.gov/data/boundaries/citycountystate/
wget https://opendata.arcgis.com/datasets/90431cac2f9f49f4bcf1505419583753_0.zip
unzip 90431cac2f9f49f4bcf1505419583753_0.zip -d utah_counties
rm 90431cac2f9f49f4bcf1505419583753_0.zip
```

### Truck stop parking data
```bash
# from https://geodata.bts.gov/datasets/usdot::truck-stop-parking
wget --no-check-certificate -O Truck_Stop_Parking.zip "https://opendata.arcgis.com/api/v3/datasets/0849b1bd4a5e4b4e831877b7c25d6062_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1"
unzip Truck_Stop_Parking.zip -d Truck_Stop_Parking
rm Truck_Stop_Parking.zip
```

### US power industry report for 2017
```bash
# From https://www.eia.gov/electricity/data/eia861/
wget https://www.eia.gov/electricity/data/eia861/archive/zip/f8612017.zip -O US_Power_Industry_Report_2017.zip
unzip US_Power_Industry_Report_2017.zip -d US_Power_Industry_Report_2017
mv US_Power_Industry_Report_2017/Utility_Data_2017.xlsx .
rm -r US_Power_Industry_Report_2017*
```

You can now cd back out of the data directory
```bash
cd ..
```

## How to run python scripts

Python scripts to encode analysis steps are stored in the [source](./source) directory. 

## Processing highway assignments

The script [ProcessFAFHighwayData.py](./source/ProcessFAFHighwayData.py) reads in both the FAF5 network links for the entire US and the associated highway network assignments for total trucking flows, and joins the total flows for 2022 (all commodities combined) with the FAF5 network links via their common link IDs to produce a combined shapefile.

To run:

```bash
python processFAFHighwayData.py 
```

This should produce a shapefile in `data/highway_assignment_links`.

## Processing eGRID emission intensity data

The script [ProcessGridData.py](./source/ProcessGridData.py) reads in the shapefile containing the borders of subregions within which eGRIDs reports grid emissions data, along with the associated eGRIDs data, and joins the shapefile with the eGRIDs data via the subregion ID to produce a combined shapefile.

To run:

```bash
python source/ProcessGridData.py 
```

This should produce shapefiles in `data/egrid2020_subregions_merged` and `data/eia2020_subregions_merged`.

## Processing electricity prices and demand charges

The script [ProcessElectricityPrices.py](./source/ProcessElectricityPrices.py) reads in the shapefile containing borders of zip codes and states, along with the associated electricity price data and demand charges, and joins the shapefiles with the electricity price data via the subregion ID to produce combined shapefiles.

To run:

```bash
python source/ProcessElectricityPrices.py 
```

## Processing State-level Incentives and Regulations

The script [ProcessStateSupport.py](./source/ProcessStateSupport.py) reads in the shapefile containing borders of US states, along with CSV files containing state-level incentives relevant to trucking from the [AFDC website](https://afdc.energy.gov/laws/state), and joins the CSV files with the shapefile to produce a set of shapefiles with the number of incentives of each type (fuel, vehicle purchase, emissions and infrastructure) and fuel target (electrification, hydrogen, ethanol, etc.) for each state. 

To run:

```bash
python source/ProcessStateSupport.py
```

# Processing planned infrastructure corridors for heavy duty vehicles

The script [PrepareInfrastructureCorridors.py](./source/PrepareInfrastructureCorridors.py) reads in either a shapefile with the US highway system, or shapefiles with specific regions of planned heavy duty vehicle infrastructure corridors [announced by the Biden-Harris administration](https://www.energy.gov/articles/biden-harris-administration-announces-funding-zero-emission-medium-and-heavy-duty-vehicle). For corridors represented as subsets of the national highway system, the code produces shapefiles for each highway segment with a planned infrastructure project. For corridors represented as regions of the US, the code produces shapefiles showing the region(s) where the planned infrastructure project will take place. 

To run:

```bash
python source/PrepareInfrastructureCorridors.py
```

This should produce shapefiles for zipcode-level and state-level electricity prices in `data/electricity_rates_merged`

## Analyzing VIUS data

The script [AnalyzeVius.py](./source/AnalyzeVius.py) produces distributions of GREET vehicle class, fuel type, age, and payload from the VIUS data. To run:

```bash
python source/AnalyzeVius.py
```

## Processing VIUS data to evaluate average product of fuel efficiency and payload

Run the script [ViusTools.py](./source/ViusTools.py) to produce an output file tabulating the product of fuel efficiency (mpg) times payload for each commodity, along with the associated standard deviation:

```bash
python source/ViusTools.py
```

This should produce the following output file: `data/VIUS_Results/mpg_times_payload.csv`. 

## Producing shapefiles to visualize freight flows and emission intensities

The script [Point2PointFAF.py](./source/Point2PointFAF.py) combines outputs from VIUS, GREET and FAF5 and merges it with geospatial shapefiles with the contours of FAF5 regions to associate each region with tons, ton-miles, and associated emissions of imports to and exports from each region, along with areal densities of these three quantities (i.e. divided by the surface area of the associated region). There is also functionality to evaluate these quantities for a user-specified mode, commodity, origin region, or destination region. 

Before running this code, you'll need to have first run the following:

```bash
python source/ViusTools.py
```

To run:

```bash
python source/Point2PointFAF.py -m user_specified_mode -c "user_specified_commodity" -o user_specified_origin_ID -d user_specified_destination_ID
```

This should produce a csv and shapefile in `data/Point2Point_outputs/mode_truck_commodity_Logs_origin_11_dest_all.[extension]`. 

NOTE: The "" around the commodity option is important because some commodities contain spaces, and python does NOT like command line arguments with spaces...

where each argument defaults to 'all' if left unspecified. The mode is one of {all, truck, water, rail}. The available commodities can be found in the 'Commodity (SCTG2)' sheet in `data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx` ('Description' column). The origin and destination region IDs can be found in the 'FAF Zone (Domestic)' sheet of the same excel file ('Numeric Label' column'). 

For example, to filter for logs carried by trucks from FAF5 region 11 to FAF5 region 139:

```bash
python source/Point2PointFAF.py -m truck -c Logs -o 11 -d 139
```

There's also a bash script in `source/run_all_Point2Point.sh` that can be executed to produce merged shapefiles for all combinations of modes, commodities, origins and destinations. 

To run:

```bash
bash source/run_all_Point2Point.sh
```

WARNING: This may take several hours to run in full, and the shapefiles and csv files produced will take up ~100 GB. To reduce this, you can comment out items that you don't want in the COMMODITIES, REGIONS and MODES variables.

## Creating shapefiles for hydrogen production facilities

The script [PrepareHydrogenHubs.py](./source/PrepareHydrogenHubs.py) combines locations and information about operating and planned hydrogen production facilities and the U.S. and Canada into shapefiles located in `data/hydrogen_hubs/shapefiles`. To run:

```bash
python source/PrepareHydrogenHubs.py
```

## Identifying truck stops and hydrogen production facilities within a given radius

The script [IdentifyFacilitiesInRadius.py](./source/IdentifyFacilitiesInRadius.py) identifies truck stops and hydrogen production facilities within a user-provided radius and central location - (33N, 97W) and 600 miles by default.

## Analyze potential infrastructure investment savings from collective investment in truck stop charging

The script [AnalyzeTruckStopCharging.py](./source/AnalyzeTruckStopCharging.py) is designed to quantify the charging demand at truck stops separated by 100 miles on average and at least 50 miles, and estimate the potential difference in infrastructure costs needed if the entire electrified trucking fleet were to electrify and either:
* The full electrified fleet shared the investment and usage of charging infrastructure, or
* The fleet was divided in half, and each half invested in and used their respective charging infrastructure separately. 

The idea of this exercise is to understand the potential infrastructure savings from trucking fleets pooling infrastructure investments in charging infrastructure based on real-world freight flow data. 

To run:

```bash
python source/AnalyzeTruckStopCharging.py
```

## Running the geospatial mapping tool

The code in [web](./web) contains all functionality to visualize the geojsons interactively on a web interface. The code can be executed as follows:

```bash
# Install python requirements if needed
install -r requirements.txt
```

```bash 
python manage.py runserver
```

If that executes without issue, you should be able to view the map in your browser at http://127.0.0.1:5000/. It currently looks something like this:

![Interactive Web Map](./images/web_map.png)
