#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 09:28:26 2023

@author: micahborrero
"""

import geopandas as gpd
import pandas as pd
import math
import matplotlib.pyplot as plt
import momepy
import numpy as np
import networkx as nx
import time
import pickle
import os

from scipy import spatial
from datetime import datetime

from CommonTools import get_top_dir


top_dir = get_top_dir()

start = time.time()


def loadShapefile(path, isgeojson = False):
    '''
    Reads in shapefile and converts to EPSG:4326 coordinate reference system

    Parameters
    ----------
    path : str
        String describing the path to the desired shapefile.

    Returns
    -------
    shapefile : Geopandas DataFrame
        DataFrame containing desired shapefile.

    '''
    shapefile = gpd.read_file(path)
    
    # Files saved as geojson by default save as EPSG 3857 - this allows for proper
    #  correction to standardized 4326 when reading in
    if isgeojson:
        shapefile.crs = {'init' :'epsg:3857'}
        
    shapefile = shapefile.to_crs("epsg:4326")
    
    return shapefile


def extractHighways():
    '''
    Additionally converts all 'Null' 'Tot Tons' values to 0
    Rescale/flip ton miles in a new column such that the max is 0 and the "0s" are the max value
    
    Returns
    -------
    highways : Geopandas DataFrame
        DataFrame containing all highway elements as defined by FAF5.

    '''
    highwayPath = f'{top_dir}/web/geojsons_simplified/highway_assignments.geojson' 
    # highwayPath = f'{top_dir}/data/highway_filter_testing/highway_assignments.shp'  
    
    highways = loadShapefile(highwayPath)


    highways['Tot Tons'] = highways['Tot Tons'].fillna(0)
    
    # Rescale/flip ton miles in a new column such that the max is 0 and the "0s" are the max value
    maxTons = highways['Tot Tons'].max()
    highways['Scaled Tot Tons'] = maxTons - highways['Tot Tons']

    return highways
    

def combinedStatisticalAreasCentroids():
    '''
    TODO: Integrate functionality to find the union of MSAs and CSAs

    Returns
    -------
    cent : Geopandas DataFrame
        GeoDataFrame containing the centroids of all Census defined 
        Combined Statistical Areas.

    '''
    
    csaPath = f'{top_dir}/data/tl_2023_us_csa/tl_2023_us_csa.shp' 
    csa = gpd.read_file(csaPath)

    csa.to_crs('epsg:4326')
    cent = csa.to_crs('+proj=cea').centroid.to_crs(csa.crs)
    
    cent = gpd.GeoDataFrame(geometry=cent)
    cent['name'] = csa['NAME']
    
    return cent


def createGraph(highways):
    '''
    Parameters
    ----------
    highways : Geopandas DataFrame
        GeoDataFrame containing all of the filtered FAF5 highways.

    Returns
    -------
    graph : MultiGraph
        NX MultiGraph of filtered FAF5 highways.
    positions : Dict
        Dictionary of geographic location of nodes in highway graph.

    '''
    
    graph = momepy.gdf_to_nx(highways, approach='primal')
    positions = {n: [n[0], n[1]] for n in list(graph.nodes)}
    graph.remove_edges_from(list(nx.selfloop_edges(graph)))
    
    return graph, positions


def saveGraph(filename, graph=None, load=True):
    '''
    Saves or loads NX MultiGraph.
    TODO: Integrate timestamp in file naming
    
    Parameters
    ----------
    filename : str
        Filename of saved graph.
    graph : NX MultiGraph, optional
        NX MultiGraph of filtered FAF5 highways. The default is None.
    load : bool, optional
        Boolean defining whether to save or load graph. The default is True.

    Returns
    -------
    graph : NX MultiGraph
        NX MultiGraph of filtered FAF5 highways.

    '''   
    name = filename #+ '_' + datetime.now().strftime("%H%M")
    
    # Create the directory to contain geojsons if it doesn't exist
    if not os.path.exists(f'{top_dir}/data/pickles'):
        os.makedirs(f'{top_dir}/data/pickles')

    if not load:
        # save graph object to file
        pickle.dump(graph, open(f'{top_dir}/data/pickles/{name}.pickle', 'wb'))
        print('Graph saved...')
    else:
        # load graph object from file
        graph = pickle.load(open(f'{top_dir}/data/pickles/{name}.pickle', 'rb'))
        print('Graph loaded...')
        return graph


def defineODPoints(graph, centroids, positions):
    '''
    Parameters
    ----------
    graph : MultiGraph
        NX MultiGraph of filtered FAF5 highways.
    centroids : DataFrame
        GeoDataFrame containing the centroids of all Census defined 
        Combined Statistical Areas.
    positions : Dict
        Dictionary of geographic locations of nodes in highway graph.

    Returns
    -------
    ret : Dict
        Dictionary of CSAs with associated node location.

    '''
    
    pos = list(positions.keys())
    ret = dict()
    tree = spatial.KDTree(pos)
    
    for index, row in centroids.iterrows(): 
        find =[row.geometry.x, row.geometry.y]
        closest = pos[tree.query(find)[1]]
        ret[row['name']] = closest
        
    return ret


def dist(a, b):
    '''
    Heuristic for A* algorithm used in the pathfinding method.
    It is presumed that the distance between nodes is small enough and the 
        they are near enough to the equatorsuch that the distance formula 
        still holds true.
    '''
    
    (x1, y1) = a
    (x2, y2) = b
    
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def findPath(graph, orig, dest):
    
    # Shortest path using A*
    path = nx.astar_path(graph, orig, dest, heuristic=dist, weight="Tot Tons")
    
    pathgraph = graph.subgraph(path)
    
    '''
    # TODO: MultiGraph using this method is not supported as of yet, potentially keep in back pocket for future update
    # Shortest path using the shortest_augmenting_path method
    path = nx.algorithms.flow.shortest_augmenting_path(graph, orig, dest, capacity='Tot Tons')
    '''
    return path, pathgraph


def visualize(visual, positions=None, isnx=False):
    '''
    Method to produce plots of graphs or highway shapefiles.

    Parameters
    ----------
    visual : MultiGraph or Geopandas DataFrame
        NX MultiGraph of highways/path or GeoDataFrame of highways.
    positions : Dict, optional
        Dictionary of the geographic locations of nodes in highway graph. The default is None.
    isnx : bool, optional
        Boolean defining whether or not visual is a NX MultiGraph vs GeoDataFrame. The default is False.

    Returns
    -------
    None.

    '''
    
    if isnx:
        if positions != None:
            nx.draw(visual, positions, node_color='tab:blue', node_size=1)
        else:
            nx.draw(visual, {n:[n[0], n[1]] for n in list(visual.nodes)}, node_color='red', node_size=1)
    else:
        visual.plot()

    
def toShapefile(graph, filename):
    '''
    Converts NetworkX Graph to GeoDataFrame and saves as shapefile.
    TODO: Had to manually change method references in module 'networkx' from
        'to_scipy_sparse_matrix' to 'to_scipy_sparse_array' => find out which 
        library needs to be updated.

    Parameters
    ----------
    graph : MultiGraph
        NX MultiGraph of path.
    filename : str
        Filename of shapefile.

    Returns
    -------
    None.

    '''
    # Create the directory to contain geojsons if it doesn't exist
    if not os.path.exists(f'{top_dir}/data/paths_of_interest'):
        os.makedirs(f'{top_dir}/data/paths_of_interest')

    nodes, edges, sw = momepy.nx_to_gdf(graph, points=True, lines=True, spatial_weights=True)
    edges.to_file(f"{top_dir}/data/paths_of_interest/{filename}.shp")
    

if __name__ == "__main__":
    #The user should change this value based upon whether or not they are starting fresh
    load = False
    
    #Can be modified based on needs/testing
    if not load:
        centroids = combinedStatisticalAreasCentroids()
        highways = extractHighways()
        graph, positions = createGraph(highways)
        origins = defineODPoints(graph, centroids, positions)
        
        saveGraph('centroids', centroids, load=False)
        saveGraph('graph', graph, load=False)
        saveGraph('positions', positions, load=False)
        saveGraph('origins', origins, load=False)

    else:
        centroids = saveGraph('centroids', load=True)
        graph = saveGraph('graph', load=True)
        positions = saveGraph('positions', load=True)
        origins = saveGraph('origins', load=True)

    
    # path, pathgraph = findPath(graph, origins['San Jose-San Francisco-Oakland, CA'], origins['Seattle-Tacoma, WA'])
    # newpath, newpathgraph = findPath(graph, origins['Cape Coral-Fort Myers-Naples, FL'], origins['Tallahassee-Bainbridge, FL-GA'])
    # ultranewpath, ultranewpathgraph = findPath(graph, origins['Seattle-Tacoma, WA'], origins['Tallahassee-Bainbridge, FL-GA'])
    
    
    path, pathgraph = findPath(graph, origins['Houston-Pasadena, TX'], origins['Los Angeles-Long Beach, CA'])
    newpath, newpathgraph = findPath(graph, origins['Salt Lake City-Provo-Orem, UT-ID'], origins['Duluth-Grand Rapids, MN-WI'])
    ultranewpath, ultranewpathgraph = findPath(graph, origins['Boston-Worcester-Providence, MA-RI-NH'], origins['Miami-Port St. Lucie-Fort Lauderdale, FL'])
    
    end = time.time()
    print(end - start)
    
    
    # visualize(graph, positions, isnx=True)
    # visualize(pathgraph, isnx=True)
    
    # toShapefile(pathgraph, 'BayToSea')
    
    toShapefile(pathgraph, 'TXCA')
    toShapefile(newpathgraph, 'UTMN')
    toShapefile(ultranewpathgraph, 'MAFL')
    
    # return centroids, graph, positions, origins, path, pathgraph
    

# centroids, graph, positions, origins, path, pathgraph = main()
