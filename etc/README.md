# Extra files

## Singularity Recipe

### xarray issues
xarray has some unfortunately strange behavior for certain versions when
`open_mfdataset(..., parallel=True)`.
Basically the function needs to be called once, then it can succeed the second
time? Something like that, but it's not consistent.

- Does not happen with an old version of xarray and python 3.8, does with 3.9
    * Python 3.8 and 3.9 are only available on Ubuntu 20.04

- Does happen with python 3.10, sometimes with 3.11 (although this has some
  other strange bugs - I don't think it's ready yet).
    * Note that both python 3.10 and 3.11 are only available on Ubuntu 22.04
