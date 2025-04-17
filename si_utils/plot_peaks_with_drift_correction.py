import matplotlib.pyplot as plt
from spikeinterface.sortingcomponents.motion import correct_motion_on_peaks

def plot_peaks_with_drift_correction(peaks,peak_locations,motion,rec,save_path=None):
    
    corrected_peak_locations = correct_motion_on_peaks(peaks, peak_locations, motion, rec)

    # check for drifts
    fs = rec.sampling_frequency
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(peaks['sample_index'] / fs, corrected_peak_locations['y'], color='k', marker='.', alpha=0.002)

    if save_path is not None:
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close(fig) 