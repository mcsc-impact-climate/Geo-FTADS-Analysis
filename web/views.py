import os
import json

from collections import OrderedDict
from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage, FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from storages.backends.s3boto3 import S3Boto3Storage
from shapely.geometry import shape, mapping
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.linestring import LineString
from shapely.geometry.multilinestring import MultiLineString

INDEX_TEMPLATE = 'local.html' if __package__ == 'web' else 'index_main.html'


# Create an ordered dictionary to maintain the order of items
geojsons = OrderedDict()

geojson_directory = 'geojsons_simplified'

# Total domestic Imports and Exports
geojsons['Truck Imports and Exports'] = os.path.join(geojson_directory, "faf5_freight_flows/mode_truck_commodity_all_origin_all_dest_all.geojson")

# Grid emission intensity
geojsons['Grid Emission Intensity'] = os.path.join(geojson_directory, "grid_emission_intensity/eia2022_state_merged.geojson")

geojsons['Hourly Grid Emissions'] = os.path.join(geojson_directory, "daily_grid_emission_profiles/daily_grid_emission_profile_hour0.geojson")

# Grid capacity and actual energy generated for 2022
geojsons['Grid Generation and Capacity'] = os.path.join(geojson_directory, "gen_cap_2022_state_merged.geojson")

# Commercial electricity price by state
geojsons['Commercial Electricity Price'] = os.path.join(geojson_directory, "electricity_rates_by_state_merged.geojson")

# Maximum demand charges from NREL
geojsons['Maximum Demand Charge (utility-level)'] = os.path.join(geojson_directory, "demand_charges_merged.geojson")

# State-level demand charges from NREL
geojsons['Maximum Demand Charge (state-level)'] = os.path.join(geojson_directory, "demand_charges_by_state.geojson")

# Highway flows
geojsons['Highway Flows (Interstate)'] = os.path.join(geojson_directory, "highway_assignment_links_interstate.geojson")
# geojsons['Highway Flows (SU)'] = os.path.join(geojson_directory, "highway_assignment_links_single_unit.geojson")
# geojsons['Highway Flows (CU)'] = os.path.join(geojson_directory, "highway_assignment_links_combined_unit.geojson")

# Alternative fueling stations along highway corridors
geojsons['Direct Current Fast Chargers'] = os.path.join(geojson_directory, "US_elec.geojson")
geojsons['Hydrogen Stations'] = os.path.join(geojson_directory, "US_hy.geojson")
geojsons['LNG Stations'] = os.path.join(geojson_directory, "US_lng.geojson")
geojsons['CNG Stations'] = os.path.join(geojson_directory, "US_cng.geojson")
geojsons['LPG Stations'] = os.path.join(geojson_directory, "US_lpg.geojson")

# Hydrogen hubs
geojsons['Operational Electrolyzers'] = os.path.join(geojson_directory, "electrolyzer_operational.geojson")
geojsons['Installed Electrolyzers'] = os.path.join(geojson_directory, "electrolyzer_installed.geojson")
geojsons['Planned Electrolyzers'] = os.path.join(geojson_directory, "electrolyzer_planned_under_construction.geojson")
geojsons['Hydrogen from Refineries'] = os.path.join(geojson_directory, "refinery.geojson")

# DOE-funded heavy duty vehicle infrastructure projects
geojsons['East Coast ZEV Corridor'] = os.path.join(geojson_directory, "eastcoast.geojson")
geojsons['Midwest ZEV Corridor'] = os.path.join(geojson_directory, "midwest.geojson")
geojsons['Houston to LA H2 Corridor'] = os.path.join(geojson_directory, "h2la.geojson")
geojsons['I-710 EV Corridor'] = os.path.join(geojson_directory, "la_i710.geojson")
geojsons['Northeast EV Corridor'] = os.path.join(geojson_directory, "northeast.geojson")
geojsons['Bay Area EV Roadmap'] = os.path.join(geojson_directory, "bayarea.geojson")
geojsons['Salt Lake City Region EV Plan'] = os.path.join(geojson_directory, "saltlake.geojson")

# Truck stop parking locations
geojsons['Truck Stop Locations'] = os.path.join(geojson_directory, "Truck_Stop_Parking.geojson")

# Principal ports
geojsons['Principal Ports'] = os.path.join(geojson_directory, "Principal_Port.geojson")

# Regional Incentives
geojsons['State-Level Incentives and Regulations'] = os.path.join(geojson_directory, "incentives_and_regulations/all_incentives_and_regulations.geojson")

# Truck charger layers
geojsons['Truck Stop Charging'] = os.path.join(geojson_directory, "infrastructure_pooling_thought_experiment/Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_200.0_chargingtime_4.0_maxwait_0.5.geojson")

# Estimated lifecycle costs and emissions per mile for Tesla Semi
geojsons['Lifecycle Truck Emissions'] = os.path.join(geojson_directory, "costs_and_emissions/state_emissions_per_mile_payload40000_avVMT100000.geojson")
geojsons['Total Cost of Truck Ownership'] = os.path.join(geojson_directory, "costs_and_emissions/costs_per_mile_payload40000_avVMT100000_maxChP400.geojson")
geojsons['Energy Demand from Electrified Trucking'] = os.path.join(geojson_directory, "trucking_energy_demand.geojson")

def auth_required(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if default_storage.__class__.__name__ != 'FileSystemStorage' and not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse('Unauthorized', content_type="application/json", status=401)
            return redirect('/users/login/')
        return function(request, *args, **kwargs)

    return decorator


@auth_required
def index(request):
    return render(request, INDEX_TEMPLATE)

@auth_required
def get_geojsons(request):
    try:
        json_str = json.dumps(geojsons, sort_keys=False)
        return HttpResponse(json_str, content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse(str(e), content_type="application/json", status=400)


@auth_required
def get_geojson(request, geojson_name=""):
    try:
        geojson_path = geojsons[geojson_name]
        geojson_filename = os.path.splitext(os.path.basename(geojson_path))[0] + '.geojson'
        with default_storage.open(f"/geojsons_simplified/{geojson_filename}", mode='r') as geojson_file:
            geojson_data = json.load(geojson_file)
        return HttpResponse(json.dumps(geojson_data), content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse({"error": str(e)}, content_type="application/json", status=400)
