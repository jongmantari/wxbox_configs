#!/usr/bin/env python3

import yaml
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import gaussian_kde

# ================================
# CONFIG
# ================================
with open("plot_config.yaml") as f:
    cfg = yaml.safe_load(f)

analysis_file = cfg["files"]["analysis"]
bkg_file = cfg["files"]["background"]
obs_file = cfg["files"]["obs"]
grid_file = cfg["files"]["grid"]

extent = cfg["plot"]["region"]
level = cfg["plot"]["level"]
var = cfg["plot"]["var"]

print("Loading datasets...")

# ================================
# LOAD DATA
# ================================
ana = xr.open_dataset(analysis_file, decode_coords=False)
bkg = xr.open_dataset(bkg_file, decode_coords=False)
grid = xr.open_dataset(grid_file)

ana_map = ana[var].data[0, level, :, :]
bkg_map = bkg[var].data[0, level, :, :]
inc_map = ana[var].data[0, level] - bkg[var].data[0, level]

# ================================
# FV3 GRID FIX (SUPERGRID → CENTER)
# ================================
lat_full = grid["y"].values
lon_full = grid["x"].values

lat_center = 0.25 * (
    lat_full[0:-1:2, 0:-1:2] +
    lat_full[1::2, 0:-1:2] +
    lat_full[0:-1:2, 1::2] +
    lat_full[1::2, 1::2]
)

lon_center = 0.25 * (
    lon_full[0:-1:2, 0:-1:2] +
    lon_full[1::2, 0:-1:2] +
    lon_full[0:-1:2, 1::2] +
    lon_full[1::2, 1::2]
)

ny, nx = inc_map.shape
lat = lat_center[:ny, :nx]
lon = lon_center[:ny, :nx]

# ================================
# LOAD OBS
# ================================
print("Loading observations...")

meta = xr.open_dataset(obs_file, group="MetaData", engine="netcdf4")
ombg_ds = xr.open_dataset(obs_file, group="ombg", engine="netcdf4")
oman_ds = xr.open_dataset(obs_file, group="oman", engine="netcdf4")

lat_obs = meta["latitude"].values
lon_obs = meta["longitude"].values
ombg = ombg_ds["airTemperature"].values
oman = oman_ds["airTemperature"].values

fill = -3.368795e+38

mask = (
    (ombg != fill)
    & (oman != fill)
    & np.isfinite(lat_obs)
)

lat_obs = lat_obs[mask]
lon_obs = lon_obs[mask]
ombg = ombg[mask]
oman = oman[mask]

# ================================
# CLEAN FOR KDE
# ================================
def clean(x):
    x = x[np.isfinite(x)]
    return x[(x > np.percentile(x, 1)) &
             (x < np.percentile(x, 99))]

ombg_c = clean(ombg)
oman_c = clean(oman)

# ================================
# HELPERS
# ================================
def setup_map():
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linestyle=":", linewidth=0.6)
    return ax

def vmax(data):
    return np.percentile(np.abs(data[np.isfinite(data)]), 99)

def colorbar_slim(mappable, label):
    cbar = plt.colorbar(
        mappable,
        orientation="horizontal",
        pad=0.06,
        fraction=0.035,
        shrink=0.8,
        aspect=40
    )
    cbar.set_label(label, fontsize=10)
    cbar.ax.tick_params(labelsize=8)

# ================================
# PDF OUTPUT
# ================================
print("Saving PDF → rrfs_3dvar_diagnostics.pdf")

with PdfPages("rrfs_3dvar_diagnostics.pdf") as pdf:

    # ============================
    # 1. BACKGROUND FIELD ✅
    # ============================
    fig = plt.figure(figsize=(8,6))
    ax = setup_map()

    pcm = ax.pcolormesh(
        lon, lat, bkg_map,
        cmap="viridis",
        shading="auto",
        transform=ccrs.PlateCarree()
    )

    plt.title("Background Temperature", fontsize=14)
    colorbar_slim(pcm, "K")

    pdf.savefig(fig)
    plt.close()

    # ============================
    # 2. INCREMENT (ZOOMED ✅)
    # ============================
    fig = plt.figure(figsize=(8,6))
    ax = setup_map()

    v = vmax(inc_map)

    pcm = ax.pcolormesh(
        lon, lat, inc_map,
        cmap="RdBu_r",
        vmin=-v, vmax=v,
        shading="auto",
        transform=ccrs.PlateCarree()
    )

    plt.title("Temperature Increment", fontsize=14)
    colorbar_slim(pcm, "K")

    pdf.savefig(fig)
    plt.close()

    # ============================
    # 3. OMB
    # ============================
    fig = plt.figure(figsize=(8,6))
    ax = setup_map()

    v = vmax(ombg)

    sc = ax.scatter(
        lon_obs, lat_obs,
        c=ombg,
        cmap="coolwarm",
        vmin=-v, vmax=v,
        s=12,
        transform=ccrs.PlateCarree()
    )

    plt.title("OMB (Obs - Background)", fontsize=14)
    colorbar_slim(sc, "K")

    pdf.savefig(fig)
    plt.close()

    # ============================
    # 4. OMA
    # ============================
    fig = plt.figure(figsize=(8,6))
    ax = setup_map()

    v = vmax(oman)

    sc = ax.scatter(
        lon_obs, lat_obs,
        c=oman,
        cmap="coolwarm",
        vmin=-v, vmax=v,
        s=12,
        transform=ccrs.PlateCarree()
    )

    plt.title("OMA (Obs - Analysis)", fontsize=14)
    colorbar_slim(sc, "K")

    pdf.savefig(fig)
    plt.close()

    # ============================
    # 5. SMOOTH KDE ✅
    # ============================
    fig = plt.figure(figsize=(8,6))

    kde_omb = gaussian_kde(ombg_c)
    kde_oma = gaussian_kde(oman_c)

    x = np.linspace(min(ombg_c.min(), oman_c.min()),
                    max(ombg_c.max(), oman_c.max()), 400)

    plt.plot(x, kde_omb(x), color="blue", linewidth=2.5, label="OMB")
    plt.plot(x, kde_oma(x), color="red", linewidth=2.5, label="OMA")

    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.title("OMB vs OMA Distribution")

    plt.legend()
    plt.grid(alpha=0.3)

    pdf.savefig(fig)
    plt.close()

print("✅ DONE — clean, zoomed, production plots")
