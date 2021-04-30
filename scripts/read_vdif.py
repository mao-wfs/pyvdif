# standard library
from pathlib import Path
from struct import Struct
from typing import Callable


# dependent packages
import numpy as np
import xarray as xr
from pyvdif.header import VDIFHeader


# constants
LITTLE_ENDIAN: str = "<"
UINT: str = "I"
SHORT: str = "h"
N_ROWS_VDIF_HEAD: int = 8
N_ROWS_CORR_HEAD: int = 64
N_ROWS_CORR_DATA: int = 512
N_UNITS_PER_SCAN: int = 64
N_BYTES_PER_UNIT: int = 1312
N_BYTES_PER_SCAN: int = 1312 * 64


# main features
def get_spectra(path: Path) -> np.ndarray:
    n_units = path.stat().st_size // N_BYTES_PER_UNIT
    n_integ = n_units // N_UNITS_PER_SCAN
    n_chans = N_ROWS_CORR_DATA // 2
    corr_dataset = np.empty([n_units, n_chans], dtype=complex)
    time_dataset = np.empty(
        n_units,
        dtype=[("time_series", "datetime64[ns]"), ("time_offset", "timedelta64[ms]")],
    )

    with open(path, "rb") as f:
        for i in range(n_units):
            vdif_head = read_vdif_head(f)
            time, frame_index = parse_vdif_head(vdif_head)
            read_corr_head(f)
            corr_data = read_corr_data(f)
            corr_dataset[i] = parse_corr_data(corr_data)
            time_dataset[i] = (time, frame_index)

    time_header = (
        time_dataset["time_series"] + (time_dataset["time_offset"] // 64 * 10)
    )[::N_UNITS_PER_SCAN]
    spectra_data = corr_dataset.reshape([int(n_integ), int(N_UNITS_PER_SCAN * n_chans)])
    spectra = xr.DataArray(
        spectra_data,
        dims=["t", "ch"],
        coords={"time": ("t", time_header)},
    )
    return spectra


# struct readers
def make_binary_reader(n_rows: int, dtype: str) -> Callable:
    struct = Struct(LITTLE_ENDIAN + dtype * n_rows)

    def reader(f):
        return struct.unpack(f.read(struct.size))

    return reader


read_vdif_head: Callable = make_binary_reader(N_ROWS_VDIF_HEAD, UINT)
read_corr_head: Callable = make_binary_reader(N_ROWS_CORR_HEAD, UINT)
read_corr_data: Callable = make_binary_reader(N_ROWS_CORR_DATA, SHORT)


# struct parsers
def parse_vdif_head(vdif_head: list):
    time = VDIFHeader(vdif_head).datetime
    frame_index = VDIFHeader(vdif_head).frame_index
    return time, frame_index


def parse_corr_head(corr_head: list):
    # not implemented yet
    pass


def parse_corr_data(corr_data: list) -> np.ndarray:
    real = np.array(corr_data[0::2])
    imag = np.array(corr_data[1::2])
    return real + imag * 1j
