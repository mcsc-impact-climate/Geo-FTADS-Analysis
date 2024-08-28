#!/usr/bin/env python3

"""
Created on Mon May 10 13:18:00 2023
@author: danikam
"""

# Import needed modules
import pandas as pd
from CommonTools import get_top_dir

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LogNorm

top_dir = get_top_dir()


def readMeta():
    """
    Reads in the metadata file (functionally keys) for the FAF5 data

    Parameters
    ----------
    None

    Returns
    -------
    dest (pd.DataFrame): A pandas dataframe containing (currently) all domestic regions from the FAF5_metadata
    mode (pd.DataFrame): A pandas dataframe containing (currently) all modes of transit used in the FAF5_metadata


    NOTE: None.

    """

    # Read in Meta Data
    metaPath = (
        f"{top_dir}/data/FAF5_regional_flows_origin_destination/FAF5_metadata.xlsx"
    )
    meta = pd.ExcelFile(metaPath)

    # Only include truck rail and water
    mode = pd.read_excel(meta, "Mode")[0:3]
    dest = pd.read_excel(meta, "FAF Zone (Domestic)")
    comms = pd.read_excel(meta, "Commodity (SCTG2)")
    return dest, mode, comms


# Collect origin-specific csv files
dest, mode, comm = readMeta()

tmiles_matrix = pd.DataFrame(
    index=list(dest["Numeric Label"].astype("int")),
    columns=list(dest["Numeric Label"].astype("int")),
)

emission_intensity_matrix = pd.DataFrame(
    index=list(dest["Numeric Label"]), columns=list(dest["Numeric Label"].astype("int"))
)

dict_all = {
    "origin ID": [],
    "origin name": [],
    "destination ID": [],
    "destination name": [],
    "Million tmiles / sqm": [],
    "emissions [tons CO2 / sqm]": [],
}

for origin, origin_name in zip(dest["Numeric Label"], dest["Short Description"]):
    data = pd.read_csv(
        f"{top_dir}/data/Point2Point_outputs/mode_truck_commodity_all_origin_{origin}_dest_all.csv"
    )

    for destination, tmiles_import, e_import in zip(
        data["FAF_Zone"], data["Tmil Imp D"], data["E Imp Den"]
    ):
        destination_name = dest[dest["Numeric Label"] == destination][
            "Short Description"
        ].iloc[0]
        dict_all["origin ID"].append(origin)
        dict_all["origin name"].append(origin_name)
        dict_all["destination ID"].append(destination)
        dict_all["destination name"].append(destination_name)

        if int(origin) == int(destination):
            tmiles_matrix.loc[int(origin), int(destination)] = 0
            emission_intensity_matrix.loc[int(origin), int(destination)] = 0

            dict_all["Million tmiles / sqm"].append(0)
            dict_all["emissions [tons CO2 / sqm]"].append(0)
        else:
            tmiles_matrix.loc[int(origin), int(destination)] = tmiles_import
            emission_intensity_matrix.loc[int(origin), int(destination)] = e_import

            dict_all["Million tmiles / sqm"].append(tmiles_import)
            dict_all["emissions [tons CO2 / sqm]"].append(e_import)


# Arrange rows in order of tmiles / sqm
df_all = pd.DataFrame(dict_all)
df_all = df_all.sort_values(by=["Million tmiles / sqm"], ascending=False)
df_all.to_csv(f"{top_dir}/data/ordered_OD.csv", index=False)

# Plot the matrix of ton-miles transported from/to each origin/destination pair as a heatmap
tmiles_matrix = tmiles_matrix[tmiles_matrix.columns].astype(float)
sns.heatmap(tmiles_matrix, linewidths=0.30, annot=False, norm=LogNorm())
plt.xlabel("FAF5 Region ID of Destination")
plt.ylabel("FAF5 Region ID of Origin")
plt.title("Areal Density of Ton-miles Transported [million ton-miles / mile$^2$]")
plt.tight_layout()

plt.savefig(f"{top_dir}/plots/tmiles_density_OD.pdf")
