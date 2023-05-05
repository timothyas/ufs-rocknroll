import os
from os.path import join

import numpy as np
from zarr import NestedDirectoryStore
import xarray as xr


from datetime import datetime, timedelta

"""Decisions to be made:

    - Save as float32?
    - Use cftime or numpy.datetime64?
    - Make consistent dimension names across files
    - fields to be saved:
        -> FV3 missing surface
        -> WTF is going on with CICE fields
"""


class EnsembleDataset():
    """This does nothing on it's own, but all its children do something"""
    experiment  = None
    chunks_in   = None
    chunks_out  = None
    nc_glob     = None
    fhr         = 3
    time_format = "%Y-%m-%dT%H-%M-%S"

    @property
    def products_path(self):
        return join(os.getenv("SCRATCH"), "work", self.experiment, "products", "forecast")


    def __init__(self, experiment):
        self.experiment = experiment

    def get_forecast_time(self, cycle):
        t0 = datetime.strptime(cycle, self.time_format)
        return t0 + timedelta(hours=self.fhr)


    def get_ncfilename(self, cycle):
        return


    def preprocess(self, xds):
        fname = xds.encoding["source"]
        # member from filename starts with 1
        # to make our python lives easier... start with 0
        memp1 = int( fname.split("/mem")[-1].split("/")[0] )
        xds["member"] = [memp1-1]
        xds["member"].attrs = {
                "long_name" : "Ensemble Member ID",
                }
        return xds


    def open_ensemble_dataset(self, cycle, **kwargs):
        """For now, read a single timestep from each cycle"""

        kw = {"combine"     : "nested",
              "concat_dim"  : "member",
              "parallel"    : True,
              "chunks"      : self.chunks_in,
              "decode_times": True,
              "preprocess"  : self.preprocess,
              }
        kw.update(kwargs)

        xds = xr.open_mfdataset(
                join(self.products_path, cycle, "mem*", self.get_ncfilename(cycle)),
                **kw)

        xds.attrs.update({
                "cycle"                     : cycle,
                "cycle_iso"                 : datetime.strptime(cycle, self.time_format).isoformat(),
                "hours_since_cycle_start"   : self.fhr,
                })

        return xds.squeeze()


    def store_ensemble_dataset(self, xds):

        for key in xds.data_vars:
            xds[key] = xds[key].astype(np.float32)

        chunks = self.chunks_out.copy()
        for key in self.chunks_out.keys():
            if key not in xds.dims:
                chunks.pop(key)

        xds = xds.chunk(chunks)
        path = join(self.products_path, "ensemble", xds.cycle, self.zarr_name)
        store = NestedDirectoryStore(path=path)
        xds.to_zarr(store, mode="w")


class MOMDataset(EnsembleDataset):

    zarr_name   = "mom.zarr"
    chunks_in   = {
            "Layer"     : 5,
            "Interface" : 5,
            "lath"      : -1,
            "lonh"      : -1,
            "latq"      : -1,
            "lonq"      : -1,
            }

    chunks_out  = {
            "member"    : 50,
            "layer"     : 5,
            "interface" : 5,
            "lath"      : 30,
            "lonh"      : 30,
            "latq"      : 30,
            "lonq"      : 30,
            }


    def get_ncfilename(self, cycle):
        tf = self.get_forecast_time(cycle)
        tfstr = tf.strftime(self.time_format)
        return f"mom.{tfstr}.nc"


    def open_ensemble_dataset(self, cycle, **kwargs):
        xds = super().open_ensemble_dataset(cycle, **kwargs)

        # Recreate time to be... sensible, rename
        xds["time"] = xr.DataArray(
                np.datetime64(self.get_forecast_time(cycle)),
                coords=xds["Time"].coords,
                dims=xds["Time"].dims,
                attrs={
                    "long_name": "time",
                    "cartesian_axis": "T"}
                )
        xds = xds.set_coords("time")
        xds = xds.drop("Time")

        # lowercase coordinates please
        for key in xds.coords:
            xds = xds.rename({key: key.lower()})

        return xds

class FV3Dataset(EnsembleDataset):
    zarr_name   = "fv3.zarr"
    chunks_in   = {
            "pfull"     : 5,
            "grid_yt"   : -1,
            "grid_xt"   : -1,
            }

    chunks_out  = {
            "member"    : 50,
            "pfull"     : 5,
            "grid_yt"   : 30,
            "grid_xt"   : 30,
            }

    def get_ncfilename(self, cycle):
        return f"sfg_f{self.fhr:03d}.nc"


    def open_ensemble_dataset(self, cycle, **kwargs):
        xds = super().open_ensemble_dataset(cycle, **kwargs)


        xds = xds.rename({"time": "cftime"})
        xds["time"] = xr.DataArray(
                np.datetime64(self.get_forecast_time(cycle)),
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "time",
                    "cartesian_axis": "T"}
                )
        xds = xds.set_coords(["time", "lon", "lat"])
        return xds


class CICEDataset(EnsembleDataset):
    zarr_name   = "cice.zarr"
    chunks_in   = {
            "ncat"      : -1,
            "nj"        : -1,
            "ni"        : -1,
            }
    chunks_out  = {
            "member"    : 50,
            "ncat"      : 5,
            "nj"        : 30,
            "ni"        : 30,
            }

    def get_ncfilename(self, cycle):
        tf = self.get_forecast_time(cycle)
        tfstr = tf.strftime(self.time_format)
        return f"cice.{tfstr}.nc"


    def open_ensemble_dataset(self, cycle, **kwargs):
        xds = super().open_ensemble_dataset(cycle, **kwargs)

        time = [np.datetime64(self.get_forecast_time(cycle))]
        xds["time"] = xr.DataArray(
                time,
                coords={"time": time},
                dims=("time",),
                attrs={
                    "long_name": "time",
                    "cartesian_axis": "T"}
                )
        xds = xds.set_coords(["time"])
        return xds
