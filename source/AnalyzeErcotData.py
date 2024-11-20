#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 15:42:00 2024

@author: danikam
"""

# Import needed modules

import numpy as np
import pandas as pd
from CommonTools import get_top_dir
import matplotlib.pyplot as plt
import glob
import re

zone_mapping = {
    "north": "NORTH",
    "far_west": "FWEST",
    "west": "WEST",
    "north_central": "NCENT",
    "east": "EAST",
    "south_central": "SCENT",
    "south": "SOUTH",
    "coast": "COAST",
}

month_names = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def read_load_data(paths):
    load_data = pd.DataFrame()
    for path in paths:
        data = pd.read_excel(path)
        load_data = pd.concat([load_data, data], ignore_index=True)

    # Remove any 'Hour Ending' rows where time shifts to DST
    load_data = load_data[~load_data["Hour Ending"].str.contains("DST")]

    # Adjust 'Hour Ending' for '24:00'
    load_data["Hour Ending"] = load_data["Hour Ending"].apply(correct_datetime)

    # Convert 'Hour Ending' to datetime
    load_data["Hour Ending"] = pd.to_datetime(
        load_data["Hour Ending"], format="%m/%d/%Y %H:%M"
    )

    return load_data


def correct_datetime(time_str):
    # Check if time is '24:00' and adjust to '00:00' of the next day
    if time_str.endswith("24:00"):
        # Parse the date part and increment the day
        new_time_str = pd.to_datetime(time_str[:-5]).date() + pd.Timedelta(days=1)
        return new_time_str.strftime("%m/%d/%Y") + " 00:00"
    return time_str


def make_daily_ev_demands_fig(top_dir, filename, zone, include_all_centers=True):
    daily_ev_demands = pd.read_csv(filename)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlabel('Hours', fontsize=24)
    ax.set_ylabel('Power (MW)', fontsize=24)
    zone_title = zone.title().replace('_', ' ')
    ax.set_title(f'Power Demands in {zone_title} Zone', fontsize=26)
    ax.tick_params(axis='both', which='major', labelsize=22)
    
    # For each zone, plot the daily variation for each center (and total over all centers)
    colors = ["red", "purple", "orange", "teal", "cyan", "magenta", "teal"]
    i_center = 0
    if include_all_centers:
        centers = daily_ev_demands.columns
    else:
        centers = ["Total (MW)"]
    for center in centers:
        if center == "Hours":
            continue
        elif "(MW)" in center:
            center_label = center.replace(" (MW)", "")
            color = "black"
            linewidth = 3
        else:
            color = colors[i_center]
            linewidth = 2
            center_label = center

        ax.plot(
            daily_ev_demands["Hours"],
            daily_ev_demands[center],
            label=f"EV Demand ({center_label})",
            color=color,
            linewidth=linewidth,
            zorder=20,
        )
        i_center += 1

    ax.axhline(
        np.mean(daily_ev_demands[center]),
        label="Average Total EV Demand",
        color="black",
        linewidth=2,
        linestyle="--",
        zorder=100,
    )

    return fig, ax


def plot_with_historical_daily_load(top_dir, load_data_df, include_all_centers=True):
    pattern = re.compile(r"daily_ev_load_([^\.]+).csv")
    for filename in glob.glob(f"{top_dir}/data/daily_ev_load_*.csv"):
        match = pattern.search(filename)
        if match:
            zone = match.group(1)

        fig, ax = make_daily_ev_demands_fig(top_dir, filename, zone, include_all_centers)

        # Extract the date for filtering
        load_data_df["Date"] = load_data_df["Hour Ending"].dt.date

        # Get unique dates that are the first of the month
        first_days = load_data_df[
            (load_data_df["Hour Ending"].dt.day == 1)
            & (load_data_df["Hour Ending"].dt.year == 2023)
        ]["Date"].unique()

        # Filter data for each first of the month
        cmap = plt.get_cmap("winter")
        num_plots = len(first_days)
        colors = [cmap(i / num_plots) for i in range(num_plots)]
        i_month = 0
        for date in first_days:
            # Filter data for the specific day
            daily_data = load_data_df[load_data_df["Date"] == date]
            if i_month == 0 or i_month == 11:
                ax.plot(
                    daily_data["Hour Ending"].dt.hour,
                    daily_data[zone_mapping[zone]],
                    color=colors[i_month],
                    label=f"Historical Load ({month_names[i_month+1]})",
                    zorder=i_month,
                    alpha=0.8,
                )
            else:
                ax.plot(
                    daily_data["Hour Ending"].dt.hour,
                    daily_data[zone_mapping[zone]],
                    color=colors[i_month],
                    alpha=0.8,
                )
            i_month += 1

        ymin, ymax = ax.get_ylim()

        ax.set_ylim(ymin, ymax*1.5)
        ax.legend(fontsize=20)
        if include_all_centers:
            plt.savefig(f'{top_dir}/plots/daily_ev_load_{zone}_allcenters.png')
        else:
            plt.savefig(f'{top_dir}/plots/daily_ev_load_{zone}.png')

def plot_with_excess_capacity(top_dir, load_data_df, include_all_centers=True):
    pattern = re.compile(r"daily_ev_load_([^\.]+).csv")
    for filename in glob.glob(f"{top_dir}/data/daily_ev_load_*.csv"):
        match = pattern.search(filename)
        if match:
            zone = match.group(1)

        # Extract the date for filtering
        load_data_df["Date"] = pd.to_datetime(load_data_df["Hour Ending"].dt.date)

        # Drop zones we're not interested in
        load_data_zone_df = load_data_df[["Hour Ending", "Date", zone_mapping[zone]]]

        ##### Get the absolute maximum power demand over the full period (approximation of nameplate capacity) #####
        max_load = load_data_zone_df[zone_mapping[zone]].max()

        # Extract the hour and month components
        load_data_zone_df["Hour"] = load_data_zone_df["Hour Ending"].dt.hour
        load_data_zone_df["Month"] = load_data_zone_df["Date"].dt.month

        for month in range(1, 13):
            # Group by the 'Hour' column
            grouped = load_data_zone_df[load_data_zone_df["Month"] == month].groupby(
                "Hour"
            )

            # Aggregate the data to get mean, max, min, and std dev
            aggregated_data_df = grouped[zone_mapping[zone]].agg(
                ["mean", "max", "min", "std"]
            )

            # Calculate the mean (+/-std), max and min excess based on the maximum load over the month
            aggregated_data_df["Max Load (MW)"] = load_data_zone_df[
                load_data_zone_df["Month"] == month
            ][zone_mapping[zone]].max()
            aggregated_data_df["Mean Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["mean"]
            )
            aggregated_data_df["Mean Excess (Month) + std (MW)"] = (
                aggregated_data_df["Max Load (MW)"]
                - aggregated_data_df["mean"]
                + aggregated_data_df["std"]
            )
            aggregated_data_df["Mean Excess (Month) - std (MW)"] = (
                aggregated_data_df["Max Load (MW)"]
                - aggregated_data_df["mean"]
                - aggregated_data_df["std"]
            )
            aggregated_data_df["Max Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["min"]
            )
            aggregated_data_df["Min Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["max"]
            )

            # Calculate the mean (+/-std), max and min excess based on the maximum load over the year
            aggregated_data_df["Mean Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["mean"]
            )
            aggregated_data_df["Mean Excess (Year) + std (MW)"] = (
                max_load - aggregated_data_df["mean"] + aggregated_data_df["std"]
            )
            aggregated_data_df["Mean Excess (Year) - std (MW)"] = (
                max_load - aggregated_data_df["mean"] - aggregated_data_df["std"]
            )
            aggregated_data_df["Max Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["min"]
            )
            aggregated_data_df["Min Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["max"]
            )

            # Reset the index to make 'Hour' a regular column
            aggregated_data_df.reset_index(inplace=True)

            aggregated_data_df = aggregated_data_df.drop(
                ["mean", "max", "min", "std"], axis=1
            )

            # Plot excess relative to monthly max, along with the EV demand curves
            fig, ax = make_daily_ev_demands_fig(top_dir, filename, zone, include_all_centers)

            ax.axhline(
                aggregated_data_df["Max Load (MW)"].iloc[0],
                label="Max Historical Load for Month",
                color="blue",
                linewidth=2,
                linestyle="--",
                zorder=100,
            )

            handles, labels = ax.get_legend_handles_labels()

            (mean_line,) = ax.plot(
                aggregated_data_df["Mean Excess (Month) (MW)"],
                linewidth=3,
                color="navy",
            )
            std_patch = ax.fill_between(
                aggregated_data_df["Hour"],
                aggregated_data_df["Mean Excess (Month) - std (MW)"],
                aggregated_data_df["Mean Excess (Month) + std (MW)"],
                color="blue",
                alpha=0.4,
            )
            extrema_patch = ax.fill_between(
                aggregated_data_df["Hour"],
                aggregated_data_df["Min Excess (Month) (MW)"],
                aggregated_data_df["Max Excess (Month) (MW)"],
                color="blue",
                alpha=0.2,
            )

            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin, ymax * 1.5)
            month_label = month_names[month]
            zone_title = zone.title().replace("_", " ")
            ax.set_title(f"{zone_title}: {month_label}", fontsize=24)

            handles = handles + [(mean_line, std_patch), extrema_patch]
            labels = labels + [
                "Mean Excess (Month) + Stdev (MW)",
                "Min/Max Excess (MW)",
            ]

            ax.legend(handles, labels, fontsize=16, ncol=2)
            if include_all_centers:
                plt.savefig(
                    f"{top_dir}/plots/daily_ev_load_with_excess_{zone}_{month_label}_monthMax_allcenters.png"
                )
            else:
                plt.savefig(
                    f"{top_dir}/plots/daily_ev_load_with_excess_{zone}_{month_label}_monthMax.png"
                )
            plt.close()

            # Plot excess relative to yearly max, along with the EV demand curves
            fig, ax = make_daily_ev_demands_fig(top_dir, filename, zone, include_all_centers)

#            ax.axhline(
#                max_load,
#                label="Max Historical Load for Year",
#                color="blue",
#                linewidth=2,
#                linestyle="--",
#                zorder=100,
#            )

            handles, labels = ax.get_legend_handles_labels()

            (mean_line,) = ax.plot(
                aggregated_data_df["Mean Excess (Year) (MW)"], linewidth=3, color="navy"
            )
            std_patch = ax.fill_between(
                aggregated_data_df["Hour"],
                aggregated_data_df["Mean Excess (Year) - std (MW)"],
                aggregated_data_df["Mean Excess (Year) + std (MW)"],
                color="blue",
                alpha=0.4,
            )
            extrema_patch = ax.fill_between(
                aggregated_data_df["Hour"],
                aggregated_data_df["Min Excess (Year) (MW)"],
                aggregated_data_df["Max Excess (Year) (MW)"],
                color="blue",
                alpha=0.2,
            )

            ymin, ymax = ax.get_ylim()
            ax.set_ylim(ymin, ymax * 1.5)
            month_label = month_names[month]
            zone_title = zone.title().replace("_", " ")
            ax.set_title(f"{zone_title}: {month_label}", fontsize=24)

            handles = handles + [(mean_line, std_patch), extrema_patch]
            labels = labels + ["Mean Excess + Stdev (MW)", "Min/Max Excess (MW)"]

            ax.legend(handles, labels, fontsize=16, ncol=2)

            if include_all_centers:
                plt.savefig(
                    f"{top_dir}/plots/daily_ev_load_with_excess_{zone}_{month_label}_yearMax_allcenters.png"
                )
            else:
                plt.savefig(
                    f"{top_dir}/plots/daily_ev_load_with_excess_{zone}_{month_label}_yearMax.png"
                )
            plt.close()


def plot_coast_load(top_dir, load_data_df):
    aggregated_data_dicts = {}
    for zone in zone_mapping:
        # Extract the date for filtering
        load_data_df["Date"] = pd.to_datetime(load_data_df["Hour Ending"].dt.date)

        # Drop zones we're not interested in
        load_data_zone_df = load_data_df[["Hour Ending", "Date", zone_mapping[zone]]]

        ##### Get the absolute maximum power demand over the full period (approximation of nameplate capacity) #####
        max_load = load_data_zone_df[zone_mapping[zone]].max()

        # Extract the hour and month components
        load_data_zone_df = load_data_zone_df.copy()
        load_data_zone_df.loc[:, "Hour"] = load_data_zone_df.loc[
            :, "Hour Ending"
        ].dt.hour
        load_data_zone_df = load_data_zone_df.copy()
        load_data_zone_df.loc[:, "Month"] = load_data_zone_df.loc[:, "Date"].dt.month

        aggregated_data_dicts[zone] = {}

        for month in range(1, 13):
            # Group by the 'Hour' column
            grouped = load_data_zone_df[load_data_zone_df["Month"] == month].groupby(
                "Hour"
            )

            # Aggregate the data to get mean, max, min, and std dev
            aggregated_data_df = grouped[zone_mapping[zone]].agg(
                ["mean", "max", "min", "std"]
            )
            aggregated_data_dicts[zone][month] = aggregated_data_df

            # Calculate the mean (+/-std), max and min excess based on the maximum load over the month
            aggregated_data_df["Max Load (MW)"] = load_data_zone_df[
                load_data_zone_df["Month"] == month
            ][zone_mapping[zone]].max()
            aggregated_data_df["Mean Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["mean"]
            )
            aggregated_data_df["Mean Excess (Month) + std (MW)"] = (
                aggregated_data_df["Max Load (MW)"]
                - aggregated_data_df["mean"]
                + aggregated_data_df["std"]
            )
            aggregated_data_df["Mean Excess (Month) - std (MW)"] = (
                aggregated_data_df["Max Load (MW)"]
                - aggregated_data_df["mean"]
                - aggregated_data_df["std"]
            )
            aggregated_data_df["Max Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["min"]
            )
            aggregated_data_df["Min Excess (Month) (MW)"] = (
                aggregated_data_df["Max Load (MW)"] - aggregated_data_df["max"]
            )

            # Calculate the mean (+/-std), max and min excess based on the maximum load over the year
            aggregated_data_df["Mean Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["mean"]
            )
            aggregated_data_df["Mean Excess (Year) + std (MW)"] = (
                max_load - aggregated_data_df["mean"] + aggregated_data_df["std"]
            )
            aggregated_data_df["Mean Excess (Year) - std (MW)"] = (
                max_load - aggregated_data_df["mean"] - aggregated_data_df["std"]
            )
            aggregated_data_df["Max Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["min"]
            )
            aggregated_data_df["Min Excess (Year) (MW)"] = (
                max_load - aggregated_data_df["max"]
            )

            # Reset the index to make 'Hour' a regular column
            aggregated_data_df.reset_index(inplace=True)

            aggregated_data_df = aggregated_data_df.drop(
                ["mean", "max", "min", "std"], axis=1
            )

    for month in range(1, 13):
        # Plot excess in coast zone relative to monthly max, overlaid with the other zones for comparison
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.set_xlabel("Hours", fontsize=20)
        ax.set_ylabel("Power (MW)", fontsize=20)
        zone_title = zone.title().replace("_", " ")
        ax.set_title(f"Power Demands in {zone_title} Zone", fontsize=24)
        ax.tick_params(axis="both", which="major", labelsize=18)

        ax.axhline(
            max_load,
            label="Max Historical Load for Month",
            color="blue",
            linewidth=2,
            linestyle="--",
            zorder=100,
        )

        handles, labels = ax.get_legend_handles_labels()

        (mean_line,) = ax.plot(
            aggregated_data_dicts["coast"][month]["Mean Excess (Month) (MW)"],
            linewidth=3,
            color="navy",
        )
        std_patch = ax.fill_between(
            aggregated_data_dicts["coast"][month]["Hour"],
            aggregated_data_dicts["coast"][month]["Mean Excess (Month) - std (MW)"],
            aggregated_data_dicts["coast"][month]["Mean Excess (Month) + std (MW)"],
            color="blue",
            alpha=0.4,
        )
        extrema_patch = ax.fill_between(
            aggregated_data_dicts["coast"][month]["Hour"],
            aggregated_data_dicts["coast"][month]["Min Excess (Month) (MW)"],
            aggregated_data_dicts["coast"][month]["Max Excess (Month) (MW)"],
            color="blue",
            alpha=0.2,
        )

        # colors=['red', 'magenta', 'orange', 'golden rod', 'chartreuse', 'bright violet', 'crimson']
        for zone in zone_mapping:
            if zone == "coast":
                continue
            (mean_line_others,) = ax.plot(
                aggregated_data_dicts[zone][month]["Mean Excess (Month) (MW)"],
                linewidth=2,
                linestyle="--",
                color="red",
            )

        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax * 1.5)
        month_label = month_names[month]
        zone_title = zone.title().replace("_", " ")
        ax.set_title(f"{zone_title}: {month_label}", fontsize=24)

        handles = handles + [(mean_line, std_patch), extrema_patch, mean_line_others]
        labels = labels + [
            "Mean Excess + Stdev (MW)",
            "Min/Max Excess (MW)",
            "Other Zones",
        ]

        ax.legend(handles, labels, fontsize=16, ncol=2)

        plt.savefig(
            f"{top_dir}/plots/daily_ev_load_with_excess_coast_{month_label}_monthMax.png"
        )
        plt.close()

        # Plot excess in coast zone relative to yearly max, overlaid with the other zones for comparison
        fig, ax = plt.subplots(figsize=(11, 8))
        ax.set_xlabel("Hours", fontsize=20)
        ax.set_ylabel("Power (MW)", fontsize=20)
        zone_title = zone.title().replace("_", " ")
        ax.set_title(f"Power Demands in {zone_title} Zone", fontsize=24)
        ax.tick_params(axis="both", which="major", labelsize=18)

        ax.axhline(
            max_load,
            label="Max Historical Load for Year",
            color="blue",
            linewidth=2,
            linestyle="--",
            zorder=100,
        )

        handles, labels = ax.get_legend_handles_labels()

        (mean_line,) = ax.plot(
            aggregated_data_dicts["coast"][month]["Mean Excess (Year) (MW)"],
            linewidth=3,
            color="navy",
        )
        std_patch = ax.fill_between(
            aggregated_data_dicts["coast"][month]["Hour"],
            aggregated_data_dicts["coast"][month]["Mean Excess (Year) - std (MW)"],
            aggregated_data_dicts["coast"][month]["Mean Excess (Year) + std (MW)"],
            color="blue",
            alpha=0.4,
        )
        extrema_patch = ax.fill_between(
            aggregated_data_dicts["coast"][month]["Hour"],
            aggregated_data_dicts["coast"][month]["Min Excess (Year) (MW)"],
            aggregated_data_dicts["coast"][month]["Max Excess (Year) (MW)"],
            color="blue",
            alpha=0.2,
        )

        # colors=['red', 'magenta', 'orange', 'golden rod', 'chartreuse', 'bright violet', 'crimson']
        for zone in zone_mapping:
            if zone == "coast":
                continue
            (mean_line_others,) = ax.plot(
                aggregated_data_dicts[zone][month]["Mean Excess (Year) (MW)"],
                linewidth=2,
                linestyle="--",
                color="red",
            )

        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, ymax * 1.5)
        month_label = month_names[month]
        zone_title = zone.title().replace("_", " ")
        ax.set_title(f"{zone_title}: {month_label}", fontsize=24)

        handles = handles + [(mean_line, std_patch), extrema_patch, mean_line_others]
        labels = labels + [
            "Mean Excess + Stdev (MW)",
            "Min/Max Excess (MW)",
            "Other Zones",
        ]

        ax.legend(handles, labels, fontsize=16, ncol=2)

        plt.savefig(
            f"{top_dir}/plots/daily_ev_load_with_excess_coast_{month_label}_yearMax.png"
        )
        plt.close()


def main():
    # Get the path to the top level of the Git repo
    top_dir = get_top_dir()

    load_data_paths = [
        f"{top_dir}/data/Native_Load_2023/Native_Load_2023.xlsx",
        f"{top_dir}/data/Native_Load_2024/Native_Load_2024.xlsx",
    ]
    load_data_df = read_load_data(load_data_paths)
        
    plot_with_historical_daily_load(top_dir, load_data_df)
    plot_with_historical_daily_load(top_dir, load_data_df, include_all_centers=False)

    plot_with_excess_capacity(top_dir, load_data_df)
    plot_with_excess_capacity(top_dir, load_data_df, include_all_centers=False)
    #plot_coast_load(top_dir, load_data_df)

main()
