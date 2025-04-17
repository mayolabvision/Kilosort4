import os
import matplotlib.pyplot as plt
import spikeinterface.full as si

from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

def plot_peaks_from_recording(rec,save_path=None):
    noise_levels_int16 = si.get_noise_levels(rec, return_scaled=False)

    job_kwargs = dict(n_jobs=40, chunk_duration='1s', progress_bar=True)
    peaks = detect_peaks(rec,  method='locally_exclusive', noise_levels=noise_levels_int16,
                         detect_threshold=5, radius_um=50., **job_kwargs)
    peak_locations = localize_peaks(rec, peaks, method='center_of_mass', radius_um=50., **job_kwargs)

    # check for drifts
    fs = rec.sampling_frequency
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(peaks['sample_index'] / fs, peak_locations['y'], color='k', marker='.',  alpha=0.002)

    if save_path is not None:
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close(fig) 

    return peaks, peak_locations