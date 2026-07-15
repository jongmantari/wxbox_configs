from netCDF4 import Dataset, stringtochar
import numpy as np
import shutil

# Copy working RRFS mosaic
shutil.copy(
    "Data/inputs/lam_rrfs/INPUT/C403_mosaic.halo3.nc",
    "Data/inputs/lam_c418/INPUT/C418_mosaic_rrfsstyle.nc"
)

fname = "Data/inputs/lam_c418/INPUT/C418_mosaic_rrfsstyle.nc"

with Dataset(fname, "r+") as nc:

    def write_char_string(varname, text):
        v = nc.variables[varname]
        strlen = v.shape[1]

        arr = stringtochar(
            np.array([text.ljust(strlen)], dtype=f"S{strlen}")
        )

        v[:] = arr

    write_char_string("gridfiles",      "C418_grid.tile7.nc")
    write_char_string("gridfiles_path", "Data/inputs/lam_c418")
    write_char_string("gridtiles",      "tile7")

print(f"Updated {fname}")
