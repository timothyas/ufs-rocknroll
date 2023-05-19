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


## Added tasks

The added tasks generally split single tasks into more subtasks in order to take
advantage of different regimes of parallelism.

- `ocean_ens_initconds_socaensperts` is now split into two parts:
    1. `ocean_ens_pertconds_socaensperts`: Init static b and compute perturbations, no problem (although unclear if
       this really needs 800 tasks over 200 nodes..
    2. `ocean_ens_ckptconds_socaensperts`: Checkpoint model (i.e., save output in format for MOM).
       Now this part chokes with 800 tasks, so drop down to
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

- `gsi_enkf` is split into two parts.
    1. `gsi_enkfonly`: runs the `gsi_enkf` executable, better to use more shared/thread-based parallelism
       e.g., 1 MPI task per node, 40 cpus
       per task and as many threads as possible. Note, using hyperthreading
       (i.e. `OMP_NUM_THREADS=80`) will require python changes b/c UFSRNR looks
       for the cpuspertask and sets that to omp threads.
       Right now, I am setting the `OMP_NUM_THREADS` manually inside of the
       `runtime*.rc` file.
       -> Note: Additionally, we will want to use Jeff's script to create 6 eigenvectors, for
          localization with additional pseudo ensemble members. See
          [../../scripts/create_vlocal_eig.py](../../scripts/create_vlocal_eig.py)
          and [../../scripts/global_hyblev.l128.txt](../../scripts/global_hyblev.l128.txt)
          which can be used like
          ```bash
          $ python create_vlocal_eig.py 64 98 global_hyblev.l128.txt
          ```
          to create 6 eigenvectors, reducing the memory footprint by ~50% over
          original setup
        -> Note: we don't want to do `modelspace_vloc=.FALSE.` in the namelist,
           because this means we will just do localization in observation space
           (it doesn't turn off localization completely). According to Jeff,
           Obs space localization will not use the radiance data as effectively.
    2. `gsi_enkfmean`: The `ensemble mean` part wants at least one MPI process per ensemble
       member, so this task uses a more distributed parallelism structure.

## Steps

1. Add `rocknroll` environment varialbe to `~/.bashrc`
    ```bash
    export rocknroll=/path/to/this/repo
    ```
   This is used within the yaml files to point to yaml files inside of this
   directory, and one can run `grep rocknroll *.yaml` to find all the
   modifications.

2. Modify `tasks.yaml` to use the right account, e.g. `gsienkf` whereas I'm
   using `rda-ddm`

3. Checkout my fork and branch of UFS-RNR,
   [hero-stuff](https://github.com/timothyas/UFS-RNR/tree/feature/hero-stuff)

4. Copy the file `runtime.UFSRNRv2.ufsp7c.rc` to `UFS-RNR/cylc/runtime/`

5. Run it
    ```bash
    cd /path/to/UFS-RNR/cylc
    python cylc_run_ufsrnr.py --yaml $rocknroll/experiments/quick-hero-800/config.yaml
    ```
