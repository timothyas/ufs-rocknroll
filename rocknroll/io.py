from os.path import join
import xarray as xr

class EnsembleDataset():

    experiment  = "hero-100"
    chunks = {
        "member"    : 1,
        "Time"      : 1,
        "Layer"     : 5,
        "lath"      : -1,
        "lonh"      : -1,
        "latq"      : -1,
        "lonq"      : -1,
        }

    @property
    def ic_path(self):
        return join(os.getenv("SSCRATCH"), "work", self.experiment, "20151201000000", "intercom", "initconds")


    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            try:
                getattr(self, key)
            except:
                raise
            setattr(self, key, val)


    def __call__(self, component, **kwargs):
        """
        Args:
            component (str): e.g. "ocean", "atmos", "ice"
        """

        kw = {"combine"     : "nested",
              "concat_dim"  : "member",
              "parallel"    : True,
              "chunks"      : self.chunks,
              "decode_times": False,
              }
        kw.update(kwargs)

        xds = xr.open_mfdataset(
                join(self.ic_path, component, "mem*", "*.nc"),
                **kw)

        return xds.squeeze()
