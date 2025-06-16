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

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"

run_name="${SESSION%_g0}"
RUNIT_PATH="/ihome/pmayo/knoneman/Packages/CatGT-linux/runit.sh"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

# check if need to run SGLXMetaToCoords
if [ ! -f "$PROBE_PATH" ]; then
    echo "PROBE_PATH does not exist. Running MetaToCoords..."

    META_PATH="${SAVE_PATH%.bin}.meta"

    python3 -c "import sys; from pathlib import Path; sys.path.insert(0, '/ihome/pmayo/knoneman/Packages/HelperFunctions/utils'); from SGLXMetaToCoords import MetaToCoords; import numpy as np; MetaToCoords(Path('$META_PATH'), 1, badChan=np.zeros((0), dtype='int'), destFullPath='', showPlot=True)"

else
    echo "PROBE_PATH exists. Skipping MetaToCoords."
fi

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

if [ ! -d "/ix1/pmayo/lab_NHPdata/${SESSION}/catgt_${SESSION}" ]; then
    echo "Directory ${CATGT_DIR} does NOT exist. Running runit.sh..."
    ${RUNIT_PATH} '-dir=/ix1/pmayo/lab_NHPdata -run='$run_name' -g=0 -t=0,0 -t_miss_ok -ni -prb=0 -bf=0,0,-1,0,9,1 -dest=/ix1/pmayo/lab_NHPdata/'$SESSION''
else
    echo "catgt_'$SESSION' exists. Skipping runit.sh."
fi

#########################################################################
echo "ESTIMATING DRIFT"
python -c "
import sys
sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4')
from KILOSORT_H2P import kilosort_h2p

kwargs = {'run_type': 'detect_motion'}
kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', **kwargs)
"

##########################
echo "Job ended at $(date)"
echo "DONE"

crc-job-stats
