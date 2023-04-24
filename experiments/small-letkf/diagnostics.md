# Diagnostics

Tracking all outputs, figuring out what we have and what we need

## ufs-rnr

Inside the tarball `ufs-rnr.<date>.tar`

### gsi

- For enkf we have `write_ensmean` turned off, but we get the ensemble mean at
  obs locations. Is that option to write it out in grid space?

- Do not know how to read files inside of
    - `gsi/cntrl/hybgain/`
    - `gsi/ensmean/enkf/`
    - `gsi/mem*/enkf/`


- In the `ensmean` and `mem*` directories, fields are printed every 3 hours to 9
  hours, why?
    - see
      [here](https://github.com/NOAA-PSL/UFS-RNR/blob/918cb4a1767d677e89bdce9d208a206d06814e15/parm/gsi/gsi.C96.gefs_v13_reanalysis.yaml#L130),
      and similarly for enkf and hox options. Why is 9 there?


### soca

Inside `mem*/letkf` we have `CICE.res.nc` and `MOM.res.nc`. I will assume that
these files contain the prior/background state, and then updated from LETKF, based
on the fact that I was able to skip SOCA steps in the past.

... The time stamp says 18:00Z ... is the model running for 9 hours and we
just grab the last step?

See txt files for MOM and CICE output.



### forecast

- Storage related: Each `mem*` has the following:
    - `CICE_grid.nc`
    - `CICE_kmt.nc`, even though the field `kmt`, ocean fraction at T-cell
      centers, is in `CICE_grid.nc`
    - `CICE_mesh.nc`
    - `MOM6_mesh.nc`
    - `SST_2015_12_01.nc`, which has the date `2015-12-01T18:00:00` even though
      looking at  time stamp 06:00Z 
    - `sfc*` at 0, 3, 6, 9 fhr. Note that we could put 0000Z outside, and do not
      need 0900Z
    - 

- Cannot read `forecast/member/INPUT/ocean_channels.nc`
