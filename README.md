# FAF5 Analysis with QGIS

The purpose of this repo is to document the development of a geospatial analysis tool with QGIS that utilizes data from the "freight analysis framework" (FAF5) database. The ultimate goal is to evaluate lifecycle emissions associated with the transportation of freight flows, and incorporate these evaluated emissions into the geospatial visualization. 

Users can interact with QGIS either through the user interface ([link to user manual](https://docs.qgis.org/3.22/en/docs/user_manual/)), or via the Python API (links to [developer's cookbook](https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/) and [API documentation](https://qgis.org/pyqgis/3.22/)). My general approach has been as follows:

1. Interact initially via the user interface (UI) to get a feel for the functionality available to perform whatever analysis I'm trying to do. 
2. Complete a first round of the analysis with the UI
3. Encode the analysis with the python API to make it reproducible and configurable. 


## Pre-requisites
* An installation of QGIS: [link to downloads for Mac, Windows and Linux](https://qgis.org/en/site/forusers/download.html)

## How to run python scripts
Python scripts to encode analysis steps are stored in the [source](./source) directory. To run a script in QGIS:
1. Open up the QGIS GUI and press the `New Project` option (white page on the top left)
2. Select `Plugins --> Python Console` to open the python console.
3. Press the `Show Editor` option (white script icon at the top) to open an empty python script. 
4. Press the `Open Script...` option (yellow folder icon in the menu above the empty python script) to open an existing script. 
5. Execute the script by pressing the `Run Script` option (green play button in the menu above the python script). 

## Downloading the data

### FAF5 Regions

```bash
# FAF5 regions (from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-regions)
wget "https://opendata.arcgis.com/api/v3/datasets/e3bcc5d26e5e42709e2bacd6fc37ab43_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_regions.zip
unzip FAF5_regions.zip -d FAF5_regions
rm FAF5_regions.zip
```

### FAF5 Network Links

```bash
# FAF5 network links (from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links)
wget "https://opendata.arcgis.com/api/v3/datasets/cbfd7a1457d749ae865f9212c978c645_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_network_links.zip
unzip FAF5_network_links.zip -d FAF5_network_links
rm FAF5_network_links.zip
```

### FAF5 Highway Network Assignments
```bash
# FAF5 highway assignments (from https://geodata.bts.gov/datasets/freight-analysis-framework-faf5-highway-network-assignments)
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

## Analyzing highway assignments

The script [AnalyzeFAFData.py](./source/AnalyzeFAFData.py) encodes an initial geospatial analysis of the FAF5 highway network assignment data. Follow the [instructions above](#how-to-run-python-scripts) to execute the script in an empty project. Currently, the result should look something like this:

![Highway network assigmments in Texas](./images/texas_highway_Assignments.png "Texas Highway Network Assignments")

Currently, the script reads in shapefiles for the FAF5 network links and FAF5 regions for the entire US, and applies a filter to visualize only the state of Texas (mainly for tractability). It then reads in the highway network assignments for total trucking flows, joins the total flows for 2022 (all commodities combined) with the FAF5 network links via their common link IDs, and visualizes the network links as lines on the map, with the line width of each link weighted by its total annual freight flow (in tons). 
