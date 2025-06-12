#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-08:00:00
#SBATCH --gres=gpu:1
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
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
IMEC="$2"
LINE_ID="$3"

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"
echo "LINE_ID: $LINE_ID"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

echo "RUNNING KILOSORT"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from kilosort_sweep import kilosort_sweep; kilosort_sweep('$SAVE_PATH', '$PROBE_PATH', line_id=${LINE_ID})"

##########################
echo "Job ended at $(date)"
echo "DONE"

crc-job-stats
