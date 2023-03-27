# hero-100

Tests simply to make sure that ensemble IC copying works, so we can run more
than 80 member ensembles.
This takes the 80 GEFSv12 ICs for 2015-12-01T00:00:00 and copies the first 20
over to initialize members 81-100.

- 100 ensemble members
- 12 hour simulation (2 DA cycles)

Otherwise follows [this experimental
setup](https://github.com/NOAA-PSL/UFS-RNR/blob/develop/cylc/experiments/RDHPCS-Hera.LETKF_HYBGAIN.1p0.coupled.yaml)
