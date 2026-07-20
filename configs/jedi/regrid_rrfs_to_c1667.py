#!/usr/bin/env python3

import os
import numpy as np
import xarray as xr

from scipy.interpolate import griddata

# =====================================================
# INPUTS
# =====================================================

SRC_GRID = (
    "Data/inputs/lam_rrfs/INPUT/C403_grid.tile7.halo3.nc"
)

SRC_CORE = (
    "Data/inputs/lam_rrfs/bkg/"
    "20201215.000000.rrfs_C403.fv_core.res.tile1.nc"
)

SRC_TRCR = (
    "Data/inputs/lam_rrfs/bkg/"
    "20201215.000000.rrfs_C403.fv_tracer.res.tile1.nc"
)

TGT_GRID = (
    "/home/jonggyunkim/grids/"
    "esg.regional_west3km/C1667/"
    "C1667_grid.tile7.halo3.nc"
)

OUTDIR = "Data/inputs/lam_c1667/bkg"

OUT_CORE = (
    f"{OUTDIR}/"
    "20201215.000000.rrfs_C1667.fv_core.res.tile1.nc"
)

OUT_TRCR = (
    f"{OUTDIR}/"
    "20201215.000000.rrfs_C1667.fv_tracer.res.tile1.nc"
)

# =====================================================
# CREATE OUTPUT DIRECTORY
# =====================================================

os.makedirs(OUTDIR, exist_ok=True)

# =====================================================
# FV3 SUPERGRID -> CELL CENTER
# =====================================================

def cell_center(arr):

    return 0.25 * (
        arr[:-1:2, :-1:2]
        + arr[1::2, :-1:2]
        + arr[:-1:2, 1::2]
        + arr[1::2, 1::2]
    )

# =====================================================
# READ GRIDS
# =====================================================

print("Reading grids...")

gsrc = xr.open_dataset(SRC_GRID)
gtgt = xr.open_dataset(TGT_GRID)

lon_src_cc = cell_center(gsrc["x"].values)
lat_src_cc = cell_center(gsrc["y"].values)

lon_tgt_cc = cell_center(gtgt["x"].values)
lat_tgt_cc = cell_center(gtgt["y"].values)

lon_diag = np.where(
    lon_tgt_cc > 180,
    lon_tgt_cc - 360,
    lon_tgt_cc
)

print()
print("Target domain")
print("Lon:", lon_diag.min(), lon_diag.max())
print("Lat:", lat_tgt_cc.min(), lat_tgt_cc.max())

# =====================================================
# READ SOURCE FILES
# =====================================================

core = xr.open_dataset(SRC_CORE)
trcr = xr.open_dataset(SRC_TRCR)

print()
print("Source dimensions")
print("T  :", core["T"][0,0].shape)
print("ua :", core["ua"][0,0].shape)
print("va :", core["va"][0,0].shape)

# =====================================================
# BUILD SOURCE COORDS
# =====================================================

nyT, nxT = core["T"][0,0].shape

lon_T = lon_src_cc[:nyT, :nxT]
lat_T = lat_src_cc[:nyT, :nxT]

pts_T = np.column_stack([
    lon_T.ravel(),
    lat_T.ravel()
])

nyU, nxU = core["ua"][0,0].shape

lon_U = lon_src_cc[:nyU, :nxU]
lat_U = lat_src_cc[:nyU, :nxU]

pts_U = np.column_stack([
    lon_U.ravel(),
    lat_U.ravel()
])

nyV, nxV = core["va"][0,0].shape

lon_V = lon_src_cc[:nyV, :nxV]
lat_V = lat_src_cc[:nyV, :nxV]

pts_V = np.column_stack([
    lon_V.ravel(),
    lat_V.ravel()
])

# =====================================================
# TARGET COORDS
# =====================================================

pts_tgt = np.column_stack([
    lon_tgt_cc.ravel(),
    lat_tgt_cc.ravel()
])

ny_new, nx_new = lon_tgt_cc.shape

print()
print("Target FV3 dimensions")
print("ny =", ny_new)
print("nx =", nx_new)

# =====================================================
# INTERPOLATION
# =====================================================

def interp_field(field, pts_src):

    vals = field.ravel()

    out = griddata(
        pts_src,
        vals,
        pts_tgt,
        method="linear"
    )

    bad = np.isnan(out)

    if np.any(bad):

        out[bad] = griddata(
            pts_src,
            vals,
            pts_tgt[bad],
            method="nearest"
        )

    return out.reshape(
        ny_new,
        nx_new
    )

# =====================================================
# FV_CORE
# =====================================================

print()
print("Interpolating fv_core...")

nz = core.sizes["zaxis_1"]

T_new = np.zeros(
    (1, nz, ny_new, nx_new),
    dtype=np.float32
)

DELP_new = np.zeros_like(T_new)
ua_new   = np.zeros_like(T_new)
va_new   = np.zeros_like(T_new)

for k in range(nz):

    print(f"Level {k+1:02d}/{nz}")

    T_new[0,k] = interp_field(
        core["T"][0,k].values,
        pts_T
    )

    DELP_new[0,k] = interp_field(
        core["DELP"][0,k].values,
        pts_T
    )

    ua_new[0,k] = interp_field(
        core["ua"][0,k].values,
        pts_U
    )

    va_new[0,k] = interp_field(
        core["va"][0,k].values,
        pts_V
    )

print("Interpolating phis...")

phis_new = interp_field(
    core["phis"][0,0].values,
    pts_T
)

core_out = xr.Dataset()

core_out["T"] = (
    ("Time","zaxis_1","yaxis_2","xaxis_1"),
    T_new
)

core_out["DELP"] = (
    ("Time","zaxis_1","yaxis_2","xaxis_1"),
    DELP_new
)

core_out["ua"] = (
    ("Time","zaxis_1","yaxis_1","xaxis_1"),
    ua_new
)

core_out["va"] = (
    ("Time","zaxis_1","yaxis_1","xaxis_1"),
    va_new
)

core_out["phis"] = (
    ("Time","zaxis_2","yaxis_2","xaxis_1"),
    phis_new[np.newaxis,np.newaxis,:,:]
)

print()
print("Writing:")
print(OUT_CORE)

core_out.to_netcdf(OUT_CORE)

# =====================================================
# FV_TRACER
# =====================================================

print()
print("Interpolating tracers...")

trcr_out = xr.Dataset()

for var in trcr.data_vars:

    data = trcr[var]

    if len(data.dims) != 4:
        continue

    print("Tracer:", var)

    out = np.zeros(
        (1, nz, ny_new, nx_new),
        dtype=np.float32
    )

    for k in range(nz):

        out[0,k] = interp_field(
            data[0,k].values,
            pts_T
        )

    trcr_out[var] = (
        ("Time","zaxis_1","yaxis_1","xaxis_1"),
        out
    )

    trcr_out[var].attrs = data.attrs

print()
print("Writing:")
print(OUT_TRCR)

trcr_out.to_netcdf(OUT_TRCR)

print()
print("DONE")
print()
print("Generated:")
print(" ", OUT_CORE)
print(" ", OUT_TRCR)
