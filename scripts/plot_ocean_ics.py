
import os
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

import cmocean

import sys
sys.path.append("..")
from rocknroll import EnsembleDataset

if __name__ == "__main__":

    eds = EnsembleDataset()
    ds = eds(component="ocean")
    fig_dir = "../figures"
    if not os.path.isdir(fig_dir):
        os.makedirs(fig_dir)

    # Standard deviation
    # Only of temperature and salinity, only taking these as controls, I guess
    vlist = ["Temp"]#, "Salt"]
    nrows = len(vlist)
    ncols = 1
    fig, axs = plt.subplots(nrows, ncols, figsize=(5*ncols, 4*nrows), constrained_layout=True)

    axs = [axs]
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("gray")

    for var, axr in zip(vlist, axs):
        fld = ds[var].isel(Layer=0) if "Layer" in ds[var].dims else ds[var]
        spread = fld.std("member")
        lon = "lonh" if "lonh" in ds[var].dims else "lonq"

        spread2 = fld.isel(member=slice(80)).std("member")
        diff = spread - spread2
        diff = diff.sortby(lon)

        # standard deviation
        ax = axr#[0]
        diff.where(spread>1e-4).plot(
                ax=ax,
                cbar_kwargs={"label": "SD Diff"},
                cmap=cmap,
                )

        # histogram
        # this is not really illuminating for small differences...
        # TODO: get the mask. for now, just avoid where std = 0
        box = (ds.lonh < 40) & (ds.lonh > 30) & (ds.lath>-45) & (ds.lath<-40)
        ax.axhline(y=-40, xmin=30, xmax=40, color='k')#, transform=ax.transData)
        ax.axhline(y=-45, xmin=30, xmax=40, color='k')#, transform=ax.transData)
        ax.axvline(x=40, ymin=-45, ymax=-40, color='k')#, transform=ax.transData)
        ax.axvline(x=30, ymin=-45, ymax=-40, color='k')#, transform=ax.transData)

        #for upper in [None, 80]:
        #    hist = fld.where(box, drop=True)
        #    hist = hist.sel(member=slice(upper))
        #    hist.plot.hist(
        #            ax=axr[1],
        #            density=True,
        #            alpha=.2,
        #            )
        ax.set(ylabel="", xlabel="", title=f"Surface {var} Spread Difference\n(100mem SD - 80mem SD)")
        #axr[1].set(ylabel="", xlabel="", title=var)

    fig.savefig(f"{fig_dir}/sst-spread-diff.jpg", bbox_inches="tight", dpi=300)
