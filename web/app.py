from flask import Flask, jsonify, send_from_directory
import json
import os
from collections import OrderedDict
from flask import request

app = Flask(__name__, static_url_path="", static_folder="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


# Serve index.html from the directory one level above the current directory
@app.route("/")
def index():
    return send_from_directory(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../html")),
        "index.html",
    )


@app.route("/style/<path:filename>")
def serve_css(filename):
    return send_from_directory(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../style")), filename
    )


# Serve main.js from the directory one level above the current directory
@app.route("/javascript/<path:filename>")
def serve_js(filename):
    return send_from_directory(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../javascript")),
        filename,
    )


# Create an ordered dictionary to maintain the order of items
geojsons = OrderedDict()

geojson_directory = "geojsons_simplified"

# Total domestic Imports and Exports
geojsons["Truck Imports and Exports"] = os.path.join(
    geojson_directory, "mode_truck_commodity_all_origin_all_dest_all.geojson"
)

# Grid emission intensity
geojsons["Grid Emission Intensity"] = os.path.join(
    geojson_directory, "egrid2020_subregions_merged.geojson"
)

# Commercial electricity price by state
geojsons["Commercial Electricity Price"] = os.path.join(
    geojson_directory, "electricity_rates_by_state_merged.geojson"
)

# Maximum demand charges from NREL
geojsons["Maximum Demand Charge"] = os.path.join(
    geojson_directory, "demand_charges_merged.geojson"
)

# Highway flows
geojsons["Highway Flows (Interstate)"] = os.path.join(
    geojson_directory, "highway_assignment_links_interstate.geojson"
)
# geojsons['Highway Flows (SU)'] = os.path.join(geojson_directory, "highway_assignment_links_single_unit.geojson")
# geojsons['Highway Flows (CU)'] = os.path.join(geojson_directory, "highway_assignment_links_combined_unit.geojson")

# Alternative fueling stations along highway corridors
geojsons["Direct Current Fast Chargers"] = os.path.join(
    geojson_directory, "US_elec.geojson"
)
geojsons["Hydrogen Stations"] = os.path.join(geojson_directory, "US_hy.geojson")
geojsons["LNG Stations"] = os.path.join(geojson_directory, "US_lng.geojson")
geojsons["CNG Stations"] = os.path.join(geojson_directory, "US_cng.geojson")
geojsons["LPG Stations"] = os.path.join(geojson_directory, "US_lpg.geojson")

# Hydrogen hubs
geojsons["Operational Electrolyzers"] = os.path.join(
    geojson_directory, "electrolyzer_operational.geojson"
)
geojsons["Installed Electrolyzers"] = os.path.join(
    geojson_directory, "electrolyzer_installed.geojson"
)
geojsons["Planned Electrolyzers"] = os.path.join(
    geojson_directory, "electrolyzer_planned_under_construction.geojson"
)
geojsons["Hydrogen from Refineries"] = os.path.join(
    geojson_directory, "refinery.geojson"
)

# DOE-funded heavy duty vehicle infrastructure projects
geojsons["East Coast ZEV Corridor"] = os.path.join(
    geojson_directory, "eastcoast.geojson"
)
geojsons["Midwest ZEV Corridor"] = os.path.join(geojson_directory, "midwest.geojson")
geojsons["Houston to LA H2 Corridor"] = os.path.join(geojson_directory, "h2la.geojson")
geojsons["I-710 EV Corridor"] = os.path.join(geojson_directory, "la_i710.geojson")
geojsons["Northeast EV Corridor"] = os.path.join(geojson_directory, "northeast.geojson")
geojsons["Bay Area EV Roadmap"] = os.path.join(geojson_directory, "bayarea.geojson")
geojsons["Salt Lake City Region EV Plan"] = os.path.join(
    geojson_directory, "saltlake.geojson"
)

# Truck stop parking locations
geojsons["Truck Stop Locations"] = os.path.join(
    geojson_directory, "Truck_Stop_Parking.geojson"
)

# Principal ports
geojsons["Principal Ports"] = os.path.join(geojson_directory, "Principal_Port.geojson")

# Regional Incentives
geojsons["State-Level Incentives and Regulations"] = os.path.join(
    geojson_directory, "all_incentives_and_regulations.geojson"
)

# Truck charger layers
geojsons["Truck Stop Charging"] = os.path.join(
    geojson_directory,
    "Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_200.0_chargingtime_4.0_maxwait_0.5.geojson",
)


@app.route("/get_geojsons")
def get_geojsons():
    json_str = json.dumps(geojsons, sort_keys=False)
    return json_str


@app.route("/get_geojson")
def get_geojson():
    # Get the 'geojson_name' and 'str_add' parameters from the query string
    geojson_name = request.args.get("geojson_name", "")
    filename = request.args.get("filename", "")

    geojson_path = geojsons[geojson_name]
    geojson_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../geojsons_simplified")
    )
    if filename == "":
        geojson_filename = os.path.join(
            geojson_directory,
            os.path.splitext(os.path.basename(geojson_path))[0] + ".geojson",
        )
    else:
        geojson_filename = os.path.join(geojson_directory, filename)

    # Create the directory to contain geojsons if it doesn't exist
    if not os.path.exists(geojson_directory):
        os.makedirs(geojson_directory)

    if os.path.exists(geojson_filename):
        # Read and return the existing .geojson file
        with open(geojson_filename, "r") as geojson_file:
            geojson_data = json.load(geojson_file)
            return jsonify(geojson_data)
    else:
        print("geojson file %s does not exist" % geojson_filename)
        return 1


if __name__ == "__main__":
    app.run(debug=True)
