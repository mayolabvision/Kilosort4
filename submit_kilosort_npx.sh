#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-05:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:1
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --job-name=kilosort
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=done,fail
#SBATCH --mail-user=knoneman@pitt.edu

# INPUTS = FILENAME, IMEC, N_BLOCKS
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

# Set NumExpr to use all allocated CPUs
export NUMEXPR_MAX_THREADS=$SLURM_CPUS_PER_TASK

##########INPUTS###########

SESSION="$1"
IMEC="${2:-0}"
DRIFT_CORRECT_TYPE="${3:-None}"

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"
echo "N_BLOCKS: $N_BLOCKS"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

# Run the KILOSORT_H2P function with nblocks from input
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', nblocks=$N_BLOCKS, drift_correction_type='$DRIFT_CORRECT_TYPE')"

echo "DONE"

