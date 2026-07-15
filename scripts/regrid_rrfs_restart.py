#!/usr/bin/env python

import numpy as np
import xarray as xr
from scipy.ndimage import zoom
from pathlib import Path

# -------------------------------------------------------
# USER SETTINGS
# -------------------------------------------------------

NX_NEW = 254
NY_NEW = 158

SRC_DIR = "Data/inputs/lam_rrfs/bkg"
DST_DIR = "Data/inputs/lam_c418/bkg"

Path(DST_DIR).mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------
# Generic 2D interpolation
# -------------------------------------------------------

def interp2d(field, ny_new, nx_new):
    zy = ny_new / field.shape[-2]
    zx = nx_new / field.shape[-1]
    return zoom(field, (zy, zx), order=1)

# -------------------------------------------------------
# Generic N-dimensional interpolation
# last two dimensions = y,x
# -------------------------------------------------------

def interp_field(data, ny_new, nx_new):

    shp = data.shape

    if len(shp) == 2:

        return interp2d(data, ny_new, nx_new)

    lead_shape = shp[:-2]

    out = np.empty((*lead_shape, ny_new, nx_new), dtype=data.dtype)

    for idx in np.ndindex(*lead_shape):

        out[idx] = interp2d(
            data[idx],
            ny_new,
            nx_new,
        )

    return out

# -------------------------------------------------------
# Coordinate creation
# -------------------------------------------------------

def build_coord(name, size):
    return np.arange(1, size + 1)

# -------------------------------------------------------
# Process one restart file
# -------------------------------------------------------

def process_file(src_file, dst_file):

    print(f"\nProcessing {src_file}")

    src = xr.open_dataset(src_file)

    out = xr.Dataset()

    # ---------------------------------------------------
    # Coordinates
    # ---------------------------------------------------

    for v in src.variables:

        if v.startswith("xaxis_"):
            continue

        if v.startswith("yaxis_"):
            continue

        dims = src[v].dims

        if len(dims) == 1:
            out[v] = src[v]

    # New FV3 dimensions

    out["xaxis_1"] = ("xaxis_1", build_coord("xaxis_1", NX_NEW))
    out["xaxis_2"] = ("xaxis_2", build_coord("xaxis_2", NX_NEW + 1))

    out["yaxis_2"] = ("yaxis_2", build_coord("yaxis_2", NY_NEW))
    out["yaxis_1"] = ("yaxis_1", build_coord("yaxis_1", NY_NEW + 1))

    # ---------------------------------------------------
    # Main variables
    # ---------------------------------------------------

    for var in src.data_vars:

        dims = src[var].dims

        if len(dims) < 2:
            out[var] = src[var]
            continue

        data = src[var].values

        # detect dimensions

        if "yaxis_1" in dims:

            ny = NY_NEW + 1

        elif "yaxis_2" in dims:

            ny = NY_NEW

        else:
            out[var] = src[var]
            continue

        if "xaxis_2" in dims:

            nx = NX_NEW + 1

        elif "xaxis_1" in dims:

            nx = NX_NEW

        else:
            out[var] = src[var]
            continue

        print("  interpolating", var)

        newdata = interp_field(data, ny, nx)

        out[var] = (dims, newdata)

        for att in src[var].attrs:
            out[var].attrs[att] = src[var].attrs[att]

    print("  writing", dst_file)

    out.to_netcdf(dst_file)

# -------------------------------------------------------
# Files
# -------------------------------------------------------

files = [

    (
        "20201215.000000.rrfs_C403.fv_core.res.tile1.nc",
        "20201215.000000.rrfs_C418.fv_core.res.tile1.nc",
    ),

    (
        "20201215.000000.rrfs_C403.fv_tracer.res.tile1.nc",
        "20201215.000000.rrfs_C418.fv_tracer.res.tile1.nc",
    ),

    (
        "20201215.000000.rrfs_C403.fv_srf_wnd.res.tile1.nc",
        "20201215.000000.rrfs_C418.fv_srf_wnd.res.tile1.nc",
    ),

    (
        "20201215.000000.rrfs_C403.sfc_data.nc",
        "20201215.000000.rrfs_C418.sfc_data.nc",
    ),
]

for srcname, dstname in files:

    process_file(
        f"{SRC_DIR}/{srcname}",
        f"{DST_DIR}/{dstname}",
    )

print("\nDONE")
