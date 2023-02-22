# FAF5_Analysis

## Get the data

### FAF5 Regions

```bash
# FAF5 regions (from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-regions)
wget "https://opendata.arcgis.com/api/v3/datasets/e3bcc5d26e5e42709e2bacd6fc37ab43_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_regions.zip
unzip FAF5_regions.zip -d FAF5_regions
rm FAF5_regions.zip
```

### FAF5 Network Links

```bash
# FAF5 regions (from https://geodata.bts.gov/datasets/usdot::freight-analysis-framework-faf5-network-links)
wget "https://opendata.arcgis.com/api/v3/datasets/cbfd7a1457d749ae865f9212c978c645_0/downloads/data?format=shp&spatialRefId=3857&where=1%3D1" -O FAF5_network_links.zip
unzip FAF5_network_links.zip -d FAF5_network_links
rm FAF5_network_links.zip
```
