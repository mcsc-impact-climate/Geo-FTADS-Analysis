# Import needed modules
from qgis.core import *
import qgis.utils
from qgis.PyQt import QtGui
import os
from console.console import _console
import sys

def getTopDir():
    '''
    Gets the path to top level of the git directory

    Parameters
    ----------
    None

    Returns
    -------
    top_dir (string): path to the top level of the directory, or None if the source directory doesn't end in 'source'
    '''
    top_dir = None
    # Get the path to top level of the git directory so we can use relative paths
    source_dir = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)
    if source_dir.endswith('/source'):
        top_dir = source_dir[:-7]
    elif source_dir.endswith('/source/'):
        top_dir = source_dir[:-8]
    else:
        print("ERROR: Expect current directory to end with 'source'. Cannot use relative directories as-is. Exiting...")
    return top_dir
    

def readRegions(path, name):
    '''
    Reads in the shapefiles containing FAF5 regions augmented with total imports and exports (in tons/year)

    Parameters
    ----------
    path (string): Path to thd shapefile to be read in

    name (string): Name to assign to the QGIS vector layer produced from the shapefile read in

    Returns
    -------
    regions (class 'qgis._core.QgsVectorLayer'): QGIS vector layer produced from the shapefile read in
    '''
    regions = QgsVectorLayer(path, name, 'ogr')

    # Confirm that the regions got loaded in correctly
    if not regions.isValid():
      print('Layer failed to load!')

    # Add the regions to the map if they aren't already there
    if not QgsProject.instance().mapLayersByName(name):
        QgsProject.instance().addMapLayer(regions)

    # Apply a filter for the moment to remove Hawaii and Alaska
    regions.setSubsetString('NOT FAF_Zone_D LIKE \'%Alaska%\' AND NOT FAF_Zone_D LIKE \'%HI%\'')

    return regions
    
def load_highway_links(links_path, st=None):
    '''
    Loads in the highway network links produced by HighwayAssignmentTools.py with the FAF5 flux data included.

    Parameters
    ----------
    path_to_links (string): Path to the shapefile containing the highway links

    Returns
    -------
    None
    '''

    # Load in the FAF5 network links shapefile
    links = QgsVectorLayer(links_path, 'FAF5 Links', 'ogr')
    
    # Confirm that the netowrk links got loaded in correctly
    if not links.isValid():
        print('Highway links failed to load!')
        
    # Add the links to the map if they aren't already there
    if not QgsProject.instance().mapLayersByName('Total Tons Transported by Highway'):
        QgsProject.instance().addMapLayer(links)
    
    # Apply a filter to only show links in the given state
    if st is not None: links.setSubsetString(st)
        
    return links
    
def style_highway_links(links):
    '''
    Styles the highway links to make the width of each link proportional to the total annual flux carried

    Parameters
    ----------
    links (class 'qgis._core.QgsVectorLayer'): Highway network links, including attribute quantifying annual flux carried over each link

    Returns
    -------
    None
    '''
    # Target field is by default the total tons transported as weighting factor for network link widths
    #myTargetField = 'Refactored_TOT Tons_22 All'
    myTargetField = 'TOT Tons_2'

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
    renderer.setSymbolSizes(0.1, 2)
    #renderer.updateColorRamp()

    # Apply the graduated symbol renderer defined above to the network links
    links.setRenderer(renderer)

def applyGradient(regions, target_field):
    '''
    Applies a color gradient to the FAF5 regions according to the specified target field

    Parameters
    ----------
    regions (class 'qgis._core.QgsVectorLayer'): QGIS vector layer containing FAF5 regions and associated imports/exports

    target_field (string): Field that the color gradient will be based on (must be decimal or int)

    Returns
    -------
    None
    '''
    # Color the regions with a gradient defined by their total imports or exports
    format = QgsRendererRangeLabelFormat()
    format.setFormat("%1 - %2")
    format.setPrecision(2)
    format.setTrimTrailingZeroes(True)
    color_ramp = QgsStyle().defaultStyle().colorRamp('Reds')
    ramp_num_steps = 10  # Number of bins to use for the color gradient

    renderer = QgsGraduatedSymbolRenderer(target_field)
    renderer.setClassAttribute(target_field)
    renderer.setClassificationMethod(QgsClassificationJenks())
    renderer.setLabelFormat(format)
    renderer.updateClasses(regions, ramp_num_steps)
    renderer.updateColorRamp(color_ramp)
    regions.setRenderer(renderer)
    regions.triggerRepaint()

def saveMap(layers, layout_title, legend_title, layout_name, file_name):
    '''
    Saves the specified layers to a pdf file containing a map of the layers and associated legend

    Parameters
    ----------
    layers (list of class 'qgis._core.QgsVectorLayer' objects): QGIS layers to be included in the map

    layout_title (string): Layout name to be shown on the output pdf

    legend_title (string): Legend name to be shown on the output pdf

    layout_name (string): Layout name to be used internally

    file_name (string): Path to the output pdf file

    Returns
    -------
    None
    '''
    project = QgsProject.instance()
    manager = project.layoutManager()
    layoutName = layout_name
    layouts_list = manager.printLayouts()
    # remove any duplicate layouts
    for layout in layouts_list:
        if layout.name() == layoutName:
            manager.removeLayout(layout)
    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(layoutName)
    manager.addLayout(layout)

    # create map item in the layout
    map = QgsLayoutItemMap(layout)
    map.setRect(20, 20, 20, 20)

    # set the map extent
    ms = QgsMapSettings()
    ms.setLayers(layers)  # set layers to be mapped
    rect = QgsRectangle(ms.fullExtent())
    rect.scale(1.0)
    ms.setExtent(rect)
    map.setExtent(rect)
    map.setBackgroundColor(QColor(255, 255, 255, 0))
    layout.addLayoutItem(map)

    map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
    map.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))

    legend = QgsLayoutItemLegend(layout)
    legend.setTitle(legend_title)
    layerTree = QgsLayerTree()
    for layer in layers:
        layerTree.addLayer(layer)
    legend.model().setRootGroup(layerTree)
    layout.addLayoutItem(legend)
    legend.attemptMove(QgsLayoutPoint(230, 15, QgsUnitTypes.LayoutMillimeters))

    title = QgsLayoutItemLabel(layout)
    title.setText(layout_title)
    title.setFont(QFont('Arial', 24))
    title.adjustSizeToText()
    layout.addLayoutItem(title)
    title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))

    layout = manager.layoutByName(layoutName)
    exporter = QgsLayoutExporter(layout)

    # exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())
    exporter.exportToPdf(file_name, QgsLayoutExporter.PdfExportSettings())

def main():
    top_dir = getTopDir()
    if top_dir is None:
        exit()
        


    # Plot and save total domestic imports
    regions_import = readRegions(f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage.shp', 'FAF5 Regions Imports')
    applyGradient(regions_import, 'Total Impo')
    #saveMap([regions], 'Total Domestic Imports', 'Imports [tons/year]', 'total_domestic_imports', f'{top_dir}/layouts/total_domestic_imports.pdf')

    # Plot and save total domestic exports
    regions_export = readRegions(f'{top_dir}/data/FAF5_regions_with_tonnage/FAF5_regions_with_tonnage.shp', 'FAF5 Regions Exports')
    applyGradient(regions_export, 'Total Expo')
    #saveMap([regions], 'Total Domestic Exports', 'Exports [tons/year]', 'total_domestic_exports', f'{top_dir}/layouts/total_domestic_exports.pdf')
    
    # Add the highway assignments
    links = load_highway_links(f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp')
    
    # Style highway links
    style_highway_links(links)
    
    
    

main()
