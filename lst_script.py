import arcpy
import rasterio
import numpy as np
import os
import glob  # Used for file searching

# ---- User Input for File Path ----
data_folder = input("Enter the folder path containing your Landsat imagery: ").strip()

# Validate input
if not os.path.exists(data_folder):
    raise FileNotFoundError(f"Error: The specified folder '{data_folder}' does not exist.")

# Set output folder inside the same directory
output_folder = os.path.join(data_folder, "Output")
os.makedirs(output_folder, exist_ok=True)

print(f"Using Landsat imagery from: {data_folder}")
print(f"Output files will be saved in: {output_folder}")

# ---- Auto-Detect Landsat Files ----
def find_band(pattern):
    """Finds the file matching a given Landsat band pattern."""
    files = glob.glob(os.path.join(data_folder, pattern))
    return files[0] if files else None

band_4 = find_band("*_SR_B4.TIF")  # Searches for Band 4 (Red)
band_5 = find_band("*_SR_B5.TIF")  # Searches for Band 5 (NIR)
band_10 = find_band("*_ST_B10.TIF")  # Searches for Band 10 (Thermal)

# Ensure all required bands are found
if not band_4 or not band_5 or not band_10:
    raise FileNotFoundError("Error: One or more required Landsat bands (B4, B5, B10) were not found in the folder.")

print(f"Detected Band 4: {band_4}")
print(f"Detected Band 5: {band_5}")
print(f"Detected Band 10: {band_10}")

# ---- Utility Functions ----

def read_raster(file_path):
    """Reads a raster file using Rasterio."""
    with rasterio.open(file_path) as src:
        array = src.read(1).astype(float)
        profile = src.profile
    return array, profile

def save_raster(output_path, array, profile):
    """Saves a NumPy array as a raster file using Rasterio, ensuring old files are removed."""
    if os.path.exists(output_path):
        os.remove(output_path)  # Delete existing file to prevent permission issues

    profile.update(dtype=rasterio.float32)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(array.astype(np.float32), 1)

# ---- DN Correction ----

def get_arcgis_min_max(file_path):
    """Retrieves the minimum and maximum DN values from ArcGIS Pro using ArcPy, ensuring statistics exist."""
    raster = arcpy.Raster(file_path)

    # Ensure statistics exist before reading min/max values
    if raster.minimum is None or raster.maximum is None:
        print(f"Statistics missing for {file_path}. Calculating in ArcGIS...")
        arcpy.management.CalculateStatistics(file_path)
        raster = arcpy.Raster(file_path)  # Reload raster after stats calculation

    return raster.minimum, raster.maximum

def correct_DN_values(Q_cal, min_DN_arcpy):
    """Ensures DN values match ArcPro's range by shifting only values below 29037."""
    Q_cal = np.copy(Q_cal)  
    mask = Q_cal < min_DN_arcpy  
    Q_cal[mask] += (min_DN_arcpy - Q_cal[mask])  
    return Q_cal  

# ---- TOA Radiance Calculation ----

def compute_TOA_radiance(Q_cal, rad_mult, rad_add):
    """Computes TOA Radiance from DN values."""
    return (rad_mult * Q_cal) + rad_add

# ---- Brightness Temperature Calculation ----

def compute_BT(toa_radiance, k1, k2):
    """Computes Brightness Temperature (BT) from TOA Radiance."""
    return k2 / (np.log((k1 / toa_radiance) + 1))

# ---- NDVI Calculation ----

def compute_NDVI(nir_array, red_array):
    """Computes NDVI using the formula: (NIR - Red) / (NIR + Red)."""
    np.seterr(divide='ignore', invalid='ignore')  
    ndvi = (nir_array - red_array) / (nir_array + red_array)
    return np.nan_to_num(ndvi)  

# ---- PVI Calculation ----

def compute_PVI(ndvi_array):
    """Computes the Proportional Vegetation Index (PVI)."""
    ndvi_min = ndvi_array.min()  
    ndvi_max = ndvi_array.max()  
    return np.square((ndvi_array - ndvi_min) / (ndvi_max - ndvi_min))  

# ---- Emissivity Calculation ----

def compute_emissivity(pvi_array, ndvi_array):
    """Computes Land Surface Emissivity (ε), adjusting for water areas."""
    emissivity = (0.0038 * pvi_array) + 0.985  # Standard emissivity scaling
    
    # Ensure emissivity stays within realistic bounds
    emissivity[emissivity > 0.99] = 0.99  
    emissivity[emissivity < 0.986] = 0.986  
    
    # Identify water pixels using NDVI (NDVI < 0 = water)
    water_mask = ndvi_array < 0  
    
    # Apply water emissivity correction (~0.992)
    emissivity[water_mask] = 0.992  
    
    return emissivity

# ---- Land Surface Temperature (LST) Calculation ----

def compute_LST(bt_array, emissivity_array, wavelength=10.895, c2=1.4388e4):
    """
    Computes Land Surface Temperature (LST) from Brightness Temperature (BT) and Emissivity (EC).
    Formula: LST = BT / (1 + (λ * BT / c2) * ln(ε))
    """
    return bt_array / (1 + (wavelength * bt_array / c2) * np.log(emissivity_array))

import glob

# ---- Auto-Detect Landsat Files ----
def find_band(pattern):
    """Finds the file matching a given Landsat band pattern."""
    files = glob.glob(os.path.join(data_folder, pattern))
    return files[0] if files else None

band_4 = find_band("*_SR_B4.TIF")  # Searches for Band 4 (Red)
band_5 = find_band("*_SR_B5.TIF")  # Searches for Band 5 (NIR)
band_10 = find_band("*_ST_B10.TIF")  # Searches for Band 10 (Thermal)

# Ensure all required bands are found
if not band_4 or not band_5 or not band_10:
    raise FileNotFoundError("Error: One or more required Landsat bands (B4, B5, B10) were not found in the folder.")


# Output files
ndvi_output = os.path.join(output_folder, "NDVI.tif")
toa_output = os.path.join(output_folder, "TOA_Radiance.tif")
bt_output = os.path.join(output_folder, "BT.tif")
pvi_output = os.path.join(output_folder, "PVI.tif")
emissivity_output = os.path.join(output_folder, "Emissivity.tif")
lst_output = os.path.join(output_folder, "LST.tif")
lst_celsius_output = os.path.join(output_folder, "LST_Celsius.tif")

os.makedirs(output_folder, exist_ok=True)  

# ---- Step 1: Compute NDVI ----
nir_array, profile = read_raster(band_5)  
red_array, _ = read_raster(band_4)  
ndvi_array = compute_NDVI(nir_array, red_array)
save_raster(ndvi_output, ndvi_array, profile)  
print(f"NDVI Min: {ndvi_array.min()} | Expected: ~-1")
print(f"NDVI Max: {ndvi_array.max()} | Expected: ~1")

# ---- Step 2: Compute TOA Radiance ----
min_DN_arcpy, max_DN_arcpy = get_arcgis_min_max(band_10)
print(f"ArcGIS Pro Band 10 Min DN: {min_DN_arcpy}, Max DN: {max_DN_arcpy}")  # Debugging Print

Q_cal, profile = read_raster(band_10)
Q_cal = correct_DN_values(Q_cal, min_DN_arcpy)

# Print Band 10 DN values
print(f"Band 10 DN Values: Min={Q_cal.min()} | Max={Q_cal.max()}")

Q_cal = correct_DN_values(Q_cal, min_DN_arcpy)
Q_cal = correct_DN_values(Q_cal, min_DN_arcpy)

# Compute TOA Radiance
TOA_radiance = compute_TOA_radiance(Q_cal, 0.0003342, 0.08000)
save_raster(toa_output, TOA_radiance, profile)
print(f"TOA Radiance Min: {TOA_radiance.min()} | Expected: ~9.5")
print(f"TOA Radiance Max: {TOA_radiance.max()} | Expected: ~17.5")

# ---- Step 3: Compute Brightness Temperature ----
BT_array = compute_BT(TOA_radiance, 774.8853, 1321.0789)
save_raster(bt_output, BT_array, profile)
print(f"BT Min Before LST: {BT_array.min()}K | Expected: ~250K")
print(f"BT Max Before LST: {BT_array.max()}K | Expected: ~350K")

# ---- Step 4: Compute PVI ----
pvi_array = compute_PVI(ndvi_array)
save_raster(pvi_output, pvi_array, profile)

# ---- Step 5: Compute Emissivity (Now Accounts for Water Areas) ----
emissivity_array = compute_emissivity(pvi_array, ndvi_array)
save_raster(emissivity_output, emissivity_array, profile)
print(f"Emissivity Min: {emissivity_array.min()} | Expected: ~0.986")
print(f"Emissivity Max: {emissivity_array.max()} | Expected: ~0.990")

# ---- Step 6: Compute Land Surface Temperature (LST) ----
lst_array = compute_LST(BT_array, emissivity_array)
lst_array_celsius = lst_array - 273.15
save_raster(lst_celsius_output, lst_array_celsius, profile)
print(f"LST Min: {lst_array_celsius.min()}C | Expected: ~7C")
print(f"LST Max: {lst_array_celsius.max()}C | Expected: ~77C")

print("\nAll steps completed successfully!")
