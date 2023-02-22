

from qgis.core import *
import qgis.utils
from qgis.PyQt import QtGui

######################################## Load and process FAF5 regions #########################################
# Load the FAF5 regions shapefile and add it to the registry if it isn't already there
regions = QgsVectorLayer('/Users/danikamacdonell/GIS/QGIS/FAF5/Freight_Analysis_Framework_(FAF5)_Regions/Freight_Analysis_Framework_(FAF5)_Regions.shp', 'FAF5 Regions', 'ogr')

# Confirm that the regions got loaded in correctly
if not regions.isValid():
  print("Layer failed to load!")
  
# Add the regions to the map if they aren't already there
if not QgsProject.instance().mapLayersByName("FAF5 Regions"):
    QgsProject.instance().addMapLayer(regions)
    
# Apply a filter to only show regions in Texas
regions.setSubsetString('FAF_Zone_D LIKE \'%TX%\'')

# Give each FAF zone a different color
field_name = 'FAF_Zone_D'
field_index = regions.fields().indexFromName(field_name)
unique_values = regions.uniqueValues(field_index)

category_list = []
for value in unique_values:
    symbol = QgsSymbol.defaultSymbol(regions.geometryType())
    category = QgsRendererCategory(value, symbol, str(value))
    category_list.append(category)

renderer = QgsCategorizedSymbolRenderer(field_name, category_list)
regions.setRenderer(renderer)
regions.triggerRepaint()
################################################################################################################

##################################### Load and process FAF5 netowrk links ######################################
# Load in the FAF5 network links shapefile
links = QgsVectorLayer('/Users/danikamacdonell/GIS/QGIS/FAF5/Freight_Analysis_Framework_(FAF5)_Network_Links/Freight_Analysis_Framework_(FAF5)_Network_Links.shp', 'FAF5 Links', 'ogr')

# Confirm that the netowrk links got loaded in correctly
if not links.isValid():
  print("Layer failed to load!")

# Add the links to the map if they aren't already there
if not QgsProject.instance().mapLayersByName("FAF5 Links"):
    QgsProject.instance().addMapLayer(links)
    
# Apply a filter to only show links in Texas
links.setSubsetString('STATE LIKE \'%TX%\'')
################################################################################################################

################################## Load and process FAF5 highway assignments ###################################
# Read in the total highway trucking flows by commodity for 2022
uri = '/Users/danikamacdonell/GIS/QGIS/FAF5/FAF5_Highway_Assignment_Results/FAF5_2022_Highway_Assignment_Results/CSV Format/FAF5 Total Truck Flows by Commodity_2022.csv'
assignments = QgsVectorLayer(uri, 'FAF5 Assignments', 'ogr')

# Skim the assignments down to what we want to work with, and make sure the variable types are correct (by default QGIS reads in CSV data as strings, even if they're actually numbers)
# Note:
proc = processing.run("native:refactorfields", {'INPUT':'/Users/danikamacdonell/GIS/QGIS/FAF5/FAF5_Highway_Assignment_Results/FAF5_2022_Highway_Assignment_Results/CSV Format/FAF5 Total Truck Flows by Commodity_2022.csv','FIELDS_MAPPING':[{'expression': '"ID"','length': 0,'name': 'ID','precision': 0,'sub_type': 0,'type': 2,'type_name': 'integer'},{'expression': '"TOT Tons_22 All"','length': 0,'name': 'TOT Tons_22 All','precision': 0,'sub_type': 0,'type': 6,'type_name': 'double precision'}],'OUTPUT':'TEMPORARY_OUTPUT'})
assignments = proc['OUTPUT']

# Confirm that the highway assignments got loaded in correctly
if not assignments.isValid():
  print("Layer failed to load!")

# Add the highway assignments to the QGIS project
if not QgsProject.instance().mapLayersByName("Refactored"):
    QgsProject.instance().addMapLayer(assignments)
################################################################################################################
    
################## Join the FAF5 assignments to the highway networks via the highway link IDs ##################
#assignments = iface.activeLayer()

# Initialize a vector layer join info object to specify how the join will be performed
info = QgsVectorLayerJoinInfo()

# The common field to be used for joining is the network link ID (called 'ID' in both the assignments and links layers)
info.setJoinFieldName("ID")
info.setTargetFieldName("ID")
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
################################################################################################################
