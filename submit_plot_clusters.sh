#!/bin/bash -l
#SBATCH --cluster=smp
#SBATCH --partition=high-mem
#SBATCH --job-name=clusts
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A_%a.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu
#SBATCH --time=0-08:59:59
#SBATCH --array=0-1

echo "My SLURM_ARRAY_JOB_ID is $SLURM_ARRAY_JOB_ID."
echo "My SLURM_ARRAY_TASK_ID is $SLURM_ARRAY_TASK_ID"
echo "My SLURM_ARRAY_TASK_COUNT is $SLURM_ARRAY_TASK_COUNT"
echo "Job started at $(date)"

# INPUTS = FILENAME, IMEC, N_BLOCKS
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

##########INPUTS###########

SESSION="$1"
IMEC="${2:-0}"
RUN_TYPE="${3:-unleashed}"
SWEEP_NAME="${4:-none}"

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"
echo "RUN_TYPE: $RUN_TYPE"

OUT_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/kilosort4_${RUN_TYPE}"
if [[ "$RUN_TYPE" == "sweep" ]]; then
    OUT_PATH="${OUT_PATH}/${SWEEP_NAME}"
    SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/figs/kilosort4_${RUN_TYPE}/${SWEEP_NAME}/clusters"
else
    SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/figs/kilosort4_${RUN_TYPE}/clusters"
fi

##########################
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from kilosort_plots_h2p import plot_all_cluster_waveforms; plot_all_cluster_waveforms('$OUT_PATH', '$SAVE_PATH', job_id=${SLURM_ARRAY_TASK_ID}, n_chunks=${SLURM_ARRAY_TASK_COUNT})"

echo "DONE"

crc-job-stats
