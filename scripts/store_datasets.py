"""Read in forecasts, convert and store"""

from os.path import join
import yaml
from rocknroll import MOMDataset, FV3Dataset, CICEDataset
from zarr import NestedDirectoryStore


def get_varlist(model):
    with open("diagnostics.yaml", "r") as f:
        diags = yaml.safe_load(f)

    return diags[model]


if __name__ == "__main__":

    for name, Opener in zip(
            ["cice", "fv3", "mom"],
            [CICEDataset, FV3Dataset, MOMDataset]
            ):
        varlist = get_varlist(name)
        mom = Opener(experiment="small-2")
        xds = mom.open_ensemble_dataset(cycle="2015-12-01T00-00-00")
        xds = xds[varlist]
        mom.store_ensemble_dataset(xds)
        print(f"stored {name}.zarr...")
