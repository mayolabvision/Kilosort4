from pathlib import Path
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.ndimage import gaussian_filter1d
from kilosort.io import load_ops
from kilosort.data_tools import (
    mean_waveform, cluster_templates, get_good_cluster, get_cluster_spikes, mean_waveform_with_bounds,
    get_spike_waveforms, get_best_channels)

######################################################################################
def plot_all_cluster_waveforms(results_dir, save_path, job_id=0, n_chunks=50):
    results_dir = Path(results_dir)

    clu = np.load(results_dir / 'spike_clusters.npy')
    cluster_ids, _ = np.sort(np.unique(clu, return_counts=True))
    
    chunks = np.array_split(cluster_ids, n_chunks)
    this_chunk = chunks[job_id]
    print(this_chunk)
 
    for i, cluster_id in enumerate(this_chunk):
        print(f"Index {i}, Cluster {cluster_id}")
        plot_cluster_waveforms(results_dir, cluster_id=cluster_id, save_path=save_path)

def plot_cluster_waveforms(results_dir, cluster_id=False, save_path=False):
    results_dir = Path(results_dir)
    match = re.search(r'imec(\d+)', str(results_dir))
    imec = f'imec{match.group(1)}' if match else 'imecX'  # fallback in case not found
    imec_num = int(re.search(r'\d+', imec).group()) if re.search(r'\d+', imec) else -1
    hemisphere = "Left" if imec_num == 0 else "Right" if imec_num == 1 else "Unknown"

    run_type = results_dir.name.replace("kilosort4_", "") if results_dir.name.startswith("kilosort4_") else "unknown"
    session_name = results_dir.parent.parent.name

    ops = load_ops(results_dir / 'ops.npy')
    t = (np.arange(ops['nt']) / ops['fs']) * 1000

    #all_spike_times = np.load(results_dir / 'spike_times.npy')
    #cluster_id = get_good_cluster(results_dir, n=1)
        
    chan = get_best_channels(results_dir)[cluster_id]

    if save_path:
        save_path = Path(save_path)  # replace with actual path
        save_path.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
        
        filename = f"imec{imec_num}_unit{cluster_id:04d}_chan{chan:03d}.png"
        full_path = save_path / filename

        if full_path.exists():
            print(f"Figure already exists: {full_path}, skipping.")
            return  # Exit early if figure already exists

    # Mean waveform, template
    mean_wv, lower_bnd, upper_bnd, spike_subset = mean_waveform_with_bounds(cluster_id, results_dir, n_spikes=np.inf, bfile=None, best=True)
    mean_temp = cluster_templates(cluster_id, results_dir, mean=True, best=True, spike_subset=spike_subset)

    # Pull out a subset of spikes to plot
    subset_spike_times, _ = get_cluster_spikes(cluster_id, results_dir, n_spikes=1000)
    subset_waves = get_spike_waveforms(subset_spike_times, results_dir, chan=chan)
    t2 = (subset_spike_times / ops['fs']) / 60

    # Pull out all spikes
    #spike_times, _ = get_cluster_spikes(cluster_id, results_dir, n_spikes=np.inf)
    #waves = get_spike_waveforms(spike_times, results_dir, chan=chan)
    #t3 = (spike_times / ops['fs'])

    #########################################################################################################
    plt.rcParams.update({'font.size': 14})
    
    # Define a 3x2 grid + 1x1 bottom row (4 total rows)
    fig = plt.figure(figsize=(20, 15))
    gs = gridspec.GridSpec(2, 3, figure=fig, width_ratios=[1.5, 1, 0.5])
    
    # Row 1
    ax0_0 = fig.add_subplot(gs[0, 0])  # Top-left
    ax0_1 = fig.add_subplot(gs[0:2, 1])  # This spans ONLY rows 0 and 1 in col 1
    
    # Row 2
    ax1_0 = fig.add_subplot(gs[1, 0])  # Bottom-left of 2x2 top section
    
    # Col 3 (spanning both rows)
    ax01_2 = fig.add_subplot(gs[0:2, 2])  # Entire bottom row, spans both columns

    # Row 3
    #ax2 = fig.add_subplot(gs[2, 0:3])
    
    #############################################
    # First plot: waveform traces
    for i in range(subset_waves.shape[1]):
        ax0_0.plot(t, subset_waves[:, i], linewidth=1, linestyle='solid', color='gray', label='single-spike waveform')
    
    ax0_0.plot(t, mean_wv, c='black', linestyle='solid', linewidth=3, label='mean waveform')
    ax0_0.set_xlabel('Time (ms)')
    ax0_0.set_ylabel('Voltage (µV)')
    ax0_0.set_title('Sample Waveforms (1000 spikes) and Mean Waveform')
    ax0_0.spines['top'].set_visible(False)
    ax0_0.spines['right'].set_visible(False)
    
    #############################################
    # Second plot: mean ± std and template
    ax1_0.fill_between(t, lower_bnd, upper_bnd, color='gray', alpha=0.25, label='±1 STD')
    ax1_0.plot(t, mean_wv, c='black', linestyle='solid', linewidth=3, label='mean waveform')
    ax1_0.plot(t, mean_temp, linewidth=2, label='template')
    ax1_0.set_xlabel('Time (ms)')
    ax1_0.set_ylabel('Voltage (µV)')
    ax1_0.spines['top'].set_visible(False)
    ax1_0.spines['right'].set_visible(False)
    ax1_0.legend()
    
    #############################################
    # Third plot: heatmap (spanning right column)
    pos = ax0_1.imshow(subset_waves.T, aspect='auto', extent=[t[0], t[-1], t2[0], t2[-1]])
    cbar = fig.colorbar(pos, ax=ax0_1, fraction=0.046, pad=0.04, shrink=0.8)
    cbar.set_label('Voltage (µV)', rotation=270, labelpad=15)
    ax0_1.set_xlabel('Time (ms)')
    ax0_1.set_ylabel('Spike time (min)')
    ax0_1.set_title('Waveform Evolution Across Recording')
    
    #############################################
    # Fourth plot: MSE over time (spans both columns)
    scores, times = np.zeros(subset_waves.shape[1]), np.zeros(subset_waves.shape[1])
    for i in range(subset_waves.shape[1]):
        times[i] = t2[i]
        scores[i] = wave_diff(subset_waves[:, i], mean_wv)
        
    ax01_2.plot(gaussian_filter1d(scores, sigma=3), times, linestyle='-', color='black')
    ax01_2.axvline(x=0, linestyle='--', color='gray', linewidth=1)
    ax01_2.set_xlabel('MSE (µV²)')
    ax01_2.set_ylim([t2.min(), t2.max()])
    ax01_2.spines['top'].set_visible(False)
    ax01_2.spines['right'].set_visible(False)
    
    #############################################
    
    # spike_times is in seconds
    #bin_size = 10  # seconds
    #duration = all_spike_times.max()
    #bins = np.arange(0, duration + bin_size, bin_size)
    #counts, _ = np.histogram(t3, bins=bins)
    #firing_rates = counts / bin_size

    #bin_centers = (bins[:-1] + bins[1:]) / 2
    
    #ax2.plot(bin_centers / 60, firing_rates, color='black')
    #ax2.set_xlabel('Time (min)')
    #ax2.set_ylabel('Firing Rate (Hz)')
    #ax2.set_title('Firing Rate Across Recording (10 sec Bins)')
    
    title_str = f"{session_name}_{run_type} --- {hemisphere} --- cluster {cluster_id} (channel {chan})"
    fig.suptitle(title_str, fontsize=22, y=1.02)
    fig.tight_layout()

    if save_path:
        fig.savefig(full_path, dpi=300, bbox_inches='tight')
        
    #########################################################################################################

def wave_diff(a, b):
    a = np.asarray(a)
    b = np.asarray(b)
    mse = np.mean((a - b) ** 2)
    return mse  # Lower means more similar
