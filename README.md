# EGM722 LST Assignment

## Overview

This Python script calculates LST (Land Surface Temperature) using Landsat 8/9 satellite imagery. The script performs a full preprocessing workflow, including:

- **NDVI** (Normalised Difference Vegetation Index)
- **PVI** (Proportional Vegetation Index)
- **E_C** (Emissivity Correction)
- **TOA** (Top of Atmosphere Radiance)
- **BT** (Brightness Temperature)
- Final **LST output in degrees Celsius**

The workflow is designed for use within a Python environment that supports the `arcpy` module, that is used in ESRI's ArcGIS Pro.

---

## Workflow Diagram

![Workflow](https://github.com/user-attachments/assets/52709a2e-42bb-4c35-b070-17c3708d7ba0)

---

## Folder Setup

Ensure the following three bands are downloaded and stored in the same folder from a single Landsat 8/9 scene / AOI (Area of Interest):

- `*_SR_B4.TIF` — Band 4 (Red)
- `*_SR_B5.TIF` — Band 5 (NIR — Near Infrared)
- `*_ST_B10.TIF` — Band 10 (Thermal Infrared)

The script automatically detects these files based on filename patterns. All other bands can remain in the folder.

---

## Environment Setup

A sample `environment.yml` file is included in the repository to help recreate the necessary Python environment using Conda. It includes:

- `numpy`
- `rasterio`
- `matplotlib`

To create the environment (excluding `arcpy`), run:

``` conda env create -f environment.yml conda activate lst_env ```

---

### Important Note on `arcpy`

This script requires the **`arcpy`** module, which is only available through an ArcGIS Pro installation.

- `arcpy` **cannot be installed using `conda` or `pip`**
- You must run the script from within the **ArcGIS Pro Python environment** (typically `arcgispro-py3`)

#### To run the script successfully:
- Use the **ArcGIS Pro Python Command Prompt**
- Or use an environment where `arcpy` is already available

Users without access to ArcGIS Pro will **not** be able to execute the script.

---

## Running the Script

After activating the correct environment, run the script:

``` python lst_script.py ```

You will be prompted to enter the full path to your Landsat imagery folder.

---

## Output Files

Output rasters are saved in a subfolder called `Output` which will sit inside your downloaded Landsat 8 or 9 folder:

- `NDVI.tif` — Normalised Difference Vegetation Index
- `PVI.tif` — Proportional Vegetation Index
- `Emissivity.tif` — Land Surface Emissivity
- `TOA_Radiance.tif` — Top of Atmosphere Radiance
- `BT.tif` — Brightness Temperature
- `LST_Celsius.tif` — Final Land Surface Temperature in Celsius

---

## Troubleshooting

| Issue                                           | Solution                                                      |
|------------------------------------------------|---------------------------------------------------------------|
| `ModuleNotFoundError: No module named 'arcpy'` | Run the script using ArcGIS Pro’s Python Command Prompt       |
| `One or more bands not found`                  | Ensure correct filenames: *_SR_B4.TIF, *_SR_B5.TIF, *_ST_B10.TIF |
| `PermissionError when saving rasters`          | Close the output folder in File Explorer and re-run the script |
| `Raster minimum/maximum not detected`          | ArcPy will automatically calculate statistics if needed       |

---

## Test Data

Landsat 8/9 imagery can be downloaded for free from:

📎 [USGS EarthExplorer](https://earthexplorer.usgs.gov/)

New users will be required to create a new account on the USGS explorer website.
A guide on this can be found on **youtube**
Use a recent Level-2 Landsat Collection 2 scene to ensure correct band formats.

---

## Version Control Notes

This repository includes a development branch (`dev`) where iterative changes and feature testing were carried out before merging into the main branch. This was done to test version control.

---

## Notes

This repository was developed as part of the EGM722 MSc assessment on Land Surface Temperature (LST) analysis using Landsat 8/9 data. A supporting how-to guide was submitted separately via the Ulster university portal.

Branches were used during development (`dev` branch) and merged into `main` for final submission.

---

## Author

**Mr Tobias Fish**  
Student ID: B01008855  
University of Ulster  
**EGM722 — Programming for GIS and Remote Sensing**
**For Academic use only**
