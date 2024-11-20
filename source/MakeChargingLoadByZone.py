#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed May 30 20:31:00 2024

@author: danikam
"""

import numpy as np
import pandas as pd

import geopandas as gpd
from CommonTools import get_top_dir
from scipy.interpolate import UnivariateSpline


import matplotlib.pyplot as plt


def get_ev_load_profile(top_dir, load_profile_path):
    load_profile_df = pd.read_csv(load_profile_path)

    # Sort the DataFrame based on the 'Hours' column
    load_profile_df = load_profile_df.sort_values(by="Hours", ascending=True)

    # Reset the index of the DataFrame after sorting
    load_profile_df = load_profile_df.reset_index(drop=True)

    # Get a spline interpolation
    spline = UnivariateSpline(
        load_profile_df["Hours"], load_profile_df["Power (kW)"], s=500, ext=3
    )
    hours_fine = np.linspace(0, 24, 300)
    power_smooth = spline(hours_fine)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_ylabel("Power (kW)", fontsize=20)
    ax.set_xlabel("Hours", fontsize=20)
    ax.set_title("Original Data from Borlaug et al.", fontsize=24)
    ax.tick_params(axis="both", which="major", labelsize=18)
    ax.plot(load_profile_df["Hours"], load_profile_df["Power (kW)"], "o")
    ax.plot(
        hours_fine, power_smooth, label="Spline Interpolation", color="red", linewidth=2
    )
    plt.savefig(f"{top_dir}/plots/extreme_load_profile.png", dpi=300)

    # Normalize the profile such that its average is 1
    power_smooth = power_smooth / np.average(power_smooth)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_ylabel("Normalize Units", fontsize=20)
    ax.set_xlabel("Hours", fontsize=20)
    ax.set_title("Normalize to Unit Average", fontsize=24)
    ax.tick_params(axis="both", which="major", labelsize=18)
    ax.plot(
        hours_fine, power_smooth, label="Spline Interpolation", color="red", linewidth=2
    )
    plt.savefig(f"{top_dir}/plots/extreme_load_profile_normalized.png", dpi=300)

    # Save the normalized load profile to a file
    load_profile_smooth_df = pd.DataFrame({"Hours": hours_fine, "Power": power_smooth})
    load_profile_smooth_df.to_csv("data/extreme_load_profile_smooth.csv")

    return load_profile_smooth_df


def get_daily_ev_demands(top_dir, ev_load_data_gpd, ev_daily_load_profile_df):
    # Drop the geometry data (we don't care about it anymore)
    ev_load_data_df = ev_load_data_gpd.drop(columns=["geometry"])

    zones = ev_load_data_df["zone"].unique()

    for zone in zones:
        ev_load_data_zone_df = ev_load_data_df[ev_load_data_df["zone"] == zone]
        daily_ev_load_dict = {}
        for center in ev_load_data_zone_df["Nearest Center"]:
            daily_ev_load_dict[center] = (
                float(
                    ev_load_data_zone_df["Av P Dem"][
                        ev_load_data_zone_df["Nearest Center"] == center
                    ].iloc[0]
                )
                * ev_daily_load_profile_df["Power"]
            )

        daily_ev_load_df = pd.DataFrame(daily_ev_load_dict)
        daily_ev_load_df["Hours"] = ev_daily_load_profile_df["Hours"]
        daily_ev_load_df["Total (MW)"] = daily_ev_load_df.sum(axis=1)

        daily_ev_load_df.to_csv(f"{top_dir}/data/daily_ev_load_{zone}.csv", index=False)


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    ev_load_data_gpd = gpd.read_file(f"{top_dir}/data/TT_charger_locations.json")

    ev_daily_load_profile_df = get_ev_load_profile(
        top_dir, f"{top_dir}/data/Borlaug_et_al_most_extreme_HDEV_load_profile.csv"
    )

    get_daily_ev_demands(top_dir, ev_load_data_gpd, ev_daily_load_profile_df)


main()
