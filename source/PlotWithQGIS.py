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
    

def readShapefile(path, name, color='white', opacity=1):
    '''
    Reads in a shapefile

    Parameters
    ----------
    path (string): Path to thd shapefile to be read in

    name (string): Name to assign to the QGIS vector layer produced from the shapefile read in
    
    color (string): Color to assign to the shapefile layer

    Returns
    -------
    regions (class 'qgis._core.QgsVectorLayer'): QGIS vector layer produced from the shapefile read in
    '''
    layer = QgsVectorLayer(path, name, 'ogr')

    # Confirm that the layer got loaded in correctly
    if not layer.isValid():
      print('Layer failed to load!')

    # Add the layer to the map if it isn't already there
    if not QgsProject.instance().mapLayersByName(name):
        QgsProject.instance().addMapLayer(layer)
    
    layer.renderer().symbol().setColor(QColor(color))
    
    # Set opacity
    layer.setOpacity(opacity)
    
    iface.layerTreeView().refreshLayerSymbology(layer.id())

    # Apply a filter for the moment to remove Hawaii and Alaska
#    if 'FAF5' in path:
#        regions.setSubsetString('NOT FAF_Zone_D LIKE \'%Alaska%\' AND NOT FAF_Zone_D LIKE \'%HI%\'')

    return layer
    
def change_line_width(layer, width):
    layer.renderer().symbol().setWidth(width)
    return layer
    
def load_highway_links(links_path, layer_name='Highway Flux (tons/link)', st=None):
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
    links = QgsVectorLayer(links_path, layer_name, 'ogr')
    
    # Confirm that the netowrk links got loaded in correctly
    if not links.isValid():
        print('Highway links failed to load!')
        
    # Add the links to the map if they aren't already there
    if not QgsProject.instance().mapLayersByName(layer_name):
        QgsProject.instance().addMapLayer(links)
    
    # Apply a filter to only show links in the given state
    if st is not None: links.setSubsetString(st)
        
    return links
    
def style_highway_links(links, color='black'):
    '''
    Styles the highway links to make the width of each link proportional to the total annual flux carried

    Parameters
    ----------
    links (class 'qgis._core.QgsVectorLayer'): Highway network links, including attribute quantifying annual flux carried over each link
    
    color (string): Color to assign to the highway links

    Returns
    -------
    None
    '''
    # Target field is by default the total tons transported as weighting factor for network link widths
    #myTargetField = 'Refactored_TOT Tons_22 All'
    myTargetField = 'Tot Tons'

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
    symbol.setColor(QColor(color))
    renderer.setSourceSymbol(symbol)

    # Specify the binning method (jenks), number of bins, and range of line widths for the graduated renderer
    renderer.setClassificationMethod(QgsClassificationJenks())
    renderer.updateClasses(links, ramp_num_steps)
    renderer.setSymbolSizes(0.1, 2)
    #renderer.updateColorRamp()

    # Apply the graduated symbol renderer defined above to the network links
    links.setRenderer(renderer)

def applyColorGradient(regions, target_field, colormap='Reds'):
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
    color_ramp = QgsStyle().defaultStyle().colorRamp(colormap)
    ramp_num_steps = 5  # Number of bins to use for the color gradient

    renderer = QgsGraduatedSymbolRenderer(target_field)
    renderer.setClassAttribute(target_field)
    renderer.setClassificationMethod(QgsClassificationJenks())
    renderer.setLabelFormat(format)
    renderer.updateClasses(regions, ramp_num_steps)
    renderer.updateColorRamp(color_ramp)
    regions.setRenderer(renderer)
    regions.triggerRepaint()
    
def applySizeGradient(list_of_layers, list_of_colors, target_field, marker_shape = 'circle'):

    # Specify the range of possible weighting factors as the max and min range of the target field
    ramp_max=-9e9
    ramp_min=9e9
    
    for layer in list_of_layers:
        this_ramp_max = layer.maximumValue(layer.fields().indexFromName(target_field))
        this_ramp_min = layer.minimumValue(layer.fields().indexFromName(target_field))
        if this_ramp_max > ramp_max:
            ramp_max = this_ramp_max
        if this_ramp_min < ramp_min:
            ramp_min = this_ramp_min
            
    # Classify the tonnages into 5 bins
    ramp_num_steps = 4
        
    i_layer = 0
    for layer in list_of_layers:

        # Initialize a graduated renderer object specify how the network link symbol properties will vary according to the numerical target field
        intervals = QgsClassificationEqualInterval().classes(ramp_min, ramp_max, ramp_num_steps)
        render_range_list = [QgsRendererRange(i, QgsMarkerSymbol.createSimple({'name': marker_shape, 'color': list_of_colors[i_layer]})) for i in intervals]
        renderer = QgsGraduatedSymbolRenderer(target_field, render_range_list)
        #renderer = QgsGraduatedSymbolRenderer(target_field)
        renderer.setClassAttribute(target_field)

        # Specify the network link symbol to be a black line in all cases
        symbol = QgsMarkerSymbol.createSimple({'name': marker_shape, 'color': list_of_colors[i_layer]})
        renderer.setSourceSymbol(symbol)

        # Specify the binning method (jenks), number of bins, and range of line widths for the graduated renderer
        #renderer.setClassificationMethod(QgsClassificationJenks())
        #renderer.updateClasses(layer, ramp_num_steps)
        renderer.setSymbolSizes(2, 8)
        layer.setRenderer(renderer)
        i_layer += 1
    

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
    
def add_basemap(path, name):
    '''
    Adds a basemap with political boundaries

    Parameters
    ----------
    path (string): Path of the basemap source
    
    name (string): Name of the basemap layer in QGIS

    Returns
    -------
    None
    '''
    basemap_layer=QgsRasterLayer(path, name, 'wms')
    QgsProject.instance().addMapLayer(basemap_layer)

def main():
    top_dir = getTopDir()
    if top_dir is None:
        exit()
        
    # Add a basic basemap with political boundaries
    add_basemap('type=xyz&zmin=0&zmax=20&url=https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', 'ESRI Gray')

#    # Plot and save total domestic imports
#    faf5_regions_import = readShapefile(f'{top_dir}/data/Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp', 'Imports (ton-miles / sq mile)')
#    applyColorGradient(faf5_regions_import, 'Tmil Imp D')
#    #saveMap([regions], 'Total Domestic Imports', 'Imports [ton-miles/year]', 'total_domestic_imports', f'{top_dir}/layouts/total_domestic_imports.pdf')
#
#    # Plot and save total domestic exports
#    faf5_regions_export = readShapefile(f'{top_dir}/data/Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp', 'Exports (ton-miles / sq mile)')
#    applyColorGradient(faf5_regions_export, 'Tmil Exp D')
#    #saveMap([regions], 'Total Domestic Exports', 'Exports [tons/year]', 'total_domestic_exports', f'{top_dir}/layouts/total_domestic_exports.pdf')
#
#    # Plot and save total domestic exports+imports
#    faf5_regions_total = readShapefile(f'{top_dir}/data/Point2Point_outputs/mode_truck_commodity_all_origin_all_dest_all.shp', 'Imports+Exports (ton-miles / sq mile)')
#    applyColorGradient(faf5_regions_total, 'Tmil Tot D')
#    #saveMap([regions], 'Total Domestic Exports', 'Exports [tons/year]', 'total_domestic_exports', f'{top_dir}/layouts/total_domestic_exports.pdf')
#
#    # Add grid emission intensity
#    egrids_regions = readShapefile(f'{top_dir}/data/egrid2020_subregions_merged/egrid2020_subregions_merged.shp', 'CO2e intensity of power grid (lb/MWh)')
#    applyColorGradient(egrids_regions, 'SRC2ERTA', colormap='Reds')
#
#    # Add commercial electricity prices by state
#    elec_prices_by_state = readShapefile(f'{top_dir}/data/electricity_rates_merged/electricity_rates_by_state_merged.shp', 'Commercial Elec Price by State (cents / kWh)')
#    applyColorGradient(elec_prices_by_state, 'Cents_kWh', colormap='Reds')
#
##    # Add commercial electricity prices by zip code
##    elec_prices_by_zipcode = readShapefile(f'{top_dir}/data/electricity_rates_merged/electricity_rates_by_zipcode_merged.shp', 'Commercial Elec Price by Zipcode (cents / kWh)')
##    applyColorGradient(elec_prices_by_zipcode, 'comm_rate', colormap='Reds')
#
#    # Add maximum demand charges
#    demand_charges_by_utility = readShapefile(f'{top_dir}/data/electricity_rates_merged/demand_charges_merged.shp', 'Maximum Demand Charge by Utility ($/kW)')
#    applyColorGradient(demand_charges_by_utility, 'MaxDemCh', colormap='Reds')
#
    # Add and style the highway assignments
    links_all = load_highway_links(f'{top_dir}/data/highway_assignment_links/highway_assignment_links.shp', layer_name = 'Highway Flux (tons/link)')
    style_highway_links(links_all, color='black')
#
#    # Add and style the highway assignments (single unit)
#    links_single_unit = load_highway_links(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_single_unit.shp', layer_name = 'SU Highway Flux (tons/link)')
#    style_highway_links(links_single_unit, color='red')
#
#    # Add and style the highway assignments (combined unit)
#    links_combined_unit = load_highway_links(f'{top_dir}/data/highway_assignment_links/highway_assignment_links_combined_unit.shp', layer_name = 'CU Highway Flux (tons/link)')
#    style_highway_links(links_combined_unit, color='blue')
#
#    # Add alternative fueling stations for highway corridors
#    dcfc_stations = readShapefile(f'{top_dir}/data/Fuel_Corridors/US_elec/US_elec.shp', 'DCFC Corridor Stations', color='orange')
#    hydrogen_stations = readShapefile(f'{top_dir}/data/Fuel_Corridors/US_hy/US_hy.shp', 'Hydrogen Corridor Stations', color='purple')
#    hydrogen_lng = readShapefile(f'{top_dir}/data/Fuel_Corridors/US_lng/US_lng.shp', 'LNG Corridor Stations', color='green')
#    hydrogen_cng = readShapefile(f'{top_dir}/data/Fuel_Corridors/US_cng/US_cng.shp', 'CNG Corridor Stations', color='pink')
#    hydrogen_lpg = readShapefile(f'{top_dir}/data/Fuel_Corridors/US_lpg/US_lpg.shp', 'LPG Corridor Stations', color='cyan')

    # Add proposed infrastructure corridors for heavy duty trucking
    eastcoast_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/eastcoast.shp', 'Funded Corridor Project: East Coast Commercial ZEV (CALSTART)', color='orange')
    change_line_width(eastcoast_corridor, 1.0)
    midwest_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/midwest.shp', 'Funded Corridor Project: I-80 Midwest Corridor (Cummins Inc)', color='purple')
    change_line_width(midwest_corridor, 1.0)
    h2la_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/h2la.shp', 'Funded Corridor Project: Houston to Los Angeles Hydrogen Corridor Project (GTI Energy)', color='green')
    change_line_width(h2la_corridor, 1.0)
    la_i710_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/la_i710.shp', 'Funded Corridor Project: Charging Network around the I-710 Corridor (Los Angeles Cleantech Incubator)', color='pink')
    change_line_width(la_i710_corridor, 1.0)
    northeast_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/northeast.shp', 'Funded Corridor Project: Northeast Electric Highways Study (National Grid)', color='cyan')
    bayarea_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/bayarea.shp', 'Funded Corridor Project: San Francisco and Bay Area Regional Medium-and Heavy-Duty Electrification Roadmap (Rocky Mountain Institute)', color='yellow')
    saltlake_corridor = readShapefile(f'{top_dir}/data/hd_zev_corridors/saltlake.shp', 'Funded Corridor Project: Multi-Modal Corridor Electrification Plan - Greater Salt Lake City Region (Utah State University)', color='red')

#    # Get truck stop parking data
#    truck_stop_parking = readShapefile(f'{top_dir}/data/Truck_Stop_Parking/Truck_Stop_Parking.shp', 'Truck stops', color='red')
#
#    # Add hydrogen hubs
#    electrolyzer_planned = readShapefile(f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer_planned_under_construction.shp', 'Hydrogen Electrolyzer Facility Capacities [Planned or Under Construction] (kW)', color='orange')
#    electrolyzer_installed = readShapefile(f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer_installed.shp', 'Hydrogen Electrolyzer Facility Capacities [Installed] (kW)', color='yellow')
#    electrolyzer_operational = readShapefile(f'{top_dir}/data/hydrogen_hubs/shapefiles/electrolyzer_operational.shp', 'Hydrogen Electrolyzer Facility Capacities [Operational] (kW)', color='green')
#
#    applySizeGradient([electrolyzer_planned, electrolyzer_installed, electrolyzer_operational], ['orange', 'yellow', 'green'], 'Power_kW', 'circle')
#
#    refinery_SMR = readShapefile(f'{top_dir}/data/hydrogen_hubs/shapefiles/refinery.shp', 'Refinery Hydrogen Production Capacity (SMR or Byproduct) (million standar cubic feet per day)', color='purple')
#    applySizeGradient([refinery_SMR], ['purple'], 'Cap_MMSCFD', 'square')
#
#    # Get principal ports
#    principal_ports = readShapefile(f'{top_dir}/data/Principal_Ports/Principal_Port.shp', 'Principal ports', color='blue')
#
#    # Read in the circle for the default identification of facilities within a 600 mile radius
#    circle_name = 'default'
#    facilities_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/circle.shp', 'Default circle for facilities in radius', color='orange', opacity=0.25)
#
#    # Read in all truck stops and hydrogen hubs within the circle
#    truck_stops_in_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/Truck_Stop_Parking.shp', 'Truck stops in Circle', color='red')
#
#    # Add hydrogen hubs
#    electrolyzer_planned_in_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/electrolyzer_planned_under_construction.shp', 'Hydrogen Electrolyzer Facility Capacities in Circle [Planned or Under Construction] (kW)', color='orange')
#    electrolyzer_installed_in_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/electrolyzer_installed.shp', 'Hydrogen Electrolyzer Facility Capacities in Circle [Installed] (kW)', color='yellow')
#    electrolyzer_operational_in_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/electrolyzer_operational.shp', 'Hydrogen Electrolyzer Facility Capacities in Circle [Operational] (kW)', color='green')
#
#    applySizeGradient([electrolyzer_planned_in_circle, electrolyzer_installed_in_circle, electrolyzer_operational_in_circle], ['orange', 'yellow', 'green'], 'Power_kW', 'circle')
#
#    refinery_SMR_in_circle = readShapefile(f'{top_dir}/data/facilities_in_circle_{circle_name}/shapefiles/refinery.shp', 'Refinery Hydrogen Production Capacity in Circle (SMR or Byproduct) (million standar cubic feet per day)', color='purple')
#    applySizeGradient([refinery_SMR_in_circle], ['purple'], 'Cap_MMSCFD', 'square')
    
    
main()
