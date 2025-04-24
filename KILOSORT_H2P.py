from pathlib import Path
import shutil
from tqdm import tqdm
import numpy as np

from kilosort import run_kilosort, DEFAULT_SETTINGS
from kilosort.io import load_probe, save_preprocessing, load_ops

def kilosort_h2p(save_path,probe_path,drift_correction_type='kilosort',probe_type='np',save_tw=False):

    SAVE_PATH = Path(save_path)
    PROBE_PATH = Path(probe_path)
    
    probe = load_probe(probe_path)

    settings = DEFAULT_SETTINGS
    settings['probe'] = probe

    if probe_type == 'np':
        if drift_correction_type == 'kilosort':
            settings['nblocks'] = 1
            kilosort_path = SAVE_PATH.parent / 'kilosort4_ksDrift'
        elif drift_correction_type == 'medicine':
            settings['nblocks'] = 2
            kilosort_path = SAVE_PATH.parent / 'kilosort4_medicine'
        else:
            settings['nblocks'] = 0
            kilosort_path = SAVE_PATH.parent / 'kilosort4_baseline'

    settings['n_chan_bin'] = probe['n_chan']+1
    settings['fs'] = 30000
    settings['data_dir'] = SAVE_PATH.parent

    settings['duplicate_spike_ms'] = 0

    if probe_type == 'plex': 
        settings['batch_size'] = 60000*2 # 60000
        settings['nblocks'] = 0 
        settings['Th_universal'] = 9 # 9
        settings['Th_learned'] = 7   # 8

        settings['min_template_size'] = 10 #10
        settings['nearest_templates'] = 23 # 100
    
    if kilosort_path.exists() and kilosort_path.is_dir():
        shutil.rmtree(kilosort_path)

    if save_tw:
        ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe, results_dir=kilosort_path, save_preprocessed_copy=True, drift_correction_type=drift_correction_type)
    else:
        ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe, results_dir=kilosort_path, save_preprocessed_copy=False, drift_correction_type=drift_correction_type)
   
    print('%%%%%%%%%%%%%%% KILOSORT DONE RUNNING %%%%%%%%%%%%%%%')
