"""Read in forecasts, convert and store"""

import os
from os.path import join
import yaml
from rocknroll import MOMDataset, FV3Dataset, CICEDataset

import numpy as np


def get_varlist(model):
    with open("diagnostics.yaml", "r") as f:
        diags = yaml.safe_load(f)

    return diags[model]

def store_ensemble(xds, drop_coords):
    xds = xds.reset_coords()

    # need to make coordinates dataset only one time
    if not drop_coords:
        coords = [x for x in allvars["coords"] if x in xds]
        cds = xds[coords].set_coords(coords)
        if "member" in cds:
            cds = cds.isel(member=0).drop("member")
        op.store_coordinate_dataset(cds)

    # now data variables for all ensemble members at this cycle
    # make various time variables as coordinates
    data_vars = [x for x in allvars["data_vars"] if x in xds]
    xds = xds.set_coords(["time", "cftime", "ftime"])
    xds = xds[data_vars]

    op.store_ensemble_dataset(xds)


if __name__ == "__main__":


    cycle = "2015-12-01T00-00-00"
    models = {
            "fv3": FV3Dataset,
            "mom": MOMDataset,
            "cice": CICEDataset}

    for name, Opener in models.items():

        allvars = get_varlist(name)

        op = Opener(experiment="small-2")

        drop_coords = os.path.isdir(op.coords_path)
        xds = op.open_ensemble_dataset(cycle=cycle)

        store_ensemble(xds, drop_coords)
        op.store_reduced_ensemble_dataset(cycle=cycle, reduction="mean")
        op.store_reduced_ensemble_dataset(cycle=cycle, reduction="std")
