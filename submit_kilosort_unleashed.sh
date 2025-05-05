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

echo "SESSION: $SESSION"
echo "IMEC: $IMEC"

##########################

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/${SESSION}_t0.imec${IMEC}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

RUN_TYPE="unleashed"
echo "RUN_TYPE: $RUN_TYPE"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', run_type='$RUN_TYPE')"

RUN_TYPE="detect_motion"
echo "RUN_TYPE: $RUN_TYPE"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', run_type='$RUN_TYPE')"

OUT_PATH="/ix1/pmayo/lab_NHPdata/${SESSION}/${SESSION}_imec${IMEC}/kilosort4_unleashed"
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from make_cluster_summary_table import make_cluster_summary_table; make_cluster_summary_table('$OUT_PATH')"

echo "DONE"

