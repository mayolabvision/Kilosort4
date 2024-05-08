import urllib.request
from pathlib import Path
from tqdm import tqdm
from kilosort.io import load_probe
from kilosort import run_kilosort

dat = 1

# NOTE: Be sure to update this filepath if you want the data downloaded to
#       a specific location.
if dat==0:
    SAVE_PATH = Path('ZFM-02370_mini.imec0.ap.bin')
elif dat==1:
    SAVE_PATH = Path('/Users/kendranoneman/OneDrive_cmu/neuropixels/Ya_240415_s219_dirmem_withhelp_0003_g0_t0.imec0.ap.bin')

class DownloadProgressBar(tqdm):
    """ from https://stackoverflow.com/a/53877507 """
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)
def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

## FULL DATASET (download locally then decompress)
# compressed using mtscomp (https://github.com/int-brain-lab/mtscomp)
# URL = 'https://ibl.flatironinstitute.org/public/mainenlab/Subjects/ZFM-02370/2021-04-28/001/raw_ephys_data/probe00/_spikeglx_ephysData_g0_t0.imec0.ap.e510da60-53e0-4e00-b369-3ea16c45623a.cbin'

if dat==0:
    ## FULL DATASET (download locally then decompress)
    #compressed using mtscomp (https://github.com/int-brain-lab/mtscomp)
    URL = 'https://ibl.flatironinstitute.org/public/mainenlab/Subjects/ZFM-02370/2021-04-28/001/raw_ephys_data/probe00/_spikeglx_ephysData_g0_t0.imec0.ap.e510da60-53e0-4e00-b369-3ea16c45623a.cbin'
    ## CROPPED DATASET
    #URL = 'http://www.kilosort.org/downloads/ZFM-02370_mini.imec0.ap.bin'
    #download_url(URL, SAVE_PATH)

    from kilosort.utils import download_probes
    download_probes()
    
    settings = {'data_dir': SAVE_PATH.parent, 'n_chan_bin': 385, 'probe_name': 'neuropixPhase3B1_kilosortChanMap.mat'}
    
    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate = \
        run_kilosort(settings=settings)

elif dat==1:
    from kilosort.io import load_probe
    probe = load_probe('/Users/kendranoneman/OneDrive_cmu/neuropixels/Ya_240415_s219_dirmem_withhelp_0003_g0_t0.imec0.ap_kilosortChanMap.mat')

    settings = {'data_dir': SAVE_PATH.parent, 'n_chan_bin': 385, 'probe': probe}

    ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate = \
        run_kilosort(settings=settings, probe=probe)
