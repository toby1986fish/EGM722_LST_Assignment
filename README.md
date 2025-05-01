# EGM722 LST Assignment

## Overview
This script calculates Land Surface Temperature (LST) from Landsat 8/9 satellite imagery using Python. It includes NDVI, TOA (Top of Atmosphere), PVI (Portional Vegetation Index), E_C (Emissivity Correction), and outputs a final LST raster in Celsius.

## Folder Setup
- Place all downloaded Landsat 8 bands in a single folder.
- Required bands:
  - Band 4: B4.TIF
  - Band 5: B5.TIF
  - Band 10: B10.TIF

Please note, keep all the bands within the folder, even if they are not used. 

## Environment Setup
Use the provided `environment.yml` file to create your Conda environment:

conda env create -f environment.yml  
conda activate lst_env

## Python Script
Ensure all the required python libraries are installed prior to running the script.
- numpy	
- rasterio	
- glob	
- os	
- arcpy	

## Running the Script
Run the script from within your new environment. When prompted, enter the `folder path` containing the Landsat imagery.

python lst_script.py

## Outputs
All output rasters will be saved in a new `Output` folder inside your Landsat folder:
- NDVI.tif
- TOA_Radiance.tif
- BT.tif (Brightness Temperature)
- PVI.tif
- Emissivity.tif
- LST_Celsius.tif

## Test Data
Use USGS EarthExplorer: https://earthexplorer.usgs.gov/
The script will run with Landsat 8 and Landsat 9 data

## Author
Mr Tobias Fish EGM722
