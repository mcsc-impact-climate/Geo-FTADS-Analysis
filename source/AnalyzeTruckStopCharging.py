import geopandas as gpd
from shapely.ops import nearest_points
from CommonTools import get_top_dir, saveShapefile
import multiprocessing
from geopy.distance import great_circle
import concurrent.futures
import scipy.special
from scipy.integrate import quad
import numpy as np
from scipy.stats import norm
import time
from functools import lru_cache
import logging
import random
import pandas as pd
from shapely.geometry import Point
import argparse

# Define the process_truck_stop_wrapper function outside of other functions
def process_truck_stop_wrapper(row, highways_gdf, attribute_name, distance_threshold):
    idx, truck_stop = row
    process_truck_stop(truck_stop, highways_gdf, attribute_name, distance_threshold)

def filter_points_by_distance(points_gdf, highways_gdf, distance_threshold):
    '''
    Removes points that lie more than the given distance threshold away from a highway.

    Parameters
    ----------
    points_gdf (gpd.DataFrame): Geopandas dataframe containing the points of interest
    highways_gdf (gpd.DataFrame): Geopandas dataframe containing the highways
    distance_threshold (float): Maximum distance (in meters) that a point can be from a highway, beyond which it gets removed

    Returns
    -------
    filtered_points_gdf (gpd.DataFrame): Points of interest, with points more than the distance threshold from a highway removed

    NOTE: None
    '''
    # Buffer the highways by the given threshold to create a buffer around them
    buffered_highways = highways_gdf.buffer(distance_threshold)

    # Create a GeoDataFrame of the buffered highways
    buffered_highways_gdf = gpd.GeoDataFrame(geometry=buffered_highways, crs=highways_gdf.crs)

    # Iterate over each point
    filtered_points = []
    for idx, point in points_gdf.iterrows():
        # Check if the truck stop is within 100 meters of any buffered highway
        if buffered_highways_gdf.intersects(point['geometry']).any():
            filtered_points.append(point)

    # Create a GeoDataFrame from the filtered truck stops
    filtered_points_gdf = gpd.GeoDataFrame(filtered_points, crs=points_gdf.crs)

    return filtered_points_gdf


def select_truck_stops(gdf, min_distance=80500, target_avg_distance=160934):
    """
    Randomly select truck stops from the geodataframe.
    Parameters:
        - gdf: input geodataframe
        - min_distance: minimum distance between truck stops in meters (default is 50 miles)
        - target_avg_distance: target average distance between truck stops in meters (default is 100 miles)
    Returns:
        - selected_gdf: geodataframe of selected truck stops
    """

    # Start with an empty list to store selected stops
    selected_stops = []

    # Randomly shuffle the geodataframe
    gdf = gdf.sample(frac=1).reset_index(drop=True)

    for i, row in gdf.iterrows():
        if not selected_stops:
            # Select the first point randomly
            selected_stops.append(row)
            continue

        # Calculate distances from the current point to all selected points
        distances = np.array([row['geometry'].distance(stop['geometry']) for stop in selected_stops])

        # Check if the current point satisfies the minimum distance condition
        if np.all(distances >= min_distance):
            # Calculate what the new average distance would be if this point is added
            new_avg_distance = np.mean(distances)

            # Only add this point if it would bring the average distance closer to the target
            if abs(new_avg_distance - target_avg_distance) <= abs(np.mean(distances) - target_avg_distance):
                selected_stops.append(row)

    # Convert the list of selected stops back to a geodataframe
    selected_gdf = gpd.GeoDataFrame(selected_stops, columns=gdf.columns).set_crs("EPSG:3857")

    return selected_gdf


def find_nearest_highway_attribute(truck_stop_point, highways_gdf, attribute_name):
    nearest_distance = float('inf')  # Initialize with a large value
    nearest_highway_attribute = None

    for idx, highway in highways_gdf.iterrows():
        # Find the nearest point on this highway to the truck stop
        nearest_point_on_highway = nearest_points(truck_stop_point, highway['geometry'])[0]

        # Calculate the distance between the truck stop and the nearest point on the highway
        distance_to_highway = truck_stop_point.distance(nearest_point_on_highway)

        # Check if this highway is closer than the previously found one
        if distance_to_highway < nearest_distance:
            nearest_distance = distance_to_highway
            nearest_highway_attribute = highway[attribute_name]

    return nearest_highway_attribute

def add_trips_per_day(truck_stops_gdf, highways_gdf, attribute_name, distance_threshold):
    print("Starting add_trips_per_day_serial function")

    for truck_stop_index, truck_stop in truck_stops_gdf.iterrows():
        try:
            print(f"Processing truck stop: {truck_stop.name}")
            nearby_highways_gdf = highways_gdf[highways_gdf.distance(truck_stop['geometry']) <= distance_threshold]

            if not nearby_highways_gdf.empty:
                nearest_highway_attribute = find_nearest_highway_attribute(truck_stop['geometry'], nearby_highways_gdf,
                                                                           attribute_name)
                if nearest_highway_attribute is not None:
                    truck_stops_gdf.at[truck_stop_index, attribute_name] = nearest_highway_attribute

            else:
                print(f"No nearby highways for truck stop: {truck_stop.name}")

        except Exception as e:
            print(f"Exception occurred: {e}")

    return truck_stops_gdf

def count_truck_stops_within_radius(truck_stops_gdf, radius_miles):
    """
    Count the number of other truck stops within the specified radius (in miles) of each truck stop using spatial indexing.

    Parameters:
    - truck_stops_gdf (gpd.GeoDataFrame): GeoDataFrame containing truck stop locations in EPSG:3857.
    - radius_miles (float): Radius in miles within which to count other truck stops.

    Returns:
    - gpd.GeoDataFrame: GeoDataFrame with an additional 'N_in_200mi' attribute.
    """
    # Convert radius from miles to meters
    radius_miles = 200
    radius_meters = radius_miles * 1609.34  # 1 mile = 1609.34 meters

    # Create a spatial index for the truck stops GeoDataFrame
    truck_stops_gdf.sindex

    # Create an empty list to store the counts
    counts = []

    # Iterate over each truck stop
    n_stops = len(truck_stops_gdf)
    for idx, truck_stop in truck_stops_gdf.iterrows():
        if idx % 100 == 0:
            print('Processed %d of %d stops' % (idx, n_stops))

        # Create a Point geometry for the current truck stop
        current_point = truck_stop['geometry']

        # Use spatial indexing to find candidate truck stops within the bounding box of the radius
        possible_neighbors = list(truck_stops_gdf.sindex.intersection(current_point.buffer(radius_meters).bounds))

        # Initialize a count for truck stops within the radius
        count_within_radius = 0

        # Iterate over potential neighbors and check if they are within the radius
        for neighbor_idx in possible_neighbors:
            if idx != neighbor_idx:  # Skip the current truck stop
                neighbor_point = truck_stops_gdf.loc[neighbor_idx, 'geometry']

                # Calculate the great-circle distance in meters between the two truck stops
                distance = current_point.distance(neighbor_point)

                # Check if the distance is within the specified radius
                if distance <= radius_meters:
                    count_within_radius += 1

        # Append the count to the list
        counts.append(count_within_radius)

    # Create a new GeoDataFrame with the 'N_in_200mi' attribute
    truck_stops_with_counts_gdf = truck_stops_gdf.copy()
    truck_stops_with_counts_gdf['N_in_200mi'] = counts

    return truck_stops_with_counts_gdf

def count_truck_stops_within_radius_parallel(truck_stops_gdf, radius_miles, num_processes):
    """
    Count the number of other truck stops within the specified radius (in miles) of each truck stop using parallel processing.

    Parameters:
    - truck_stops_gdf (gpd.GeoDataFrame): GeoDataFrame containing truck stop locations.
    - radius_miles (float): Radius in miles within which to count other truck stops.
    - num_processes (int): Number of processes to use for parallelization.

    Returns:
    - gpd.GeoDataFrame: GeoDataFrame with an additional 'N_in_200mi' attribute.
    """
    # Ensure the GeoDataFrame is in EPSG:4326 (WGS 84)
    truck_stops_gdf = truck_stops_gdf.to_crs("EPSG:4326")

    # Create a copy of the GeoDataFrame to avoid potential issues with indexing
    truck_stops_gdf = truck_stops_gdf.copy()

    # Initialize a ProcessPoolExecutor with the specified number of processes
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Create a list to store future objects for each truck stop
        futures = []

        # Iterate over each truck stop and submit it for processing
        for idx, truck_stop in truck_stops_gdf.iterrows():
            future = executor.submit(process_truck_stop, truck_stop, truck_stops_gdf, radius_miles)
            futures.append(future)

        # Wait for all futures to complete and retrieve the results
        concurrent.futures.wait(futures)

        # Extract the results from the completed futures
        counts = [future.result() for future in futures]

    # Create a new GeoDataFrame with the 'N_in_200mi' attribute
    truck_stops_with_counts_gdf = truck_stops_gdf.copy()
    truck_stops_with_counts_gdf['N_in_200mi'] = counts
    print(truck_stops_with_counts_gdf)

    return truck_stops_with_counts_gdf.to_crs("EPSG:3857")

def process_truck_stop(truck_stop, truck_stops_gdf, radius_miles):
    """
    Process a single truck stop to count the number of other truck stops within the specified radius.

    Parameters:
    - truck_stop (Series): A single row (truck stop) from the GeoDataFrame.
    - truck_stops_gdf (gpd.GeoDataFrame): GeoDataFrame containing all truck stops.
    - radius_miles (float): Radius in miles within which to count other truck stops.

    Returns:
    - int: The count of other truck stops within the radius.
    """
    current_point = truck_stop['geometry']

    # Use spatial indexing to find candidate truck stops within the bounding box of the radius
    possible_neighbors = list(truck_stops_gdf.sindex.intersection(current_point.buffer(radius_miles).bounds))

    # Initialize a count for truck stops within the radius
    count_within_radius = 0

    # Iterate over potential neighbors and check if they are within the radius
    for neighbor_idx in possible_neighbors:
        if truck_stop.name != neighbor_idx:  # Skip the current truck stop
            neighbor_point = truck_stops_gdf.loc[neighbor_idx, 'geometry']

            # Calculate the great-circle distance in miles between the two truck stops
            distance = great_circle(
                (current_point.y, current_point.x),
                (neighbor_point.y, neighbor_point.x)
            ).miles

            # Check if the distance is within the specified radius
            if distance <= radius_miles:
                count_within_radius += 1

    return count_within_radius
@lru_cache(maxsize=None)
def calculate_charges_per_day(trucks_per_day, n_stops_in_range, range_miles):
    """
    Calculates the average number of trucks expected to arrive at a station each day to charge

    Parameters:
    trucks_per_day (float): Average number of trucks stopping to charge per day
    n_stops_in_range (float): Number of other truck stops within EV truck driving range (200 miles by default)

    Returns:
    charges_per_day (float): Average number of truck charges at the station per day
    """
    #charges_per_day = trucks_per_day / 2.#/ (1+n_stops_in_range)
    charges_per_day = trucks_per_day * 100. / range_miles

    return charges_per_day

@lru_cache(maxsize=None)
def p_x_trucks_at_stop(charges_per_day, x_trucks, charging_time=0.5):
    """
    Calculates the binomial probability of there being x_trucks other trucks charging at the stop when a given truck arrives

    Parameters
    ----------
    charges_per_day (float): Average number of truck charges at the station per day
    x_trucks (float): Number of trucks already at the station when a truck arrives
    charging_time (float): Average amount of time needed for each truck to charge (in hours)

    Returns
    -------
    p_x_at_stop (float): Binomial probability
    """
    # Probability that any given truck is charging at the stop is just given by the ratio of charging time to the number of hours (24) in a day
    p_given_truck_at_stop = charging_time / 24.

    # Convert charges per day to an integer
    charges_per_day = int(charges_per_day)

    # If np>5 and n(1-p)>5, use the gaussian approximation of the binomial distribution
    if charges_per_day * p_given_truck_at_stop > 5 and charges_per_day * (1 - p_given_truck_at_stop) > 5:
        # Calculate mean (μ) and standard deviation (σ) of the binomial distribution
        mean = charges_per_day * p_given_truck_at_stop
        std_dev = np.sqrt(charges_per_day * p_given_truck_at_stop * (1 - p_given_truck_at_stop))

        # Calculate the Gaussian approximation using norm.pdf
        gaussian_appx = norm.pdf(x_trucks, loc=mean, scale=std_dev)

        p_x_at_stop = gaussian_appx
    else:
        p_x_at_stop = scipy.special.binom(charges_per_day - 1, x_trucks) * p_given_truck_at_stop ** x_trucks * (1.-p_given_truck_at_stop) ** (charges_per_day - 1 - x_trucks)

    return p_x_at_stop

@lru_cache(maxsize=None)
def p_waiting_for_charger(t, n_chargers, charging_time):
    """
    Calculates the probability that a truck is still waiting for a charger after time t, if there are n_chargers chargers and all chargers are in use when the truck arrives

    Parameters
    ----------
    t (float): Time elapsed since the truck started waiting for a charger with all chargers occupied and no queue in front of it
    charging_time (float): Time it takes for the truck to charge (in hours)
    n_chargers (int): Number of chargers at the truck stop

    Returns
    -------
    p_waiting_for_charger (float): Probability that the truck is still waiting for a charger after time t

    """
    return (1 - t / charging_time) ** n_chargers

@lru_cache(maxsize=None)
def mu_queue_lt_chargers(trucks_queued, n_chargers, charging_time=0.5):
    """
    Calculates the average time that a truck at the back of a queue spends waiting for a charger to free up, assuming that the length of the queue is smaller than the number of chargers

    Parameters
    ----------
    trucks_queued (float): Trucks queued in front of the truck we're interested in
    n_chargers (int): Number of chargers at the truck stop
    charging_time (float): Average amount of time needed for each truck to charge (in hours)

    Returns
    -------
    mu_queue (float): Average time the truck spends waiting for a charger to free up
    """

    # Define the probability of waiting for a charger to integrate over, for the given values of n_chargers and charging_time
    def this_p_waiting_for_charger(t):
        return p_waiting_for_charger(t, n_chargers, charging_time)

    # Integrate over the probability from 0 to the full charging time to evaluate the average time spent mu_0 waiting for a charger for the first truck in the queue
    mu_0, res = quad(this_p_waiting_for_charger, 0, charging_time)
    mu_last = mu_0      # Update the time that the truck at the front of the queue waited to start charging
    mu_queue = mu_0     # Update the total time the truck of interest has spent waiting in the queue to mu_0

    # Go through all subsequent trucks in the queue and evaluate the average length of time they wait for a charger
    for i in range(1, trucks_queued + 1):
        # The ith truck in the queue is now waiting for n_chargers-i chargers, i of the chargers are in use by the trucks that were queued in front of it
        def this_p_waiting_for_charger(t):
            return p_waiting_for_charger(t, n_chargers-i, charging_time)

        # Now we integrate starting from when the last truck started charging (mu_last) to the total charging time to get the average that the truck now at the start of the queue waits to start charging
        mu_front_of_queue, res = quad(this_p_waiting_for_charger, mu_last, charging_time)
        mu_last = mu_front_of_queue                 # Update the time that the truck at the front of the queue waited to start charging
        mu_queue = mu_last + mu_front_of_queue      # Update the total time the truck of interest has spent waiting in the queue by mu_last
    return mu_queue

@lru_cache(maxsize=None)
def mu_queue(trucks_queued, n_chargers, charging_time=0.5):
    """
    General function to calculate the average time that a truck at the back of a queue spends waiting for a charger to free up, handling both the cases where the queue is smaller than and equal to the number of chargers

    Parameters
    ----------
    trucks_queued (float): Trucks queued in front of the truck we're interested in
    n_chargers (int): Number of chargers at the truck stop
    charging_time (float): Average amount of time needed for each truck to charge (in hours)

    Returns
    -------
    mu_queue (float): Average time the truck spends waiting for a charger to free up
    """

    # If the number of trucks queued is less than the number of chargers, we can just evaluate the average wait time using mu_queue_lt_chargers
    if trucks_queued < n_chargers:
        return mu_queue_lt_chargers(trucks_queued, n_chargers, charging_time)

    # If the number of trucks queued is equal to or greater than the number of chargers, we know we'll need to wait the full charging time for each set F of n_chargers trucks in the queue. For the remaining trucks R, we can evaluate the average wait time using mu_queue_lt_chargers
    else:
        F = np.floor(trucks_queued / n_chargers)
        R = int(trucks_queued - F * n_chargers)
        return mu_queue_lt_chargers(R, n_chargers, charging_time) + charging_time * F

@lru_cache(maxsize=None)
def average_wait_time(charges_per_day, n_chargers, charging_time=0.5):
    """
    Calculates the average time that a truck will spend waiting for a charger at a given truck stop

    Parameters
    ----------
    charges_per_day (float): Average number of truck charges at the station per day
    charging_time (float): Average amount of time needed for each truck to charge (in hours)

    Returns
    -------
    mu_queue (float): Average time the truck spends waiting for a charger to free up
    """
    x_trucks_arr = np.arange(n_chargers, charges_per_day)
    p_x_values = np.array([p_x_trucks_at_stop(charges_per_day, x, charging_time) for x in x_trucks_arr])
    mu_values = np.array([mu_queue(int(x - n_chargers), n_chargers, charging_time) for x in x_trucks_arr])
    av_t_wait = np.sum(p_x_values * mu_values)
    return av_t_wait

def get_min_chargers(trucks_per_day, n_stops_in_range, range_miles=200., charging_time=4., max_wait_time=1.):
    """
    Calculates the minimum number of chargers and charger-to-truck ratio (where the trucks in the ratio is the number of trucks stopping at the station to charge per day)

    Parameters
    ----------
    trucks_per_day (float): Average number of trucks stopping to charge per day
    n_stops_in_range (float): Number of other truck stops within EV truck driving range (200 miles by default)
    charging_time (float): Average amount of time needed for each truck to charge (in hours)

    Returns
    -------
    min_chargers (int): Minumum number of chargers needed to keep the average wait time below the given value
    min_ratio (float): Minimum charger-to-truck ratio needed
    """

    # Calculate the average number of trucks that will need to stop and charge at the truck stop per day
    charges_per_day = int(calculate_charges_per_day(trucks_per_day, n_stops_in_range, range_miles))

    if charges_per_day == 0:
        charges_per_day = 1

    # Make an array of possible numbers of chargers, ranging from one to the number of trucks charging per day
    n_chargers_arr = np.arange(1, charges_per_day)

    # Initialize the minimum number of chargers to the number of charges per day
    min_chargers = charges_per_day
    for n_chargers in n_chargers_arr:
        av_wait = average_wait_time(charges_per_day, n_chargers, charging_time)
        if av_wait < max_wait_time:
            min_chargers = n_chargers
            break

    min_ratio = 1.*min_chargers / (1.*charges_per_day)

    return min_chargers, min_ratio, charges_per_day

def apply_min_chargers(truck_stops_gdf, range_miles, charging_time=4., max_wait_time=1.):
    """
    Apply the get_min_chargers function to each truck stop in the GeoDataFrame and add the results as attributes.

    Parameters:
    - truck_stops_gdf (gpd.GeoDataFrame): GeoDataFrame containing truck stop locations with 'Tot Trips' and 'N_in_200mi' attributes.

    Returns:
    - gpd.GeoDataFrame: GeoDataFrame with additional 'Min Chargers' and 'Charger-to-Truck Ratio' attributes.
    """
    # Initialize empty lists to store the results
    min_chargers_list = []
    charger_to_truck_ratio_list = []
    CPD_list = []

    # Iterate over each truck stop
    n_stops = len(truck_stops_gdf)
    for idx, truck_stop in truck_stops_gdf.iterrows():
        print('Processing stop %d of %d'%(idx, n_stops))
#        if idx > 1:
#            min_chargers_list.append(0)
#            charger_to_truck_ratio_list.append(0)
#            CPD_list.append(0)
#        else:
        trucks_per_day = truck_stop['Tot Trips']
        n_stops_in_range = truck_stop['N_in_200mi']

        # Call the get_min_chargers function to calculate min chargers and ratio
        min_chargers, charger_to_truck_ratio, charges_per_day = get_min_chargers(trucks_per_day, n_stops_in_range, range_miles, charging_time, max_wait_time)

        # Append the results to the lists
        min_chargers_list.append(min_chargers)
        charger_to_truck_ratio_list.append(charger_to_truck_ratio)
        CPD_list.append(charges_per_day)

    # Add the results as new attributes to the GeoDataFrame
    truck_stops_gdf['Min_Charge'] = min_chargers_list
    truck_stops_gdf['Min_Ratio'] = charger_to_truck_ratio_list
    truck_stops_gdf['CPD'] = CPD_list

    return truck_stops_gdf

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--charging_time', default='4', type=float, help = 'Charging time (hours)')
parser.add_argument('-m', '--max_wait_time', default='1', type=float, help = 'Maximum allowable wait time (hours)')
parser.add_argument('-r', '--range_miles', default='200', type=float, help = 'Truck range (miles)')

if __name__ == '__main__':

  args = parser.parse_args()
  
  # Get the path to the top level of the Git repo
  top_dir = get_top_dir()

#  # Read the shapefiles and ensure the CRS is a projected coordinate system to evaluate separation distances
#  truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking.shp').to_crs("EPSG:3857")
#  highways_gdf = gpd.read_file(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_interstate.shp').to_crs("EPSG:3857")
#
#  # Distance threshold between truck stops and highways set to 1km
#  truck_stops_gdf = filter_points_by_distance(points_gdf=truck_stops_gdf, highways_gdf=highways_gdf, distance_threshold=1000)
#
#  # Save the points along interstates
#  saveShapefile(truck_stops_gdf, f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate.shp')
#
#  # Add the trips per day for the nearest highway link to each truck stop
#  truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate.shp').to_crs("EPSG:3857")
#  truck_stops_gdf = add_trips_per_day(truck_stops_gdf, highways_gdf, attribute_name='Tot Trips', distance_threshold=1000)
#
#  # Save the augmented truck_stops_gdf as a shapefile
#  saveShapefile(truck_stops_gdf, f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips.shp')
#
#  # Open the augmented truck stops geodataframe
#  truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips.shp').to_crs("EPSG:3857")
#
#  # Randomly select truck stops so they're separated by at least 50 miles and 100 miles on average
#  truck_stops_gdf = select_truck_stops(truck_stops_gdf)
#  saveShapefile(truck_stops_gdf,f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips_Sparse.shp')
#
#  truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips_Sparse.shp').to_crs("EPSG:3857")
#
#  # Call the function to count truck stops within the radius and add the count as an attribute
#  truck_stops_gdf = count_truck_stops_within_radius(truck_stops_gdf, args.range_miles)
#
#  # Specify the number of processes to use for parallelization
#  num_processes = multiprocessing.cpu_count()  # Use all available CPU cores
#
#  # Call the parallel function to count truck stops within the radius and add the count as an attribute
#  truck_stops_gdf = count_truck_stops_within_radius_parallel(truck_stops_gdf, args.radius_miles, num_processes)
#
#  # Save the augmented truck_stops_gdf as a shapefile
#  saveShapefile(truck_stops_gdf, f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips_and_Stops_Within_200mi.shp')

  # Open the augmented truck stops geodataframe
  truck_stops_gdf = gpd.read_file(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_Tot_Trips_and_Stops_Within_200mi.shp').to_crs("EPSG:3857")

  # For each truck stop, calculate the number of chargers needed to keep quick charging wait times below 30 minutes and add it as an attribute, along with the charger-to-truck ratio
  truck_stops_gdf = apply_min_chargers(truck_stops_gdf, args.range_miles, float(args.charging_time), float(args.max_wait_time))

  # Now suppose we only have half the highway flows (equivalent to splitting the flows between two companies). Calculate the updated min_chargers
  truck_stops_gdf_half = truck_stops_gdf.copy()
  truck_stops_gdf_half['Tot Trips'] = truck_stops_gdf_half['Tot Trips'] / 2.

  truck_stops_gdf_half = apply_min_chargers(truck_stops_gdf_half, args.range_miles, float(args.charging_time), float(args.max_wait_time))

  truck_stops_gdf['Half_CPD'] = truck_stops_gdf_half['CPD']
  truck_stops_gdf['Half_Charge'] = truck_stops_gdf_half['Min_Charge']
  truck_stops_gdf['Half_Ratio'] = truck_stops_gdf_half['Min_Ratio']
  truck_stops_gdf['Col_Save'] = 100.*(1.-truck_stops_gdf['Min_Ratio']/truck_stops_gdf['Half_Ratio'])

  saveShapefile(truck_stops_gdf, f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking_Along_Interstate_with_min_chargers_range_{args.range_miles}_chargingtime_{args.charging_time}_maxwait_{args.max_wait_time}.shp')

#main()
