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

SRC_SFCW = (
    "Data/inputs/lam_rrfs/bkg/"
    "20201215.000000.rrfs_C403.fv_srf_wnd.res.tile1.nc"
)

SRC_SFCD = (
    "Data/inputs/lam_rrfs/bkg/"
    "20201215.000000.rrfs_C403.sfc_data.nc"
)

TGT_GRID = (
    "/home/jonggyunkim/grids/"
    "esg.regional_west3km/C1667/"
    "C1667_grid.tile7.halo3.nc"
)

OUTDIR = "Data/inputs/lam_c1667/bkg"

OUT_SFCW = (
    f"{OUTDIR}/"
    "20201215.000000.rrfs_C1667."
    "fv_srf_wnd.res.tile1.nc"
)

OUT_SFCD = (
    f"{OUTDIR}/"
    "20201215.000000.rrfs_C1667."
    "sfc_data.nc"
)

# =====================================================
# CREATE OUTPUT DIRECTORY
# =====================================================

os.makedirs(OUTDIR, exist_ok=True)

# =====================================================
# FV3 CELL CENTERS
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
# RRFS SURFACE GRID
# =====================================================

ny_src = 105
nx_src = 201

lon_src = lon_src_cc[:ny_src, :nx_src]
lat_src = lat_src_cc[:ny_src, :nx_src]

pts_src = np.column_stack([
    lon_src.ravel(),
    lat_src.ravel()
])

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
# INTERPOLATORS
# =====================================================

def interp_linear(field):

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

def interp_nearest(field):

    vals = field.ravel()

    out = griddata(
        pts_src,
        vals,
        pts_tgt,
        method="nearest"
    )

    return out.reshape(
        ny_new,
        nx_new
    )

# =====================================================
# SURFACE WIND FILE
# =====================================================

print()
print("Interpolating fv_srf_wnd...")

sfcw = xr.open_dataset(SRC_SFCW)
sfcw_out = xr.Dataset()

for var in sfcw.data_vars:

    print("  ", var)

    data = sfcw[var].values

    out = np.zeros(
        (1, 1, ny_new, nx_new),
        dtype=np.float32
    )

    out[0,0] = interp_linear(
        data[0,0]
    )

    sfcw_out[var] = (
        ("Time","zaxis_1","yaxis_1","xaxis_1"),
        out
    )

    sfcw_out[var].attrs = sfcw[var].attrs

print("Writing:", OUT_SFCW)

sfcw_out.to_netcdf(OUT_SFCW)

# =====================================================
# SFC DATA
# =====================================================

print()
print("Interpolating sfc_data...")

sfcd = xr.open_dataset(SRC_SFCD)
sfcd_out = xr.Dataset()

nearest_vars = {
    "slmsk",
    "stype",
    "vtype"
}

for var in sfcd.data_vars:

    print("  ", var)

    data = sfcd[var]

    arr = data.values

    # ------------------------------------------
    # 3D
    # ------------------------------------------

    if len(arr.shape) == 4:

        nt, nz, _, _ = arr.shape

        out = np.zeros(
            (nt, nz, ny_new, nx_new),
            dtype=np.float32
        )

        for t in range(nt):

            for k in range(nz):

                if var in nearest_vars:

                    out[t,k] = interp_nearest(
                        arr[t,k]
                    )

                else:

                    out[t,k] = interp_linear(
                        arr[t,k]
                    )

        sfcd_out[var] = (
            data.dims,
            out
        )

    sfcd_out[var].attrs = data.attrs

print("Writing:", OUT_SFCD)

sfcd_out.to_netcdf(OUT_SFCD)

print()
print("DONE")
