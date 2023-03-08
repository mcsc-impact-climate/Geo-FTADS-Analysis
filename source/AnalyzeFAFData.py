# Import needed modules
from qgis.core import *
import qgis.utils
from qgis.PyQt import QtGui
import processing
import os
from console.console import _console
import sys


# Get the path to top level of the git directory so we can use relative paths
source_dir = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)
if source_dir.endswith('/source'):
    top_dir = source_dir[:-7]
elif source_dir.endswith('/source/'):
    top_dir = source_dir[:-8]
else:
    print("ERROR: Expect current directory to end with 'source'. Cannot use relative directories as-is. Exiting...")
    sys.exitfunc()
    

def loadRegions(st=None):
    '''
    Load and process FAF5 regions
    '''
    # Load the FAF5 regions shapefile and add it to the registry if it isn't already there
    regions = QgsVectorLayer(f'{top_dir}/data/FAF5_regions/Freight_Analysis_Framework_(FAF5)_Regions.shp', 'FAF5 Regions', 'ogr')

    # Confirm that the regions got loaded in correctly
    if not regions.isValid():
      print('Layer failed to load!')
      
    # Add the regions to the map if they aren't already there
    if not QgsProject.instance().mapLayersByName('FAF5 Regions'):
        QgsProject.instance().addMapLayer(regions)
    
        
    # Load the data csv and add it to the registry if it isn't already there
    data = QgsVectorLayer(f'file:///{top_dir}/data/total_tons.csv', 'Total Tons', 'delimitedtext')
    QgsProject.instance().addMapLayer(data)
    
    # Confirm that the data got loaded in correctly
    if not data.isValid():
      print('Layer failed to load!')
    
    shpField = 'FAF_Zone_D'
    csvField = 'Short Description'
    
    joinObject = QgsVectorLayerJoinInfo()
    joinObject.setJoinFieldName(csvField)
    joinObject.setTargetFieldName(shpField)
    joinObject.setJoinLayerId(data.id())
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(data)
    regions.addJoin(joinObject)
    

    passin = f'FAF_Zone_D LIKE {st}'
    # print(passin, len(states))
    # Apply a filter to only show regions in 'State'
    if st is not None: regions.setSubsetString(st)

    fieldName = 'Total Tons_Total Import'
    fieldIndex = regions.fields().indexFromName(fieldName)
    uniqueValues = regions.uniqueValues(fieldIndex)
    
    vals = []
    for f in regions.getFeatures():
        vals.append(f[fieldName])
    # print(vals)
    
    colors = ['#b7f7f3', '#8ce1e8', '#5ccbdf', '#14b5d8', '#009dd2', '#0086ca', '#006dc0', '#0054b2', '#003a9f', '#001b87']
    lower = sorted(vals)[0]
    upper = sorted(vals)[-1]
    step = (upper-lower)/len(colors)
    
    catList = []
    for color in colors:
        cat = [lower, lower+step, color]
        sym = QgsSymbol.defaultSymbol(regions.geometryType())
        sym.setColor(QColor(cat[2]))
        rng = QgsRendererRange(cat[0], cat[1], sym, '{0:.1f}-{1:.1f}'.format(cat[0], cat[1]))
        catList.append(rng)
        lower = (lower+step)+0.1
        
    renderer = QgsGraduatedSymbolRenderer(fieldName, catList)
    regions.setRenderer(renderer)
    regions.triggerRepaint()
    
# =============================================================================
#     # Give each FAF zone a different color
#     field_name = 'FAF_Zone_D'
#     field_index = regions.fields().indexFromName(field_name)
#     unique_values = regions.uniqueValues(field_index)
# 
#     category_list = []
#     for value in unique_values:
#         symbol = QgsSymbol.defaultSymbol(regions.geometryType())
#         category = QgsRendererCategory(value, symbol, str(value))
#         category_list.append(category)
# 
#     renderer = QgsCategorizedSymbolRenderer(field_name, category_list)
#     regions.setRenderer(renderer)
#     regions.triggerRepaint()
# =============================================================================


def loadNetworkLinks(st=None):
    ''' 
    Load and process FAF5 network links 
    '''
    # Load in the FAF5 network links shapefile
    links = QgsVectorLayer(f'{top_dir}/data/FAF5_network_links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp', 'FAF5 Links', 'ogr')

    # Confirm that the netowrk links got loaded in correctly
    if not links.isValid():
      print('Layer failed to load!')

    # Add the links to the map if they aren't already there
    if not QgsProject.instance().mapLayersByName('FAF5 Links'):
        QgsProject.instance().addMapLayer(links)
        
    # Apply a filter to only show links in 'State'
    if st is not None: links.setSubsetString(st)
    return links
    
    
def highways(links):
    '''
    Load and process FAF5 highway assignments
    '''
    # Read in the total highway trucking flows by commodity for 2022
    uri = f'{top_dir}/data/FAF5_highway_assignment_results/FAF5_2022_Highway_Assignment_Results/CSV Format/FAF5 Total Truck Flows by Commodity_2022.csv'
    assignments = QgsVectorLayer(uri, 'FAF5 Assignments', 'ogr')
    
    # Skim the assignments down to what we want to work with, and make sure the variable types are correct (by default QGIS reads in CSV data as strings, even if they're actually numbers)
    # Note:
    proc = processing.run("native:refactorfields", {'INPUT':uri,'FIELDS_MAPPING':[{'expression': '"ID"','length': 0,'name': 'ID','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'expression': '"TOT Tons_22 All"','length': 0,'name': 'TOT Tons_22 All','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'}],'OUTPUT':'TEMPORARY_OUTPUT'})
    assignments = proc['OUTPUT']
    
    # Confirm that the highway assignments got loaded in correctly
    if not assignments.isValid():
      print('Layer failed to load!')
    
    # Add the highway assignments to the QGIS project
    if not QgsProject.instance().mapLayersByName('Refactored'):
        QgsProject.instance().addMapLayer(assignments)
        
    ################## Join the FAF5 assignments to the highway networks via the highway link IDs ##################
    #assignments = iface.activeLayer()

    # Initialize a vector layer join info object to specify how the join will be performed
    info = QgsVectorLayerJoinInfo()

    # The common field to be used for joining is the network link ID (called 'ID' in both the assignments and links layers)
    info.setJoinFieldName('ID')
    info.setTargetFieldName('ID')
    info.setJoinLayer(assignments)

    # Specify that the joined layer will be stored in memory for ready access
    info.setUsingMemoryCache(True)

    # Apply the join to the network links layer
    links.addJoin(info)
    ################################################################################################################

    ######################### Style the network links to have width proportional to tonnage ########################
    # Target field is by default the total tons transported as weighting factor for network link widths
    myTargetField = 'Refactored_TOT Tons_22 All'

    # Specify the range of possible weighting factors as the max and min range of the target field
    ramp_max = links.maximumValue(links.fields().indexFromName(myTargetField))
    ramp_min = links.minimumValue(links.fields().indexFromName(myTargetField))

    # Classify the tonnages into 5 bins
    ramp_num_steps = 5

    # Initialize a graduated renderer object specify how the network link symbol properties will vary according to the numerical target field
    renderer = QgsGraduatedSymbolRenderer(myTargetField)
    renderer.setClassAttribute(myTargetField)

    # Specify the network link symbol to be a black line in all cases
    symbol = QgsSymbol.defaultSymbol(links.geometryType())
    symbol.setColor(QtGui.QColor('#000000'))
    renderer.setSourceSymbol(symbol)

    # Specify the binning method (jenks), number of bins, and range of line widths for the graduated renderer
    renderer.setClassificationMethod(QgsClassificationJenks())
    renderer.updateClasses(links, ramp_num_steps)
    renderer.setSymbolSizes(0.1, 3)
    #renderer.updateColorRamp()

    # Apply the graduated symbol renderer defined above to the network links
    links.setRenderer(renderer)
    

def loadFilteredData():
    pass


def regionFilter(key, states):
    st = ''
    for i in range(len(states)):
        st += key + ' LIKE ' + '\'%' + states[i] + '%\''
        if i < len(states)-1:
            st += ' OR '
            
    return st

def main():
    states = ['Maine', 'NH', 'MA', 'Vermont']    
    # regionFilter('FAF_Zone_D', states)
    loadRegions()
    loadFilteredData()
    
    # regionFilter('STATE', states)
    links = loadNetworkLinks()
    highways(links)
    
    
main()
