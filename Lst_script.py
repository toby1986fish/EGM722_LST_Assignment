import arcpy
import rasterio
import numpy as np
import os
import glob2

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

band_4 = find_band("*_SR_B4.TIF")  # Red
band_5 = find_band("*_SR_B5.TIF")  # NIR
band_10 = find_band("*_ST_B10.TIF")  # Thermal

if not band_4 or not band_5 or not band_10:
    raise FileNotFoundError("Error: One or more required Landsat bands (B4, B5, B10) were not found.")

print(f"Detected Band 4: {band_4}")
print(f"Detected Band 5: {band_5}")
print(f"Detected Band 10: {band_10}")

# ---- Utility Functions ----
def read_raster(file_path):
    with rasterio.open(file_path) as src:
        array = src.read(1).astype(float)
        profile = src.profile
    return array, profile

def save_raster(output_path, array, profile):
    if os.path.exists(output_path):
        os.remove(output_path)
    profile.update(dtype=rasterio.float32)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(array.astype(np.float32), 1)

def get_arcgis_min_max(file_path):
    raster = arcpy.Raster(file_path)
    if raster.minimum is None or raster.maximum is None:
        print(f"Statistics missing for {file_path}. Calculating in ArcGIS...")
        arcpy.management.CalculateStatistics(file_path)
        raster = arcpy.Raster(file_path)
    return raster.minimum, raster.maximum

def correct_DN_values(Q_cal, min_DN_arcpy):
    Q_cal = np.copy(Q_cal)
    Q_cal[Q_cal < min_DN_arcpy] += (min_DN_arcpy - Q_cal[Q_cal < min_DN_arcpy])
    return Q_cal

def compute_TOA_radiance(Q_cal, rad_mult, rad_add):
    return (rad_mult * Q_cal) + rad_add

def compute_BT(toa_radiance, k1, k2):
    return k2 / (np.log((k1 / toa_radiance) + 1))

def compute_NDVI(nir_array, red_array):
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = (nir_array - red_array) / (nir_array + red_array)
    return np.nan_to_num(ndvi)

def compute_PVI(ndvi_array):
    ndvi_min = ndvi_array.min()
    ndvi_max = ndvi_array.max()
    return np.square((ndvi_array - ndvi_min) / (ndvi_max - ndvi_min))

def compute_emissivity(pvi_array, ndvi_array):
    emissivity = (0.0038 * pvi_array) + 0.985
    emissivity = np.clip(emissivity, 0.986, 0.99)
    water_mask = ndvi_array < 0
    emissivity[water_mask] = 0.992
    return emissivity

def compute_LST(bt_array, emissivity_array, wavelength=10.895, c2=1.4388e4):
    return bt_array / (1 + (wavelength * bt_array / c2) * np.log(emissivity_array))

# ---- Output File Paths ----
ndvi_output = os.path.join(output_folder, "NDVI.tif")
toa_output = os.path.join(output_folder, "TOA_Radiance.tif")
bt_output = os.path.join(output_folder, "BT.tif")
pvi_output = os.path.join(output_folder, "PVI.tif")
emissivity_output = os.path.join(output_folder, "Emissivity.tif")
lst_output = os.path.join(output_folder, "LST.tif")
lst_celsius_output = os.path.join(output_folder, "LST_Celsius.tif")

# ---- Step 1: NDVI ----
nir_array, profile = read_raster(band_5)
red_array, _ = read_raster(band_4)
ndvi_array = compute_NDVI(nir_array, red_array)
save_raster(ndvi_output, ndvi_array, profile)
print(f"NDVI Min: {ndvi_array.min():.4f} | Max: {ndvi_array.max():.4f}")

# ---- Step 2: TOA Radiance ----
min_DN_arcpy, _ = get_arcgis_min_max(band_10)
Q_cal, profile = read_raster(band_10)
Q_cal = correct_DN_values(Q_cal, min_DN_arcpy)
TOA_radiance = compute_TOA_radiance(Q_cal, 0.0003342, 0.08000)
save_raster(toa_output, TOA_radiance, profile)
print(f"TOA Radiance Min: {TOA_radiance.min():.4f} | Max: {TOA_radiance.max():.4f}")

# ---- Step 3: Brightness Temperature ----
BT_array = compute_BT(TOA_radiance, 774.8853, 1321.0789)
save_raster(bt_output, BT_array, profile)
print(f"BT Min: {BT_array.min():.2f}K | Max: {BT_array.max():.2f}K")

# ---- Step 4: PVI ----
pvi_array = compute_PVI(ndvi_array)
save_raster(pvi_output, pvi_array, profile)

# ---- Step 5: Emissivity ----
emissivity_array = compute_emissivity(pvi_array, ndvi_array)
save_raster(emissivity_output, emissivity_array, profile)
print(f"Emissivity Min: {emissivity_array.min():.4f} | Max: {emissivity_array.max():.4f}")

# ---- Step 6: LST ----
lst_array = compute_LST(BT_array, emissivity_array)
lst_array_celsius = lst_array - 273.15
save_raster(lst_celsius_output, lst_array_celsius, profile)
print(f"LST Min: {lst_array_celsius.min():.2f}°C | Max: {lst_array_celsius.max():.2f}°C")

print("\nAll steps completed successfully!")
