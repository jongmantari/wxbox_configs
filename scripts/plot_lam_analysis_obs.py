#!/usr/bin/env python3

import argparse
import yaml
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature

from matplotlib.backends.backend_pdf import PdfPages
from scipy.ndimage import zoom
from scipy.stats import gaussian_kde


# =====================================================
# INPUT
# =====================================================

parser = argparse.ArgumentParser()
parser.add_argument('--config', default='plot_c1667.yaml')
args = parser.parse_args()

with open(args.config) as f:
    cfg = yaml.safe_load(f)

analysis_file = cfg['files']['analysis']
background_file = cfg['files']['background']
obs_file = cfg['files']['obs']
grid_file = cfg['files']['grid']

level = cfg['plot']['level']
var = cfg['plot']['var']

print('Loading datasets...')

# =====================================================
# OPEN FILES
# =====================================================

ana = xr.open_dataset(analysis_file, decode_coords=False)
bkg = xr.open_dataset(background_file, decode_coords=False)
grid = xr.open_dataset(grid_file)

# =====================================================
# EXTRACT FIELDS
# =====================================================

ana_map = ana[var].data[0, level, :, :]
bkg_map = bkg[var].data[0, level, :, :]

print('analysis shape   =', ana_map.shape)
print('background shape =', bkg_map.shape)

ana_resampled = zoom(
    ana_map,
    (
        bkg_map.shape[0] / ana_map.shape[0],
        bkg_map.shape[1] / ana_map.shape[1]
    ),
    order=1
)

# =====================================================
# GRID
# =====================================================

ny, nx = bkg_map.shape
lat = grid['y'].values[:ny, :nx]
lon = grid['x'].values[:ny, :nx]
lon = np.where(lon > 180, lon - 360, lon)

if 'region' in cfg['plot']:
    extent = cfg['plot']['region']
else:
    extent = [
        float(np.nanmin(lon)) - 2,
        float(np.nanmax(lon)) + 2,
        float(np.nanmin(lat)) - 2,
        float(np.nanmax(lat)) + 2,
    ]

print('Extent =', extent)

# =====================================================
# OBS
# =====================================================

meta = xr.open_dataset(obs_file, group='MetaData', engine='netcdf4')
ombg_ds = xr.open_dataset(obs_file, group='ombg', engine='netcdf4')
oman_ds = xr.open_dataset(obs_file, group='oman', engine='netcdf4')

lat_obs = meta['latitude'].values
lon_obs = meta['longitude'].values
ombg = ombg_ds['airTemperature'].values
oman = oman_ds['airTemperature'].values

fill = -3.368795e38
mask = (
    np.isfinite(lat_obs)
    & np.isfinite(lon_obs)
    & (ombg != fill)
    & (oman != fill)
)

lat_obs = lat_obs[mask]
lon_obs = lon_obs[mask]
ombg = ombg[mask]
oman = oman[mask]


def clean(x):
    x = x[np.isfinite(x)]
    lo = np.percentile(x, 1)
    hi = np.percentile(x, 99)
    return x[(x > lo) & (x < hi)]


ombg_clean = clean(ombg)
oman_clean = clean(oman)


def setup_map():
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.3)
    return ax


def percentile_max(data):
    return np.percentile(np.abs(data[np.isfinite(data)]), 99)


def add_cbar(obj, label):
    cb = plt.colorbar(obj, orientation='horizontal', shrink=0.8, pad=0.05)
    cb.set_label(label)


pdfname = cfg['plot'].get('output_pdf', 'rrfs_3dvar_diagnostics.pdf')
print('Writing', pdfname)

with PdfPages(pdfname) as pdf:

    fig = plt.figure(figsize=(10, 7))
    ax = setup_map()
    pcm = ax.pcolormesh(lon, lat, bkg_map, shading='auto', cmap='viridis', transform=ccrs.PlateCarree())
    plt.title('Background Temperature')
    add_cbar(pcm, 'K')
    pdf.savefig(fig)
    plt.close()

    fig = plt.figure(figsize=(10, 7))
    ax = setup_map()
    pcm = ax.pcolormesh(lon, lat, ana_resampled, shading='auto', cmap='viridis', transform=ccrs.PlateCarree())
    plt.title('Analysis Temperature')
    add_cbar(pcm, 'K')
    pdf.savefig(fig)
    plt.close()

    fig = plt.figure(figsize=(10, 7))
    ax = setup_map()
    v = percentile_max(ombg)
    sc = ax.scatter(lon_obs, lat_obs, c=ombg, cmap='RdBu_r', vmin=-v, vmax=v, s=18, transform=ccrs.PlateCarree())
    plt.title('OMB (Obs - Background)')
    add_cbar(sc, 'K')
    pdf.savefig(fig)
    plt.close()

    fig = plt.figure(figsize=(10, 7))
    ax = setup_map()
    v = percentile_max(oman)
    sc = ax.scatter(lon_obs, lat_obs, c=oman, cmap='RdBu_r', vmin=-v, vmax=v, s=18, transform=ccrs.PlateCarree())
    plt.title('OMA (Obs - Analysis)')
    add_cbar(sc, 'K')
    pdf.savefig(fig)
    plt.close()

    #=========================================================================================
    # =================================================
    # OMB / OMA DENSITY
    # =================================================

    fig = plt.figure(figsize=(8, 6))

    xmin = min(
        ombg_clean.min(),
        oman_clean.min()
    )

    xmax = max(
        ombg_clean.max(),
        oman_clean.max()
    )

    bw = cfg["density"].get(
        "bandwidth",
        1.2
    )

    x = np.linspace(
        xmin,
        xmax,
        cfg["density"].get(
            "points",
            500
        )
    )

    kde_omb = gaussian_kde(
        ombg_clean,
        bw_method=bw
    )

    kde_oma = gaussian_kde(
        oman_clean,
        bw_method=bw
    )

    #
    # Density curves
    #
    plt.plot(
        x,
        kde_omb(x),
        color="blue",
        linewidth=3,
        label=f"OMB (n={len(ombg_clean)})",
    )

    plt.plot(
        x,
        kde_oma(x),
        color="red",
        linewidth=3,
        label=f"OMA (n={len(oman_clean)})",
    )

    #
    # Means
    #
    omb_mean = np.mean(
        ombg_clean
    )

    oma_mean = np.mean(
        oman_clean
    )

    plt.axvline(
        omb_mean,
        color="blue",
        linestyle="--",
        linewidth=2.5,
    )

    plt.axvline(
        oma_mean,
        color="red",
        linestyle="--",
        linewidth=2.5,
    )

    #
    # RMSE
    #
    omb_rmse = np.sqrt(
        np.mean(
            ombg_clean**2
        )
    )

    oma_rmse = np.sqrt(
        np.mean(
            oman_clean**2
        )
    )

    plt.xlabel(
        "Temperature Innovation (K)"
    )

    plt.ylabel(
        "Density"
    )

    plt.title(
        f"OMB (Blue) vs OMA (Red)\n"
        f"RMSE: {omb_rmse:.2f} → {oma_rmse:.2f} K"
    )

    plt.grid(alpha=0.3)

    plt.legend()

    pdf.savefig(fig)

    plt.close()
    #=========================================================================================

print(f'\nDONE -> {pdfname}')
