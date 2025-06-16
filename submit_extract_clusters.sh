#!/bin/bash -l
#SBATCH --cluster=smp
#SBATCH --partition=high-mem
#SBATCH --job-name=clusts
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A_%a.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A_%a.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu
#SBATCH --time=0-04:59:59
#SBATCH --array=0-199

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
fi
echo "OUT_PATH = $OUT_PATH"

##########################

echo "MAKING CLUSTER SUMMARY"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from make_cluster_summary_table import make_cluster_summary_table; make_cluster_summary_table('$OUT_PATH', job_id=${SLURM_ARRAY_TASK_ID}, n_chunks=${SLURM_ARRAY_TASK_COUNT})"

##########################
echo "Job ended at $(date)"
echo "DONE"

crc-job-stats
