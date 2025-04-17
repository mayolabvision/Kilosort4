from pathlib import Path
import os

def make_folder_paths(spikeglx_folder,IMEC,drift_preset):
    #motion_folder = str(Path(spikeglx_folder) / f"{Path(spikeglx_folder).name}_imec{IMEC}" / drift_preset)
    motion_folder = Path(spikeglx_folder) / f"{Path(spikeglx_folder).name}_imec{IMEC}" / 'corrected'
    
    figs_folder = spikeglx_folder+"figs/preprocess"
    os.makedirs(figs_folder, exist_ok=True)

    return motion_folder, figs_folder