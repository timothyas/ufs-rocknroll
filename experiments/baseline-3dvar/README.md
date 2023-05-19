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

## Steps

1. Add `rocknroll` environment varialbe to `~/.bashrc`
    ```bash
    export rocknroll=/path/to/this/repo
    ```
   This is used within the yaml files to point to yaml files inside of this
   directory, and one can run `grep rocknroll *.yaml` to find all the
   modifications.

2. Run it
    ```bash
    cd /path/to/UFS-RNR/cylc
    python cylc_run_ufsrnr.py --yaml $rocknroll/experiments/baseline-3dvar/config.yaml
    ```

## List of failed tasks & dates

There are some dates that failed, only the first is actually an issue.
This documents the hiccups that occurred, and how to avoid them in the future.

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
    * Confirmed by Henry, the failure is related to missing observation files,
      so both the task and its dependencies can be skipped
        ```bash
        cylc reset --state=succeeded baseline-3dvar soca_3dvar.20160123T0600Z
        cylc reset --state=succeeded baseline-3dvar soca_insitudiags.20160123T0600Z
        cylc reset --state=succeeded baseline-3dvar soca_post.20160123T0600Z
        ```

- 2016-01-26T12:00: `staging_fetch_atmosobs` and `staging_fetch_atmostcvsyndat`
    * Actually these task failures were just a hiccup. Re-triggering the jobs got us going again, e.g.
        ```bash
        $ cylc trigger baseline-3dvar staging_fetch_atmosobs.20160126T1200Z
        ```

