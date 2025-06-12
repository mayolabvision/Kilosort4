from pathlib import Path
import shutil
from tqdm import tqdm
import numpy as np
import os

from kilosort import run_kilosort, DEFAULT_SETTINGS
from kilosort.io import load_probe, save_preprocessing, load_ops

def kilosort_h2p(save_path,probe_path,run_type='unleashed',probe_type='np',tmax=None):

    SAVE_PATH = Path(save_path)
    PROBE_PATH = Path(probe_path)
    
    probe = load_probe(probe_path)

    settings = DEFAULT_SETTINGS
    settings['probe']      =  probe
    settings['n_chan_bin'] =  probe['n_chan']+1
    settings['fs']         =  30000

    if probe_type == 'np': #assuming NHP-Long probe
        settings['dminx'] = 103
     
        if run_type == 'unleashed': # first pass, let kilosort do its thing
            kilosort_path          =  SAVE_PATH.parent / 'kilosort4_unleashed'
            drift_correction_type  = 'none'
            with_whitening         =  True 
            save_preprocessed_copy =  False
            stop_after_motion      =  False

            settings['nblocks']    =  0

        elif run_type == 'detect_motion': # first pass, just detect motion 
            kilosort_path          = SAVE_PATH.parent / 'motion'
            drift_correction_type  = 'medicine'
            with_whitening         =  True 
            save_preprocessed_copy =  False
            stop_after_motion      =  True

            settings['nblocks']    =  1

        elif run_type == 'refined':
            kilosort_path          = SAVE_PATH.parent / 'kilosort4_refined'
            drift_correction_type  = 'none'
            with_whitening         =  True
            save_preprocessed_copy =  False
            stop_after_motion      =  False

            settings['nblocks']              =  0
            settings['whitening_range']      =  12
            settings['acg_threshold']        =  0.01
            settings['ccg_threshold']        =  0.01 
            settings['duplicate_spike_ms']   =  0
            settings['save_preprocessed_copy']   =  False
            
    settings['data_dir'] = SAVE_PATH.parent

    ########## time cutoff ############
    if tmax is not None:
        settings['tmax'] = tmax

    '''
    if probe_type == 'plex': 
        settings['batch_size'] = 60000*2 # 60000
        settings['nblocks'] = 0 
        settings['Th_universal'] = 9 # 9
        settings['Th_learned'] = 7   # 8

        settings['min_template_size'] = 10 #10
        settings['nearest_templates'] = 23 # 100

        save_tw = True
    '''

    if kilosort_path.exists() and kilosort_path.is_dir():
        shutil.rmtree(kilosort_path)

    ##########################################3
    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe, data_dtype='int16', results_dir=kilosort_path, save_preprocessed_copy=save_preprocessed_copy, drift_correction_type=drift_correction_type, with_whitening=with_whitening, stop_after_motion=stop_after_motion)
    ##########################################3
  
 
    print('%%%%%%%%%%%%%%% KILOSORT DONE RUNNING %%%%%%%%%%%%%%%')
