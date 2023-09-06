# FAF5 Analysis with QGIS

The purpose of this repo is to document the development of a geospatial analysis tool with QGIS that utilizes data from the "freight analysis framework" (FAF5) database. The ultimate goal is to evaluate lifecycle emissions associated with the transportation of freight flows, and incorporate these evaluated emissions into the geospatial visualization. 

Users can interact with QGIS either through the user interface ([link to user manual](https://docs.qgis.org/3.22/en/docs/user_manual/)), or via the Python API (links to [developer's cookbook](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/) and [API documentation](https://qgis.org/pyqgis/3.22/)). My general approach has been as follows:

1. Interact initially via the user interface (UI) to get a feel for the functionality available to perform whatever analysis I'm trying to do. 
2. Complete a first round of the analysis with the UI
3. Encode the analysis with the python API to make it reproducible and configurable. 

## Pre-requisites
* An installation of QGIS: [link to downloads for Mac, Windows and Linux](https://qgis.org/en/site/forusers/download.html)
* python3

## Setup

```bash
git clone git@github.com:cubicalknight/FAF5-Analysis.git
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
# from https://geodata.bts.gov/datasets/freight-analysis-framework-faf5-highway-network-assignments
wget "https://ago-item-storage.s3.us-east-1.amazonaws.com/9343414b46794fb8be9867db2d1ccb75/FAF5_Highway_Assignment_Results.zip?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEEQaCXVzLWVhc3QtMSJHMEUCIQCrLGO%2Fr8PJ8cc6BE8YSFaX2P%2BDADNbx2rW1%2FaT8vdmRQIgWAhElFIzmozsOQo8Tko1%2FJikKnI9oAJE2Ix9XYAUNUMq1QQI3f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2MDQ3NTgxMDI2NjUiDMfFqnbDfa8xOds7VSqpBFhDUITvXbPjoi0ha9ITvWXqhF%2Bb191Cz9c9Fv96aF8BBU4rw0WGZOUNZrKddpZxtJQx%2Ffz6EllAAhksvmtsv9Sf%2Ba1beFEIz6rqTOwceSC71CEQUKgd5JItSUFHMAbtXJyIB9MBG0van3zGyYl5JtW60ulv3KuPpkAnG8k8RhELLPix8qtp8DW%2BxY1Dapw2rfvETVRa9dPxsi8HYFeaVEBRuUCDQuE522qnKJOZoCj01z0rAArG1q4OyEFGXOrD6WiWuLGW0EuaGmLjxK9fd05tWfn5A7Oa7Y78gQsTQs8AKqyVCjIl8aExUq%2BTjdUDrNi3qBvtb51WM%2BMKXfmka4CCMPwpIlnAgPnoIxe1k1aXZpJgzyRS7ay6kOp7DVzrY49lciBZnMdxYbjlJMyEyyxlCgvtxJudBsI%2BMpcLV6lY520k9G7fDk%2BnPBqEzpMuIND8mT3RGU6y3w9SAbL21bGWaAOfFp1QS8FXVm6SN74UAo4GR1ISxZiLjao3jo7sMfDxyfVDF8n953L9HvS8tltjtlnG4jaJI4tXfiKT7kEU4FlN%2B6jgKqE6yQJ%2FeeUsZiHlBggYBkr1ei%2By4Kyl0kTDOMDaI9LGjJs%2FCkdttTiNI7zDfFGP9MYmDSrKFG7GJyQ3oJ6SeMJ39KcIuq36boE2jHvfUruOOMJL6IQFC6ez8hpjlLTach87aEXA56JEUNMASIc4vLBgz4njE6Z4tX4xMwliujd6CE8wj%2BnZnwY6qQEvi%2FemViSkkfkN8WsJH2nnwk4ZPxSNdiRzyFbMO67BF8z9Jvx7b5IuJ7%2Bi2h4Vdxx3yfxL%2BDQ5ipnbxSEPSyvzh%2BaRf14Lh32ey33oB8dxAgl%2F2Qba68wGYiq4JE%2F%2BuZleD5aECW9UzcfUVaTJ8Nm7JNAlv9ZS%2FSB2jQp%2Fkdc%2BdbfwCMJA4r0poC6k8uSGUpBqOqiWZiY11D3xfxkBzJNF6Xj56PBsTvtY&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230222T204330Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAYZTTEKKESMM3W3WB%2F20230222%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=cd310388a59d6ac0b48d6dc824337d152bc6e61aec0229a0e6ecabea490d8562" -O FAF5_highway_network_assignments.zip
unzip FAF5_highway_network_assignments.zip
rm FAF5_highway_network_assignments.zip
```

### FAF5 regional database 
```bash
# FAF5 regional database of tonnage and value by origin-destination pair, commodity type, and mode from 2018-2020 (from https://www.bts.gov/faf)
wget "https://faf.ornl.gov/faf5/data/download_files/FAF5.4.1_2018-2020.zip" -O FAF5_regional_od.zip
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
wget "https://opendata.arcgis.com/api/v3/datasets/23e16f24702948ac9e2032bfa0526a8f_1/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O egrid2020_subregions.zip
unzip egrid2020_subregions.zip -d egrid2020_subregions
rm egrid2020_subregions.zip
```

### eGRID grid intensity data
```bash
# from https://www.epa.gov/egrid/download-data
wget "https://www.epa.gov/system/files/documents/2023-01/eGRID2021_data.xlsx"
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

You can now cd back out of the data directory
```bash
cd ..
```

## How to run python scripts

Python scripts to encode analysis steps are stored in the [source](./source) directory. 

### Running scripts in QGIS

The following scripts should be run in QGIS: 
* [AnalyzeFAFData.py](./source/AnalyzeFAFData.py)
* [PlotWithQGIS.py](./source/PlotWithQGIS.py)

To run a script in QGIS:
1. Open up the QGIS GUI and press the `New Project` option (white page on the top left)
2. Select `Plugins --> Python Console` to open the python console.
3. Press the `Show Editor` option (white script icon at the top) to open an empty python script. 
4. Press the `Open Script...` option (yellow folder icon in the menu above the empty python script) to open an existing script. 
5. Execute the script by pressing the `Run Script` option (green play button in the menu above the python script). 

### Running scripts outside of QGIS
The following scripts should be run outside of QGIS:
* [Point2PointFAF.py](./source/Point2PointFAF.py)

Scripts run outside of QGIS should be executed directly with the python installation that was used to install the requirements in `requirements.txt`(./requirements.txt) (examples below).

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

This should produce a shapefile in `data/egrid2020_subregions_merged`.

## Processing electricity demand data

The script [rocessElectricityDemand.py](./source/ProcessElectricityDemand.py) reads in the shapefile containing the borders of US states, along with the associated electricity demand data, and joins the shapefile with the electricity demand data via the subregion ID to produce a combined shapefile.

To run:

```bash
python source/ProcessElectricityDemand.py
```

This should produce a shapefile in `data/electricity_demand_merged`.

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

The script [AnalyzeVius.py] produces distributions of GREET vehicle class, fuel type, age, and payload from the VIUS data. To run:

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

## Identifying truck stops and hydrogen production facilities within a given radius

The script [IdentifyFacilitiesInRadius.py](./source/IdentifyFacilitiesInRadius.py) 

## Visualizing layers with QGIS

The script [PlotWithQGIS.py](./PlotWithQGIS.py) reads in processed shapefiles containing:
* total imports and exports for all of the FAF5 regions 
* CO2e intensity (in lb/MWh) of the US powergrid
* Public charging and alternative refueling stations along highway corridors
* Highway links and assignments
* Electricity rates by state
* Demand charges by utility

and plots them as colormaps in QGIS. It also visualizes the network links as lines on the map, with the line width of each link weighted by its total annual freight flow (in tons). This should look something like:

Before running this code, you'll need to have run the following:

```bash
python source/processFAFHighwayData.py 
python source/ProcessGridData.py 
python source/ProcessElectricityDemand.py
python source/ProcessElectricityPrices.py 
```

as well as `python source/Point2PointFAF.py [arguments]` for any freight flow and emission intensity layers you'd like to visualize (more detailed instructions [above](./README.md#producing-shapefiles-to-visualize-freight-flows-and-emission-intensities)). Note that these layers currently need to be read in manually. 

<!-- Executing [PlotWithQGIS.py](./PlotWithQGIS.py) in the QGIS GUI (after first running [Point2PointFAF.py](./source/Point2PointFAF.py)) should produce output PDF files in the [layouts](./layouts) directory, which look something like: -->

![Total domestic exports](./images/highway_and_total_flows.png "Total Domestic Exports")


## Visualizing Shapefiles with a Web Interface

The code and shapefiles in [web_interface](./web_interface) represent an initial skeleton for functionality to visualize shapefiles interactively on a web interface. The code can be executed as follows:

```bash 
cd web_interface
python app.py
```

If that executes without issue, you should be able to view the map in your browser at http://127.0.0.1:5000/. It currently looks something like this:

![Interactive Web Map](./images/web_map.png "Interactive Web Map")
