# EGM722 LST Assignment

## Overview
This Python script calculates Land Surface Temperature (LST) using Landsat 8/9 satellite imagery. It performs a full preprocessing workflow including NDVI (Normalised Difference Vegetation Index), PVI (Proportional Vegetation Index), E_C (Emissivity Correction), TOA (Top of Atmosphere) Radiance, BT (Brightness Temperature), and the final LST output in Celsius.

## Folder Setup
Ensure the following bands are present in the downloaded Landsat folder:
- Band 4: B4.TIF (Red)
- Band 5: B5.TIF (NIR (Near Infra-red))
- Band 10: B10.TIF (TIR (Thermal Infrared))

## Environment Setup
A sample `environment.yml` is provided for reproducibility, containing the required open-source packages:
- `numpy`
- `rasterio`
- `matplotlib`

### Note on `arcpy`
This script requires the `arcpy` module to access raster statistics.  
`arcpy` **cannot be installed using conda or pip** — it is only available via an ArcGIS Pro installation.  
To run this script successfully:

- Use the **ArcGIS Pro Python Command Prompt**
- Or use a Conda environment where `arcpy` is already available (e.g. the default `arcgispro-py3`)

Users without ArcGIS Pro will not be able to execute the script due to this dependency.

To create the environment without `arcpy`, run:

conda env create -f environment.yml conda activate lst_env

## Running the Script
After activating the correct environment, run the script:

python lst_script.py


You will be prompted to enter the full path to the folder containing your Landsat bands.

## Outputs
Output rasters will be saved in a new subfolder called `Output` inside your Landsat folder:
- `NDVI.tif`
- `PVI.tif`
- `Emissivity.tif`
- `TOA_Radiance.tif`
- `BT.tif` (Brightness Temperature)
- `LST_Celsius.tif`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'arcpy'` | Run from ArcGIS Pro’s Python Command Prompt |
| `One or more bands not found` | Check that the correct band filenames are in the folder |
| `PermissionError when saving rasters` | Close the folder in File Explorer and re-run the script |

## Test Data
Landsat 8/9 imagery can be downloaded from [USGS EarthExplorer](https://earthexplorer.usgs.gov/)

## Author
Mr Tobias Fish 
B01008855
University of Ulster 
EGM722 Programming for GIS and Remote Sensing
