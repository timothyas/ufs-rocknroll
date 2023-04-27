
import os
from os.path import join
import xarray as xr
from rocknroll import print_dataset

class HPSSWriter():

    main_dir = "/scratch2/BMC/gsienkf/Tim.Smith/hpss-output/small-letkf/ufs-rnr.20151201060000"
    out_dir = "/scratch2/BMC/gsienkf/Tim.Smith/ufs-rocknroll/experiments/small-letkf/hpss-output"

    def read_and_write(self, dir_layers, ncfile):
        frontname = ".".join(dir_layers).replace("mem001", "member").replace("tile1", "tile").lower()
        basename = ncfile.split(".")[0].lower()
        try:
            ds = xr.open_dataset(ncfile)
            print_dataset(ds, fname=join(self.out_dir, f"{frontname}.{basename}.txt"))
        except:
            print(f"Warning: could not read and will skip: {ncfile}")


    def print_directory(self, dir_layers):
        """e.g. dir_layers is soca/mem001/letkf , describing the path relative to main_dir"""

        in_dir = join(self.main_dir, *dir_layers)
        os.chdir(in_dir)

        file_list = [x for x in os.listdir() if ".nc" in x]

        # Filter out tiles other than #1...
        tile_list = [x for x in file_list if "tile1" in x]
        file_list = [x for x in file_list if "tile" not in x]
        file_list += tile_list

        for ncfile in file_list:
            self.read_and_write(dir_layers, ncfile)



if __name__ == "__main__":

    writer = HPSSWriter()
    writer.print_directory(["gsi", "cntrl", "3dvar"])

    writer.print_directory(["soca", "mem001", "letkf"])
    writer.print_directory(["soca", "solver", "letkf", "obs"])
    writer.print_directory(["forecast", "mem001"])
    writer.print_directory(["forecast", "mem001", "INPUT"])
    writer.print_directory(["forecast", "mem001", "INPUT_NODA"])
    writer.print_directory(["forecast", "mem001", "RESTART"])
    writer.print_directory(["post", "gsi", "3dvar"])
    writer.print_directory(["post", "soca", "letkf"])
