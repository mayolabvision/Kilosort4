#!/bin/bash -l
#SBATCH --nodes=1
#SBATCH --time=0-09:00:00
#SBATCH --ntasks-per-node=4
#SBATCH --gres=gpu:2
#SBATCH --cluster=gpu
#SBATCH --partition=a100
#SBATCH --constraint=40g
#SBATCH --job-name=si
#SBATCH --error=/ix1/pmayo/kilosort/outfiles/out_%A.err
#SBATCH --output=/ix1/pmayo/kilosort/outfiles/out_%A.out
#SBATCH --mail-type=fail
#SBATCH --mail-user=knoneman@pitt.edu

# INPUTS = FILENAME, IMEC
module purge
conda activate /ihome/pmayo/knoneman/.conda/envs/kilosort

SPIKEGLX_PATH="/ix1/pmayo/lab_NHPdata/${1}"
echo "SPIKEGLX_PATH= $SPIKEGLX_PATH"

# Run the SI_H2P function from the imported file
python -c "import sys; sys.path.append('/ihome/pmayo/knoneman/Packages/Kilosort4'); from SI_H2P import si_h2p; si_h2p('$SPIKEGLX_PATH', IMEC=${2})"

echo "DONE"