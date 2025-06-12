from pathlib import Path
import shutil
from tqdm import tqdm
import numpy as np
import os

from kilosort import run_kilosort, DEFAULT_SETTINGS
from kilosort.io import load_probe, save_preprocessing, load_ops
import helpers

def kilosort_sweep(save_path,probe_path,line_id=0):
    SAVE_PATH = Path(save_path)
    PROBE_PATH = Path(probe_path)

    bs,wh,tu,tl,at,ct = helpers.get_params(int(line_id),'params.txt')
    kilosort_path = helpers.make_name(int(line_id),bs,wh,tu,tl,at,ct,SAVE_PATH.parent)

    probe = load_probe(probe_path)

    settings = DEFAULT_SETTINGS
    drift_correction_type  = 'none'
    with_whitening         =  True 
    save_preprocessed_copy =  False
    stop_after_motion      =  False
    settings['data_dir'] = SAVE_PATH.parent
    
    settings['tmax']                  =  4000 #sec
    
    # constant parameters
    settings['probe']                 =  probe
    settings['n_chan_bin']            =  probe['n_chan']+1
    settings['fs']                    =  30000
    settings['dminx']                 =  103
    settings['nblocks']               =  0
    settings['duplicate_spike_ms']    =  0
 
    # tunable parameters
    settings['batch_size']            =  bs
    settings['whitening_range']       =  wh
    settings['Th_universal']          =  tu 
    settings['Th_learned']            =  tl  
    settings['acg_threshold']         =  at
    settings['ccg_threshold']         =  ct
    
    if kilosort_path.exists() and kilosort_path.is_dir():
        shutil.rmtree(kilosort_path)

    ##########################################3
    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe, data_dtype='int16', results_dir=kilosort_path, save_preprocessed_copy=save_preprocessed_copy, drift_correction_type=drift_correction_type, with_whitening=with_whitening, stop_after_motion=stop_after_motion)
    ##########################################3
  
 
    print('%%%%%%%%%%%%%%% KILOSORT DONE RUNNING %%%%%%%%%%%%%%%')
