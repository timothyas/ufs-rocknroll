# small-letkf

A quick test run to make sure the gears are turning

- 5 ensemble members
- 12 hour simulation (2 DA cycles)


Otherwise follows [this experimental
setup](https://github.com/NOAA-PSL/UFS-RNR/blob/develop/cylc/experiments/RDHPCS-Hera.LETKF_HYBGAIN.1p0.coupled.yaml)
i.e.,
- Coupled atmosphere, ocean, ice
- 1p0
- LETKF
- RDHPCS-Hera

## Questions

- How many tasks are really necessary for `gsi_3dvar_ens`? One per member? This
  took 20 minutes for a 100 member ensemble but times-out at 45 minutes for 5
  members by using at most 20 tasks per node (and therefore 1 node for this
  small setup). It still took too long with 2 nodes.

## The graphs

### Initial

<img src="small-letkf.graph.initial.png" width=1000>

### Cycling

<img src="small-letkf.graph.cycling.png" width=1000>

### Final

<img src="small-letkf.graph.final.png" width=1000>

## Steps

1. Add `rocknroll` environment varialbe to `~/.bashrc`
    ```bash
    export rocknroll=/path/to/this/repo
    ```
2. Copy the file `runtime.UFSRNRv2.ufsp7c.rc` to `UFS-RNR/cylc/runtime/`

3. Run it
    ```bash
    cd /path/to/UFS-RNR/cylc
    python cylc_run_ufsrnr.py --yaml $rocknroll/experiments/small-letkf/config.yaml
    ```

