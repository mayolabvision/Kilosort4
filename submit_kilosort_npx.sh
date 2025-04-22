#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-09:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:2
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --constraint=40g
#SBATCH --job-name=kilosort
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu

# INPUTS = FILENAME, IMEC, N_BLOCKS
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

##########INPUTS###########

SESSION="$1"
IMEC="${2:-0}"
N_BLOCKS="${3:-0}"

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"
echo "N_BLOCKS: $N_BLOCKS"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

# Run the KILOSORT_H2P function with nblocks from input
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', nblocks=$N_BLOCKS, run_ks=True, temp_wh=False)"

python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', nblocks=$N_BLOCKS, run_ks=False, temp_wh=True)"

# Rename kilosort4 output directory based on N_BLOCKS
PARENT_DIR=$(dirname "$SAVE_PATH")
KS_DIR="${PARENT_DIR}/kilosort4"

if [ -d "$KS_DIR" ]; then
    if [ "$N_BLOCKS" -eq 0 ]; then
        mv "$KS_DIR" "${PARENT_DIR}/kilosort4_baseline"
        echo "Renamed $KS_DIR to kilosort4_baseline"
    elif [ "$N_BLOCKS" -eq 1 ]; then
        mv "$KS_DIR" "${PARENT_DIR}/kilosort4_medicine"
        echo "Renamed $KS_DIR to kilosort4_medicine"
    else
        echo "N_BLOCKS=$N_BLOCKS not matched to known rename condition. No rename performed."
    fi
else
    echo "Directory $KS_DIR does not exist, skipping rename."
fi

echo "DONE"

