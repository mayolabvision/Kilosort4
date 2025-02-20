import urllib.request
from pathlib import Path
from tqdm import tqdm
from kilosort.io import load_probe
from kilosort import run_kilosort

# Specify filepath of neuropixels data
DATA_PATH = Path('/ix1/pmayo/neuropixels/Ya_240415_s219_dirmem_withhelp_0003_g0_imec0/Ya_240415_s219_dirmem_withhelp_0003_g0_t0.imec0.ap.bin')
PROBE_PATH = Path('/ix1/pmayo/neuropixels/Ya_240415_s219_dirmem_withhelp_0003_g0_imec0/Ya_240415_s219_dirmem_withhelp_0003_g0_t0.imec0.ap_kilosortChanMap.mat') 

# If you want to test code with example dataset
'''
SAVE_PATH = Path('/ihome/pmayo/knoneman/Kilosort4/ex_results/ZFM-02370_mini.imec0.ap.bin')
URL = 'http://www.kilosort.org/downloads/ZFM-02370_mini.imec0.ap.bin'
download_url(URL, SAVE_PATH)

from kilosort.utils import download_probes
download_probes()

settings = {'data_dir': SAVE_PATH.parent, 'n_chan_bin': 385, 'probe_name': 'neuropixPhase3B1_kilosortChanMap.mat'}
'''

class DownloadProgressBar(tqdm):
    """ from https://stackoverflow.com/a/53877507 """
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)
def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

##############################################################################################
probe = load_probe(PROBE_PATH)
settings = {'data_dir': SAVE_PATH.parent, 'n_chan_bin': 385, 'probe': probe}

ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate = \
    run_kilosort(settings=settings)
