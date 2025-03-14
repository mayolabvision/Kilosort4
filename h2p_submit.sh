#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-01:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:1
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

SAVE_PATH="/ix1/pmayo/OneDrive/DATA/${1}_${2}_${3}/${1}_${2}_${3}.bin"
echo "SAVE_PATH = $SAVE_PATH"

# Run the KILOSORT_H2P function from the imported file
python -c "from KILOSORT_H2P import kilosort_h2p; kilosort_h2p('$SAVE_PATH')"

echo "DONE"
