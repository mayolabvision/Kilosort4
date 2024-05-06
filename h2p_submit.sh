#!/bin/bash -l
#SBATCH --cluster=smp
#SBATCH --partition=smp
#SBATCH --job-name=kilosort
#SBATCH --error=outfiles/error_%A_%a.err
#SBATCH --output=outfiles/out_%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu
#SBATCH --time=0-02:59:59
#SBATCH --array=0

echo "My SLURM_ARRAY_JOB_ID is $SLURM_ARRAY_JOB_ID."
echo "My SLURM_ARRAY_TASK_ID is $SLURM_ARRAY_TASK_ID"

module purge
module load gcc/8.2.0
module load python/ondemand-jupyter-python3.10
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

pytest --gpu

echo "DONE"
