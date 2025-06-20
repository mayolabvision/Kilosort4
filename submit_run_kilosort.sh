#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-08:00:00
#SBATCH --gres=gpu:2
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=24
#SBATCH --job-name=kilosort
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=done,fail
#SBATCH --mail-user=knoneman@pitt.edu

# INPUTS = FILENAME, IMEC, N_BLOCKS
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

##########INPUTS###########

SESSION="$1"
IMEC="${2:-0}"
RUN_TYPE="${3:-unleashed}"

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"
echo "RUN_TYPE: $RUN_TYPE"

run_name="${SESSION%_g0}"
RUNIT_PATH="/ihome/pmayo/knoneman/Packages/CatGT-linux/runit.sh"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

#########################################################################
echo "RUNNING KILOSORT"
python -c "import sys
sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4')
from KILOSORT_H2P import kilosort_h2p

kwargs = {'run_type': '$RUN_TYPE'}
kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', **kwargs)
"

##########################
echo "Job ended at $(date)"
echo "DONE"

crc-job-stats
