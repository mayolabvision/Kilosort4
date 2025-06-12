#!/bin/bash -l
#SBATCH --cluster=smp
#SBATCH --partition=high-mem
#SBATCH --job-name=clusts
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu
#SBATCH --time=0-00:59:59

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

echo "CONCATENATING NPY FILES FOR EACH CLUSTER"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from make_cluster_summary_table import merge_clusters_to_csv; merge_clusters_to_csv('$OUT_PATH')"

##########################
echo "Job ended at $(date)"
echo "DONE"

crc-job-stats
