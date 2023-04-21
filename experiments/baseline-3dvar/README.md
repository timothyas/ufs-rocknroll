# baseline-3dvar

A baseline 3DVar experiment for comparison

- 3DVar
- 3 month simulation


Otherwise follows [this experimental
setup](https://github.com/NOAA-PSL/UFS-RNR/blob/develop/cylc/experiments/RDHPCS-Hera.3DVar.1p0.coupled.yaml)
i.e.,
- Coupled atmosphere, ocean, ice
- 1p0
- RDHPCS-Hera

## List of failed tasks & dates

- 2016-01-23T06:00: `soca_3dvar` fails with no comprehensible message. In the
  work jedi/soca/3dvar directory, `var.err` just gives
  ```bash
  Abort(1) on node 1 (rank 1 in comm 0): application called MPI_Abort(MPI_COMM_WORLD, 1) - process 1
  ```
  For each process. Thanks to Henry, who noticed the following incorrect detail
  about observations:
  ```bash
  ufo_geovals_get2d_f90sea_surface_temperature is not a 2D var:           0 levels
  ```
  Meaning that there is likely a land mismatch in one of the super-ob SST files.
  Proceed by skipping it and the dependent `soca_insitudiags` and `soca_post`
  tasks by resetting the state to succeeded.

- 2016-01-26T12:00: `staging_fetch_atmosobs` and `staging_fetch_atmostcvsyndat`
  Actually this was just a hiccup. Re-triggering the jobs got us going again.

