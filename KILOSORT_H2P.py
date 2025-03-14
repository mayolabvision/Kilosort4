from pathlib import Path
import shutil
from tqdm import tqdm
import numpy as np

from kilosort import run_kilosort, DEFAULT_SETTINGS
from kilosort.io import save_preprocessing, load_ops

def kilosort_h2p(save_path):
    SAVE_PATH = Path(save_path)

    n_chan = 24
    chanMap = np.arange(n_chan)
    kcoords = np.zeros(n_chan)
    xc = np.ones(n_chan)*7.5
    yc = np.array([7.5 + 150*i for i in range(n_chan)])

    probe = {
        'chanMap': chanMap,
        'xc': xc,
        'yc': yc[::-1],
        'kcoords': kcoords,
        'n_chan': n_chan}

    settings = DEFAULT_SETTINGS
    settings['probe'] = probe
    settings['n_chan_bin'] = 24
    settings['fs'] = 30000
    settings['data_dir'] = SAVE_PATH.parent

    settings['nskip']

    settings['batch_size'] = 60000*2 # 60000
    settings['nblocks'] = 0 # 1
    settings['Th_universal'] = 8 # 9
    settings['Th_learned'] = 8   # 8

    settings['min_template_size'] = 10 #10
    settings['nearest_templates'] = 23 # 100
    print(settings)
    
    kilosort_path = SAVE_PATH.parent / 'kilosort4'
    temp_wh_path = SAVE_PATH.parent / 'temp_wh.dat'

    if kilosort_path.exists() and kilosort_path.is_dir():
        shutil.rmtree(kilosort_path)

    if temp_wh_path.exists() and temp_wh_path.is_file():
        temp_wh_path.unlink()   


    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate, kept_spikes = run_kilosort(settings=settings, probe=probe)

    ops_path = SAVE_PATH.parent / 'kilosort4' / 'ops.npy'
    ops = load_ops(ops_path)
    save_preprocessing(SAVE_PATH.parent / 'temp_wh.dat', ops, bfile_path=SAVE_PATH)



