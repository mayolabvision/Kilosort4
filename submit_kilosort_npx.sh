#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-09:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:2
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --constraint=40g
#SBATCH --job-name=kilosort
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.err
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu

# INPUTS = FILENAME, IMEC
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${1}/${1}_imec${2}/${1}_t0.imec${2}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${1}/${1}_imec${2}/${1}_t0.imec${2}.ap_kilosortChanMap.mat"
KILO4_PATH="/ix1/pmayo/lab_NHPdata/${1}/${1}_imec${2}/kilosort4"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

# Run the KILOSORT_H2P function from the imported file
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', run_ks=True, temp_wh=False)"

python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH', '$PROBE_PATH', run_ks=False, temp_wh=True)"

echo "DONE"
