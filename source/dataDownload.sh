#!/bin/sh

echo "Running data download..."
cd data/


# from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-regions
wget "https://opendata.arcgis.com/api/v3/datasets/e3bcc5d26e5e42709e2bacd6fc37ab43_0/downloads/data format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_regions.zip

unzip FAF5_regions.zip -d FAF5_regions
rm FAF5_regions.zip


# from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links
wget "https://opendata.arcgis.com/api/v3/datasets/cbfd7a1457d749ae865f9212c978c645_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_network_links.zip

unzip FAF5_network_links.zip -d FAF5_network_links
rm FAF5_network_links.zip


# from https://geodata.bts.gov/datasets/freight-analysis-framework-faf5-highway-network-assignments
wget "https://ago-item-storage.s3.us-east-1.amazonaws.com/9343414b46794fb8be9867db2d1ccb75/FAF5_Highway_Assignment_Results.zip?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEEQaCXVzLWVhc3QtMSJHMEUCIQCrLGO%2Fr8PJ8cc6BE8YSFaX2P%2BDADNbx2rW1%2FaT8vdmRQIgWAhElFIzmozsOQo8Tko1%2FJikKnI9oAJE2Ix9XYAUNUMq1QQI3f%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgw2MDQ3NTgxMDI2NjUiDMfFqnbDfa8xOds7VSqpBFhDUITvXbPjoi0ha9ITvWXqhF%2Bb191Cz9c9Fv96aF8BBU4rw0WGZOUNZrKddpZxtJQx%2Ffz6EllAAhksvmtsv9Sf%2Ba1beFEIz6rqTOwceSC71CEQUKgd5JItSUFHMAbtXJyIB9MBG0van3zGyYl5JtW60ulv3KuPpkAnG8k8RhELLPix8qtp8DW%2BxY1Dapw2rfvETVRa9dPxsi8HYFeaVEBRuUCDQuE522qnKJOZoCj01z0rAArG1q4OyEFGXOrD6WiWuLGW0EuaGmLjxK9fd05tWfn5A7Oa7Y78gQsTQs8AKqyVCjIl8aExUq%2BTjdUDrNi3qBvtb51WM%2BMKXfmka4CCMPwpIlnAgPnoIxe1k1aXZpJgzyRS7ay6kOp7DVzrY49lciBZnMdxYbjlJMyEyyxlCgvtxJudBsI%2BMpcLV6lY520k9G7fDk%2BnPBqEzpMuIND8mT3RGU6y3w9SAbL21bGWaAOfFp1QS8FXVm6SN74UAo4GR1ISxZiLjao3jo7sMfDxyfVDF8n953L9HvS8tltjtlnG4jaJI4tXfiKT7kEU4FlN%2B6jgKqE6yQJ%2FeeUsZiHlBggYBkr1ei%2By4Kyl0kTDOMDaI9LGjJs%2FCkdttTiNI7zDfFGP9MYmDSrKFG7GJyQ3oJ6SeMJ39KcIuq36boE2jHvfUruOOMJL6IQFC6ez8hpjlLTach87aEXA56JEUNMASIc4vLBgz4njE6Z4tX4xMwliujd6CE8wj%2BnZnwY6qQEvi%2FemViSkkfkN8WsJH2nnwk4ZPxSNdiRzyFbMO67BF8z9Jvx7b5IuJ7%2Bi2h4Vdxx3yfxL%2BDQ5ipnbxSEPSyvzh%2BaRf14Lh32ey33oB8dxAgl%2F2Qba68wGYiq4JE%2F%2BuZleD5aECW9UzcfUVaTJ8Nm7JNAlv9ZS%2FSB2jQp%2Fkdc%2BdbfwCMJA4r0poC6k8uSGUpBqOqiWZiY11D3xfxkBzJNF6Xj56PBsTvtY&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230222T204330Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAYZTTEKKESMM3W3WB%2F20230222%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=cd310388a59d6ac0b48d6dc824337d152bc6e61aec0229a0e6ecabea490d8562" -O FAF5_highway_network_assignments.zip

unzip FAF5_highway_network_assignments.zip
rm FAF5_highway_network_assignments.zip


# FAF5 regional database of tonnage and value by origin-destination pair, commodity type, and mode from 2018-2020 (from https://www.bts.gov/faf)
wget "https://faf.ornl.gov/faf5/data/download_files/FAF5.4.1_2018-2020.zip" -O FAF5_regional_od.zip

unzip FAF5_regional_od.zip -d FAF5_regional_flows_origin_destination
rm FAF5_regional_od.zip


# from https://www.bts.gov/faf
wget "https://rosap.ntl.bts.gov/view/dot/42632/dot_42632_DS2.zip" -O VIUS_2002.zip

unzip VIUS_2002.zip -d VIUS_2002
rm VIUS_2002.zip


# from ls
wget "https://opendata.arcgis.com/api/v3/datasets/23e16f24702948ac9e2032bfa0526a8f_1/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O egrid2020_subregions.zip

unzip egrid2020_subregions.zip -d egrid2020_subregions
rm egrid2020_subregions.zip


# from https://www.epa.gov/egrid/download-data
wget "https://www.epa.gov/system/files/documents/2023-01/eGRID2021_data.xlsx"


# from https://hub.arcgis.com/datasets/d6f7ee6129e241cc9b6f75978e47128b
wget "https://opendata.arcgis.com/api/v3/datasets/d6f7ee6129e241cc9b6f75978e47128b_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O zip_code_regions.zip

unzip zip_code_regions.zip -d zip_code_regions
rm zip_code_regions.zip


# from https://www.sciencebase.gov/catalog
wget "https://www.sciencebase.gov/catalog/file/get/52c78623e4b060b9ebca5be5?facet=tl_2012_us_state" -O state_boundaries.zip

unzip state_boundaries.zip -d state_boundaries
rm state_boundaries.zip


# from https://www.eia.gov/electricity/data.php
mkdir -p electricity_rates
wget "https://www.eia.gov/electricity/data/state/sales_annual_a.xlsx" -O electricity_rates/sales_annual_a.xlsx


# from https://catalog.data.gov/dataset/u-s-electric-utility-companies-and-rates-look-up-by-zipcode-2020
mkdir -p electricity_rates
wget "https://data.openei.org/files/5650/iou_zipcodes_2020.csv" -O electricity_rates/iou_zipcodes_2020.csv


# from https://data.nrel.gov/submissions/74
wget "https://data.nrel.gov/system/files/74/Demand%20charge%20rate%20data.xlsm" -O Demand_charge_rate_data.xlsm


# from https://atlas.eia.gov/datasets/f4cd55044b924fed9bc8b64022966097_0
wget "https://opendata.arcgis.com/api/v3/datasets/f4cd55044b924fed9bc8b64022966097_0/downloads/data?format=shp&spatialRefId=4326&where=1%3D1" -O utility_boundaries.zip
unzip utility_boundaries.zip -d utility_boundaries
rm utility_boundaries.zip


# from https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::electric-planning-areas/about
wget "https://opendata.arcgis.com/api/v3/datasets/7d35521e3b2c48ab8048330e14a4d2d1_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O balancing_authority_boundaries.zip
unzip balancing_authority_boundaries.zip -d balancing_authority_boundaries
rm balancing_authority_boundaries.zip


# from https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/US48/US48
mkdir -p power_demand_by_balancing_authority
wget "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jul_Dec.csv" -O power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jul_Dec.csv
wget "https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/EIA930_BALANCE_2022_Jan_Jun.csv" -O power_demand_by_balancing_authority/EIA930_BALANCE_2022_Jan_Jun.csv


# from https://www.eia.gov/electricity/data/state/
wget https://www.eia.gov/electricity/data/state/existcapacity_annual.xlsx