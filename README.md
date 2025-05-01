# EGM722_LST_Assignment
Land Surface Temperature Calculation (LST) using Landsat MSI &amp; Python (EGM722 MSc Assignment)

## Overview
This script calculates Land Surface Temperature (LST) from Landsat 8 satellite imagery using Python. It includes NDVI, PVI, emissivity correction (accounting for water), and outputs a final LST raster in Celsius.

## Folder Setup
- Place all downloaded Landsat 8 bands in a single folder.
- Required bands:
  - Band 4: *_SR_B4.TIF
  - Band 5: *_SR_B5.TIF
  - Band 10: *_ST_B10.TIF

## Environment Setup
Use the provided `environment.yml` file to create your Conda environment:

```bash
conda env create -f environment.yml
conda activate lst_env
