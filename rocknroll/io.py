import os
from os.path import join

import numpy as np
from zarr import NestedDirectoryStore
import xarray as xr

from datetime import datetime, timedelta
from cftime import DatetimeJulian

"""Decisions to be made:

    - Save as float32?
    - snapshots not averages
    - Use cftime or numpy.datetime64?
    - Make consistent dimension names across files
    - fields to be saved:
        -> FV3 missing surface
"""


class EnsembleDataset():
    """This does nothing on it's own, but all its children do something"""
    experiment  = None
    chunks_in   = None
    chunks_out  = None
    nc_glob     = None
    fhr         = 3
    time_format = "%Y-%m-%dT%H-%M-%S"
    zarr_name   = None

    @property
    def products_dir(self):
        return join(os.getenv("SCRATCH"), "work", self.experiment, "products", "forecast")

    @property
    def coords_dir(self):
        return join(os.getenv("SCRATCH"), "work", self.experiment, "products", "coordinates")

    @property
    def coords_path(self):
        return join(self.coords_dir, self.zarr_name)


    def __init__(self, experiment):
        self.experiment = experiment


    def get_forecast_time(self, cycle):
        t0 = datetime.strptime(cycle, self.time_format)
        return t0 + timedelta(hours=self.fhr)


    def get_forecast_time_vector(self, cycle):
        """All possible times for a dataset that has multiple time steps"""
        t0 = datetime.strptime(cycle, self.time_format)
        t = [np.datetime64(t0 + timedelta(hours=x)) for x in [3, 6, 9, 12]]
        return np.array(t)


    def get_ensemble_path(self, cycle):
        return join(self.products_dir, "ensemble", cycle, self.zarr_name)


    def get_mean_path(self, cycle):
        return join(self.products_dir, "ensemble-mean", cycle, self.zarr_name)


    def get_std_path(self, cycle):
        return join(self.products_dir, "ensemble-std", cycle, self.zarr_name)


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
                join(self.products_dir, cycle, "mem*", self.get_ncfilename(cycle)),
                **kw)

        xds.attrs.update({
                "cycle"                     : cycle,
                "cycle_iso"                 : datetime.strptime(cycle, self.time_format).isoformat(),
                "hours_since_cycle_start"   : self.fhr,
                })

        return xds.squeeze()


    def chunk(self, xds):

        chunks = self.chunks_out.copy()
        for key in self.chunks_out.keys():
            if key not in xds.dims:
                chunks.pop(key)

        return xds.chunk(chunks)


    def store_coordinate_dataset(self, cds):

        try:
            assert len(cds.data_vars) == 0
        except AssertionError:
            msg = f"EnsembleDataset.store_coordinate_dataset: we should not have any data variables in this dataset, but we found some."
            msg += f"\n{cds.data_vars}"
            raise AttributeError(msg)

        # these don't need to be chunked, coordinates are opened in memory
        store = NestedDirectoryStore(path=self.coords_path)
        cds.to_zarr(store, mode="w")
        print(f"Stored coordinate dataset at {self.coords_path}")


    def store_ensemble_dataset(self, xds):

        xds = self.chunk(xds)

        path = self.get_ensemble_path(cycle=xds.cycle)
        store = NestedDirectoryStore(path=path)
        xds.to_zarr(store, mode="w")
        print(f"Stored ensemble dataset at {path}")


    def store_reduced_ensemble_dataset(self, cycle, reduction="mean"):
        """Reduction is applied across 'member' axis"""

        try:
            assert reduction in ("mean", "std")
        except:
            raise NotImplementedError("only mean and std coded up")

        epath = self.get_ensemble_path(cycle=cycle)
        xds = xr.open_zarr(epath)

        with xr.set_options(keep_attrs=True):
            xds = xds.mean("member") if reduction == "mean" else \
                  xds.std("member")

        # add to meta data to let user know this happened
        for key in xds.data_vars:
            cell_methods = xds[key].attrs.get("cell_methods", "")
            xds[key].attrs["cell_methods"] = f"{cell_methods} member: {reduction}"

        path = self.get_mean_path(cycle=cycle) if reduction == "mean" else \
               self.get_std_path(cycle=cycle)
        store = NestedDirectoryStore(path=path)
        xds.to_zarr(store, mode="w")
        print(f"Stored ensemble {reduction} dataset at {path}")


class MOMDataset(EnsembleDataset):

    zarr_name   = "mom.zarr"
    chunks_in   = {
            "Layer"     : 5,
            "Interface" : 5,
            "yh"        : -1,
            "xh"        : -1,
            "yq"        : -1,
            "xq"        : -1,
            }

    chunks_out  = {
            "member"    : 50,
            "layer"     : 5,
            "interface" : 5,
            "yh"        : 30,
            "xh"        : 30,
            "yq"        : 30,
            "xq"        : 30,
            }


    def get_ncfilename(self, cycle):
        return "mom.nc"


    def open_ensemble_dataset(self, cycle, **kwargs):
        xds = super().open_ensemble_dataset(cycle, **kwargs)

        # rename time to use numpy.datetime64, but keep cftime
        # also make a "forecast_time" which is a timedelta
        xds = xds.rename({"time": "cftime"})
        t0 = np.datetime64(datetime.strptime(cycle, self.time_format))
        time = self.get_forecast_time_vector(cycle)
        xds["time"] = xr.DataArray(
                time,
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "time",
                    "axis": "T"},
                )

        xds["ftime"] = xr.DataArray(
                time-t0,
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "forecast_time",
                    "description": f"time passed since {cycle}",
                    "axis": "T"},
                )
        # use forecast time to pick the single hour we want
        # ... this convenience is why we use numpy.datetime/timedelta!
        xds = xds.swap_dims({"cftime": "ftime"})
        xds = xds.sel(ftime=f"{self.fhr}h")
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

        # Deal with time
        xds = xds.rename({"time": "cftime"})
        t0 = np.datetime64(datetime.strptime(cycle, self.time_format))
        time = np.datetime64(self.get_forecast_time(cycle))
        xds["time"] = xr.DataArray(
                time,
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "time",
                    "axis": "T"}
                )
        xds["ftime"] = xr.DataArray(
                time-t0,
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "forecast_time",
                    "description": "time passed since {cycle}",
                    "axis": "T"},
                )

        # convert ak/bk attrs to coordinates
        for key in ["ak", "bk"]:
            xds[key] = xr.DataArray(
                    xds.attrs.pop(key),
                    coords=xds["phalf"].coords,
                    dims=xds["phalf"].dims,
                    )
            xds = xds.set_coords(key)

        # rename grid_yt.long_name to avoid typo
        xds["grid_yt"].attrs["long_name"] = "T-cell latitude"
        return xds


class CICEDataset(EnsembleDataset):
    zarr_name   = "cice.zarr"
    chunks_in   = {
            "nc"        : 1,
            "nkice"     : 1,
            "nkaer"     : 1,
            "nksnow"    : 1,
            "nj"        : -1,
            "ni"        : -1,
            }
    chunks_out  = {
            "member"    : 50,
            "NCAT"      : 5,
            "VGRDi"     : 7,
            "VGRDa"     : 5,
            "nj"        : 30,
            "ni"        : 30,
            }

    def get_ncfilename(self, cycle):
        tf = self.get_forecast_time(cycle)
        tfstr = tf.strftime(self.time_format)
        return f"cice.{tfstr}.nc"


    def open_ensemble_dataset(self, cycle, **kwargs):
        xds = super().open_ensemble_dataset(cycle, **kwargs)

        # Deal with time
        t0 = np.datetime64(datetime.strptime(cycle, self.time_format))
        time = np.datetime64(self.get_forecast_time(cycle))

        # make cftime to be consistent with MOM and FV3
        cftime = DatetimeJulian(
                int(xds.time.dt.year),
                int(xds.time.dt.month),
                int(xds.time.dt.day),
                int(xds.time.dt.hour),
                int(xds.time.dt.minute),
                int(xds.time.dt.second),
                has_year_zero=False)
        xds["cftime"] = xr.DataArray(
                cftime,
                coords=xds["time"].coords,
                dims=xds["time"].dims,
                attrs={
                    "long_name": "time",
                    "axis": "T",
                    "calendar_type": "JULIAN"},
                )
        xds["ftime"] = xr.DataArray(
                time-t0,
                coords=xds["cftime"].coords,
                dims=xds["cftime"].dims,
                attrs={
                    "long_name": "forecast_time",
                    "description": "time passed since {cycle}",
                    "axis": "T"},
                )

        # Swap meaningless logical indices for values, where it makes sense (basically, not ni,nj)
        # Note we can only do this for time_bounds b/c ds is squeezed
        swap = {"nc"    : "NCAT",
                "nkaer" : "VGRDa",
                "nkice" : "VGRDi",
                "nksnow": "VGRDs",
                "d2"    : "time_bounds",
                }
        for org, new in swap.items():
            if new in xds and xds[new].ndim>0:
                if "member" in xds[new].dims:
                    xds[new] = xds[new].isel(member=0)
                xds = xds.swap_dims({org: new})
            if org in xds:
                xds = xds.drop(org)

        # This one gets squeezed out and is for some reason problematic?
        if xds["VGRDs"].ndim == 0:
            xds = xds.drop("VGRDs")
        return xds
