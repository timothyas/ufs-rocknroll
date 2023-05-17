##SBATCH --ntasks=1
##SBATCH --time=0:30:00
##SBATCH -A rda-ddm
##SBATCH --partition=service
##SBATCH -J hpss-rmdirs

module load hpss

declare -a experiment_list=("hero-100" "small-letkf" "small-letkf-2" "small-letkf-3" "small-letkf-4" "small-letkf-fcstdiags" "test-letkf-diagnostics")
hpssdir=BMC/gsienkf/5year/Tim.Smith

for experiment in ${experiment_list[@]}; do
    this_exp="${hpssdir}/${experiment}"
    for subdir in "${this_exp}/*.tar"; do
        hsi rm ${subdir}
        idx="${subdir}.idx"
        hsi rm ${idx}
    done
    for subsub in "${this_exp}/products/*.tar"; do
        hsi rm ${subsub}
        idx="${subsub}.idx"
        hsi rm ${idx}
    done

    for subsubsub in "${this_exp}/products/forecast/*.tar"; do
        hsi rm ${subsubsub}
        idx="${subsubsub}.idx"
        hsi rm ${idx}
    done

    for ens in "${this_exp}/products/forecast/ensembl*/"; do
        for cycle in "${ens}/*.tar"; do
            hsi rm ${cycle}
            idx="${cycle}.idx"
            hsi rm ${idx}
        done
        hsi rmdir ${ens}
    done 
    hsi rmdir ${this_exp}/products/forecast
    hsi rmdir ${this_exp}/products
    hsi rmdir ${this_exp}
done
