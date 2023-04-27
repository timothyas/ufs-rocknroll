
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

