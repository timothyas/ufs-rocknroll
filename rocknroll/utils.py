import numpy as np

def print_dataset(xds, fname):

    with open(fname, "w") as f:
        print(" --- Coordinates --- ", file=f)
        for key in xds.coords:
            print(f"{xds[key].name}", file=f)
            for k2,v2 in xds[key].attrs.items():
                print(f"    {k2:<16s} : {v2}", file=f)
            print(file=f)


        print(file=f)
        print(" --- Data Variables --- ", file=f)
        for key in xds.data_vars:
            print(f"{xds[key].name}", file=f)
            print(f"    {'dims':<16s} : {xds[key].dims}", file=f)
            for k2,v2 in xds[key].attrs.items():
                print(f"    {k2:<16s} : {v2}", file=f)
            print(file=f)


def read_timing(fname):
    """
    Args:
        fname (str): path to job.status file

    Returns:
        timing (int): in seconds
    """

    start = None
    stop = None
    with open(fname, "r") as f:
        for line in f:
            if "CYLC_JOB_INIT_TIME" in line:
                start = line.split("=")[-1].replace("Z\n","")
            elif "CYLC_JOB_EXIT_TIME" in line:
                stop = line.split("=")[-1].replace("Z\n","")

    assert start is not None and stop is not None, "Could not find start and/or stop time"

    dtime = np.datetime64(stop) - np.datetime64(start)
    return dtime.astype("<m8[s]").astype(int)


