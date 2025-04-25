import pandas as pd
import ee  # Ensure Earth Engine API is initialized in your environment
#from tabulate import tabulate  # Import for displaying tables in a formatted way

def calculate_no_planting_area_for_state(geometry, no_planting_data, year):
    # Calculate pixel area in square meters for the no planting area mask
    pixel_area = ee.Image.pixelArea()
    no_planting_area = no_planting_data.multiply(pixel_area)
    
    # Dynamically format the band name using the year argument
    band_name = f'EVI_Z_Score_{year}'

    # Reduce the region to calculate the sum of pixel areas for the feature's geometry
    area_reduction = no_planting_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=1500,
        tileScale=16  # Adjust tileScale if needed for large areas
    )
    
    # Extract the area in square meters and convert it to hectares
    area_ha = ee.Number(area_reduction.get(band_name)).divide(10000).getInfo()
    
    return area_ha

def calculate_total_cropland_area_for_state(geometry, evi_data):
    # Calculate pixel area in square meters for the cropland mask
    pixel_area = ee.Image.pixelArea()
    cropland_area = evi_data.gt(0).multiply(pixel_area)
    
    # Reduce the region to calculate the sum of pixel areas for the feature's geometry
    area_reduction = cropland_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=2000,
        tileScale=16  # Adjust tileScale if needed for large areas
    )
    
    # Extract the area in square meters and convert it to hectares
    area_ha = ee.Number(area_reduction.get('EVI')).divide(10000).getInfo()
    
    return area_ha

def process_sdn_adm1(sdn_adm1, no_planting_data, evi_data, year):
    # Iterate over each row in the GeoDataFrame and calculate the no-planting and total cropland areas
    no_planting_areas = []
    total_cropland_areas = []
    percent_no_planting = []
    year = year

    for index, row in sdn_adm1.iterrows():
        # Get the geometry from the GeoDataFrame
        geometry = ee.Geometry(row['geometry'].__geo_interface__)
        
        # Calculate the no-planting area for this geometry
        no_planting_area_ha = calculate_no_planting_area_for_state(geometry, no_planting_data, year)
        total_cropland_area_ha = calculate_total_cropland_area_for_state(geometry, evi_data)
        
        # Calculate the percentage of no-planting area out of total cropland area
        if total_cropland_area_ha > 0:
            percent_no_planting_area = (no_planting_area_ha / total_cropland_area_ha) * 100
        else:
            percent_no_planting_area = None  # Handle division by zero if no cropland area
        
        # Append the results to the lists
        no_planting_areas.append(no_planting_area_ha)
        total_cropland_areas.append(total_cropland_area_ha)
        percent_no_planting.append(percent_no_planting_area)

    # Add the calculated areas and percentages to the GeoDataFrame
    sdn_adm1['No_Planting_Area_ha'] = no_planting_areas
    sdn_adm1['Total_Cropland_Area_ha'] = total_cropland_areas
    sdn_adm1['Percent_No_Planting'] = percent_no_planting

    # Round the numeric columns
    sdn_adm1['No_Planting_Area_ha'] = sdn_adm1['No_Planting_Area_ha'].round(2)
    sdn_adm1['Total_Cropland_Area_ha'] = sdn_adm1['Total_Cropland_Area_ha'].round(2)
    sdn_adm1['Percent_No_Planting'] = sdn_adm1['Percent_No_Planting'].round(2)

    #print(sdn_adm1[['State_En', 'No_Planting_Area_ha', 'Total_Cropland_Area_ha', 'Percent_No_Planting']].to_string(index=False))

    return sdn_adm1


    '''# Display the updated GeoDataFrame as a formatted table
    table = tabulate(sdn_adm1[['State_En', 'No_Planting_Area_ha', 'Total_Cropland_Area_ha', 'Percent_No_Planting']], 
        headers='keys', 
        tablefmt='fancy_grid'
    )
    print(table)    

    return sdn_adm1'''