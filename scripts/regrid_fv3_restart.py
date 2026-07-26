#!/usr/bin/env python3

import sys
import yaml
import shutil
import numpy as np
import xarray as xr

from pathlib import Path
from scipy.ndimage import zoom


def interp2d(field, ny_new, nx_new, order=1):

    zy = ny_new / field.shape[-2]
    zx = nx_new / field.shape[-1]

    return zoom(
        field,
        (zy, zx),
        order=order,
    )


def interp_field(data, ny_new, nx_new, order=1):

    shp = data.shape

    #
    # simple 2D field
    #
    if len(shp) == 2:

        return interp2d(
            data,
            ny_new,
            nx_new,
            order,
        )

    #
    # interpolate last two dimensions
    #
    lead_shape = shp[:-2]

    out = np.empty(
        (*lead_shape, ny_new, nx_new),
        dtype=data.dtype,
    )

    for idx in np.ndindex(*lead_shape):

        out[idx] = interp2d(
            data[idx],
            ny_new,
            nx_new,
            order,
        )

    return out


def build_coord(size):

    return np.arange(
        1,
        size + 1,
    )


class FV3RestartInterpolator:

    def __init__(
        self,
        grid_file,
        src_dir,
        dst_dir,
        order=1,
    ):

        self.grid_file = grid_file
        self.src_dir = src_dir
        self.dst_dir = dst_dir

        self.order = order

        Path(
            self.dst_dir
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        self.load_target_grid()

    def load_target_grid(self):

        ds = xr.open_dataset(
            self.grid_file
        )

        self.nx = ds.sizes["nx"]
        self.ny = ds.sizes["ny"]

        self.nxp = ds.sizes["nxp"]
        self.nyp = ds.sizes["nyp"]

        print()
        print(
            f"Target Grid:"
        )
        print(
            f"  nx={self.nx}"
        )
        print(
            f"  ny={self.ny}"
        )
        print(
            f"  nxp={self.nxp}"
        )
        print(
            f"  nyp={self.nyp}"
        )

    def process_file(
        self,
        src_file,
        dst_file,
    ):

        print()
        print(
            f"Processing {src_file}"
        )

        src = xr.open_dataset(
            src_file
        )

        out = xr.Dataset()

        #
        # Copy all 1D vars
        #
        for v in src.variables:

            if len(src[v].dims) == 1:

                out[v] = src[v]

        #
        # Build FV3 coordinates
        #
        out["xaxis_1"] = (
            "xaxis_1",
            build_coord(self.nx),
        )

        out["xaxis_2"] = (
            "xaxis_2",
            build_coord(self.nxp),
        )

        out["yaxis_1"] = (
            "yaxis_1",
            build_coord(self.nyp),
        )

        out["yaxis_2"] = (
            "yaxis_2",
            build_coord(self.ny),
        )

        #
        # Interpolate fields
        #
        for var in src.data_vars:

            dims = src[var].dims

            #
            # Scalars and 1D vars
            #
            if len(dims) < 2:

                out[var] = src[var]
                continue

            #
            # Determine target sizes
            #
            if "yaxis_1" in dims:

                ny_new = self.nyp

            elif "yaxis_2" in dims:

                ny_new = self.ny

            else:

                out[var] = src[var]
                continue

            if "xaxis_2" in dims:

                nx_new = self.nxp

            elif "xaxis_1" in dims:

                nx_new = self.nx

            else:

                out[var] = src[var]
                continue

            print(
                f"  interpolating {var}"
            )

            newdata = interp_field(
                src[var].values,
                ny_new,
                nx_new,
                self.order,
            )

            out[var] = (
                dims,
                newdata,
            )

            #
            # Preserve attrs
            #
            out[var].attrs.update(
                src[var].attrs
            )

        #
        # Preserve global attrs
        #
        out.attrs.update(
            src.attrs
        )

        print(
            f"  writing {dst_file}"
        )

        out.to_netcdf(
            dst_file
        )

    def process_files(
        self,
        files,
    ):

        for entry in files:

            src_file = (
                f"{self.src_dir}/"
                f"{entry['src']}"
            )

            dst_file = (
                f"{self.dst_dir}/"
                f"{entry['dst']}"
            )

            self.process_file(
                src_file,
                dst_file,
            )


def main():

    if len(sys.argv) != 2:

        print(
            "\nUsage:\n"
            "python regrid_fv3_restart.py c1667.yaml\n"
        )

        sys.exit(1)

    with open(
        sys.argv[1],
        "r",
    ) as f:

        cfg = yaml.safe_load(f)

    job = FV3RestartInterpolator(

        grid_file=
        cfg["grid"]["output"]["grid_file"],
        
        src_dir=
        cfg["background"]["src_dir"],

        dst_dir=
        cfg["background"]["dst_dir"],

        order=
        cfg["interpolation"]["order"],
    )

    job.process_files(
        cfg["background"]["files"]
    )

    #
    # Copy coupler.res
    #
    print()
    print(
        "Copying coupler.res"
    )

    shutil.copy(
        cfg["coupler"]["src"],
        cfg["coupler"]["dst"],
    )

    print()
    print("DONE")


if __name__ == "__main__":
    main()
