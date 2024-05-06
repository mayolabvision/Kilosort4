import urllib.request
from pathlib import Path
from tqdm import tqdm

# NOTE: Be sure to update this filepath if you want the data downloaded to
#       a specific location.
SAVE_PATH = Path('ZFM-02370_mini.imec0.ap.bin')

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

## CROPPED DATASET
URL = 'http://www.kilosort.org/downloads/ZFM-02370_mini.imec0.ap.bin'
download_url(URL, SAVE_PATH)

# Download channel maps for default probes
from kilosort.utils import download_probes
download_probes()

from kilosort import run_kilosort

# NOTE: 'n_chan_bin' is a required setting, and should reflect the total number
#       of channels in the binary file. For information on other available
#       settings, see `kilosort.run_kilosort.default_settings`.
settings = {'data_dir': SAVE_PATH.parent, 'n_chan_bin': 385}

ops, st, clu, tF, Wall, similar_templates, is_ref, est_contam_rate = \
    run_kilosort(settings=settings, probe_name='neuropixPhase3B1_kilosortChanMap.mat')
