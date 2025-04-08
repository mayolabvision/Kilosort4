#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-06:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:4
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --constraint=40g
#SBATCH --job-name=kilosort
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/error_%A.err
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu

module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

SAVE_PATH="/ix1/pmayo/lab_NHPdata/${1}_g0/${1}_g0_imec${2}/${1}_g0_t0.imec${2}.ap.bin"
PROBE_PATH="/ix1/pmayo/lab_NHPdata/${1}_g0/${1}_g0_imec${2}/${1}_g0_t0.imec${2}.ap_kilosortChanMap.mat"

echo "SAVE_PATH = $SAVE_PATH"
echo "PROBE_PATH = $PROBE_PATH"

# Run the KILOSORT_H2P function from the imported file
python -c "from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH','$PROBE_PATH')"

echo "DONE"
