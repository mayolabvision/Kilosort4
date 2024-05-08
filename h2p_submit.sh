#!/bin/bash -l
#SBATCH --cluster=smp
#SBATCH --partition=smp
#SBATCH --job-name=kilosort
#SBATCH --error=outfiles/error_%A_%a.err
#SBATCH --output=outfiles/out_%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu
#SBATCH --time=0-09:59:59

module purge
module load python/ondemand-jupyter-python3.10
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

python MAIN.py

echo "DONE"
