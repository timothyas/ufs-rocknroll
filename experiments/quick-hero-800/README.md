# quick-hero-800

A quick test run to make sure the gears are turning for

- 800 ensemble members
- 80 atmosphere initial conditions (using copying idea)
- 12 hour simulation (2 DA cycles)


Otherwise follows [this experimental
setup](https://github.com/NOAA-PSL/UFS-RNR/blob/develop/cylc/experiments/RDHPCS-Hera.LETKF_HYBGAIN.1p0.coupled.yaml)
i.e.,
- Coupled atmosphere, ocean, ice
- 1p0
- LETKF
- RDHPCS-Hera

## Noticed issues

- `soca_ensperts` could be more efficient. Two parts:
    1. Init static b and compute perturbations, no problem (although unclear if
       this really needs 800 tasks over 200 nodes..
    2. Checkpoint model. Now this part chokes with 800 tasks, so drop down to
       just one node and run serially. This could be parallelized.

- Actually, it is not necessary to split `gsi_3dvar` into the two parts below.
  It just helps to run the file concatenation operations sequentially, as in
  without creating a `multi_prog` file for slurm (?), that is apparently too
  big.
  In any case it seems to go faster by doing these two steps together, keeping
  the 800 tasks, so maybe the file concatenation isn't truly serial? It takes
  45 minutes, maybe more, so will set to 1hr 15min just in case...
  So... don't need the tasks `gsi_3dvar_ensinc` and `gsi_3dvar_ensdeliver`, just
  `gsi_3dvar_ens`
    1. compute the increment using 800 tasks... no problem.
    2. concatenate a bunch of netcdf files, one per member per obs stream.
       Why do we want to concatenate? Probably faster to just use the fragmented
       files... Right now just doing this serially

- for hybrid gain applications ensemble mean is computed (?)
  both for 3dvar increment and enkf increment (need to verify that it's
  computing and not looking for precomputed file)

- For GSI, is the forecast going for 9 hours, and then we only use the 6th hour?
  Seems very inefficient if I'm interpreting that correctly.

- Are the GSI convdiags only using 3DVar?

### Note:
need to put the runtime.rc into the `cylc/runtime` directory... this is hard
coded unfortunately
