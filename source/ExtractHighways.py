#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 09:28:26 2023

@author: micahborrero
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

# import osmnx as ox
import networkx as nx

import sys
from libpysal import weights, examples

from shapely.geometry import Point
from shapely.ops import nearest_points
from scipy.spatial import cKDTree

from CommonTools import get_top_dir


top_dir = get_top_dir()


def extractHighways():
    '''
    Returns
    -------
    highways : Geopandas DataFrame
        DataFrame containing all highway elements as defined by FAF5.

    '''
    highwayPath = f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp'    
    highways = gpd.read_file(highwayPath)

    return highways
    

def filt(highways):
    nodes = highways[(highways['Road_Name'] == 'I 10')].reset_index(drop=True)
    
    return nodes
    

def convertToPoints(highways):
    '''
    Converts highways shapefile to set of points.

    Parameters
    ----------
    highways : GeoSeries
        GeoSeries dataframe/shapefile containing [linesstrings] of highways.

    Returns
    -------
    points : GeoSeries
        GeoSeries dataframe/shapefile containing [points] of highways..

    '''
    points = highways.copy()
    points['geometry'] = points['geometry'].centroid
    # print(points)
    
    return points


def findNearest(highways, city, maxDistance=100):
    '''
    WIP - To be modified IAW highway attribute conventions

    Parameters
    ----------
    highways : GeoSeries
        DESCRIPTION.
    city : String
        DESCRIPTION.

    Returns
    -------
    gdf : TYPE
        Returns the distance and 'Name' of the nearest neighbor in gpd2 from 
        each point in gpd1. It assumes both gdfs have a geometry column 
        (of points).

    '''
    cit = gpd.tools.geocode(city, provider='nominatim', user_agent='test_user', timeout=4)
    
    
    nA = np.array(list(cit.geometry.apply(lambda x: (x.x, x.y))))    
    nB = np.array(list(highways.geometry.apply(lambda x: (x.x, x.y))))
    
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    # gdB_nearest = highways.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdB_nearest = highways.iloc[idx]
    
    # gdf = pd.concat(
    #     [
    #         cit.reset_index(drop=True),
    #         gdB_nearest,
    #         pd.Series(dist, name='dist')
    #     ], 
    #     axis=1)

    return gdB_nearest
   

highways = extractHighways()
filtered = filt(highways)
points = convertToPoints(filtered)

# start = absolute(highways, 64., 'CONTRA COSTA', 61., 'LOS ANGELES', 'Interstate Highway')

orig = findNearest(points, "San Francisco")
# print(ret)
print(orig.index[0])
dest = findNearest(points, "Los Angeles")

# points.plot()

# print(points)

coordinates = np.column_stack((points.geometry.x, points.geometry.y))
dist = weights.DistanceBand.from_array(coordinates, threshold=50000)
dist_graph = dist.to_networkx()

# print(dist_graph.nodes)
knn3 = weights.KNN.from_dataframe(points, k=3)

'''
It is not crucial to add attributes to the NetworkX nodes given that we know
    the index of the node based on the orignal filtered data. The index does 
    not change when it is converted to a networkx data type.

ids = filtered['ID']
print(ids)
nx.set_node_attributes(dist_graph, ids)

print(dist_graph.nodes(data=True)[50])

sys.exit()
# print(dist_graph.nodes(data=True))
'''


f, ax = plt.subplots(1, 1, figsize=(8, 8))
# for i, facet in enumerate(ax):
#     points.plot(marker=".", color="orangered", ax=facet)
#     # add_basemap(facet)
#     facet.set_title(("KNN-3", "50-meter Distance Band")[i])
#     facet.axis("off")
positions = dict(zip(dist_graph.nodes, coordinates))
# print(positions)

nx.draw(dist_graph, positions, ax=ax, node_size=2, node_color="b")

path = nx.shortest_path(dist_graph, source=orig.index[0], target=dest.index[0])
path_edges = list(zip(path,path[1:]))
nx.draw_networkx_nodes(dist_graph, positions, nodelist=path, node_color='r')
nx.draw_networkx_edges(dist_graph, positions, edgelist=path_edges, edge_color='r', width=10)
# print(p1to6)
plt.show()



# def absolute(highways, org_FAF, org_county, dest_FAF, dest_county, roadtype):
#     '''
#     Finds the absolute "best" route as defined by the highest throughput combined with the shortest distance
    
#     Initially filter according to starting county, origin FAFzone, and hihway type


#     Parameters
#     ----------
#     highways : TYPE
#         DESCRIPTION.
#     org_FAF : TYPE
#         DESCRIPTION.
#     org_county : TYPE
#         DESCRIPTION.
#     dest_FAF : TYPE
#         DESCRIPTION.
#     dest_county : TYPE
#         DESCRIPTION.
#     roadtype : TYPE
#         DESCRIPTION.

#     Returns
#     -------
#     starting_node : TYPE
#         DESCRIPTION.

#     '''
#     starting_node = highways[(highways['FAFZONE'] == float(org_FAF)) & (highways['County_Nam'] == org_county) & (highways['Class_Desc'] == roadtype)]
#     starting_node = highways[highways['Tot Tons'] == highways['Tot Tons'].max()]
#     # We define the starting node as the one 
#     # print(starting_node)
    
#     return starting_node.geometry.centroid
    