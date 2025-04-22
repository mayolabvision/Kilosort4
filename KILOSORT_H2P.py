from pathlib import Path
import shutil
from tqdm import tqdm
import numpy as np

from kilosort import run_kilosort, DEFAULT_SETTINGS
from kilosort.io import load_probe, save_preprocessing, load_ops

def kilosort_h2p(save_path,probe_path,nblocks=0,run_ks=True,temp_wh=True):

    SAVE_PATH = Path(save_path)
    PROBE_PATH = Path(probe_path)
    
    if run_ks:
        probe = load_probe(probe_path)

        settings = DEFAULT_SETTINGS
        settings['probe'] = probe
        settings['nblocks'] = nblocks
    
        settings['n_chan_bin'] = probe['n_chan']+1
        settings['fs'] = 30000
        settings['data_dir'] = SAVE_PATH.parent

        #settings['nskip']

        #settings['batch_size'] = 60000*2 # 60000
        #settings['nblocks'] = 1 # 1
        #settings['Th_universal'] = 9 # 9
        #settings['Th_learned'] = 7   # 8

        #settings['min_template_size'] = 10 #10
        #settings['nearest_templates'] = 23 # 100
        
        kilosort_path = SAVE_PATH.parent / 'kilosort4'

        if kilosort_path.exists() and kilosort_path.is_dir():
            shutil.rmtree(kilosort_path)

        ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe)
       
    if temp_wh: 
        ops_path = SAVE_PATH.parent / 'kilosort4' / 'ops.npy'
        ops = load_ops(ops_path)
        
        temp_wh_path = SAVE_PATH.parent / 'temp_wh.dat'
        if temp_wh_path.exists() and temp_wh_path.is_file():
            temp_wh_path.unlink()   
        
        print('%%%%%%%%%%%%%%% WRITING TO TEMP_WH.DAT %%%%%%%%%%%%%%%')
        save_preprocessing(SAVE_PATH.parent / 'temp_wh.dat', ops, bfile_path=SAVE_PATH)
        print('%%%%%%%%%%%%%%% DONE WRITING TO TEMP_WH.DAT %%%%%%%%%%%%%%%')
