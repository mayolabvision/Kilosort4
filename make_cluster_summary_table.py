from pathlib import Path
import numpy as np
import pandas as pd
import datetime
import time
import os
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from kilosort.io import load_ops
from kilosort.data_tools import (get_cluster_spikes, get_spike_waveforms, get_best_channels, get_best_channel)

def make_cluster_summary_table(results_dir, job_id=0, n_chunks=1):
    # Initialize cluster_summary 
    start_time = time.time()
    results_dir = Path(results_dir)

    clusters_dir = results_dir / 'clusters'
    clusters_dir.mkdir(exist_ok=True)

    # Pull out details from kilosort results
    ops = load_ops(results_dir / 'ops.npy')

    fs = ops['fs']
    chan_map = np.load(results_dir / 'channel_map.npy')
    templates = np.load(results_dir / 'templates.npy')
    chan_best = (templates**2).sum(axis=1).argmax(axis=-1)
    chan_best = chan_map[chan_best]

    template_amplitudes = np.sqrt((templates**2).sum(axis=(-2, -1)))
    st = np.load(results_dir / 'spike_times.npy')
    clu = np.load(results_dir / 'spike_clusters.npy')
    pos = np.load(results_dir / 'spike_positions.npy')

    # Identify cluster_ids 
    cluster_ids, spike_counts = np.unique(clu, return_counts=True)
    print(f"There are {len(cluster_ids)} clusters total.")

    firing_rates = spike_counts * fs / st.max()
    xpos = np.array([pos[clu == i, 0].mean() if np.any(clu == i) else np.nan for i in cluster_ids])
    ypos = np.array([pos[clu == i, 1].mean() if np.any(clu == i) else np.nan for i in cluster_ids])
    
    chunks = np.array_split(cluster_ids, n_chunks)
    this_chunk = chunks[job_id]
    print(f"Have {len(this_chunk)} clusters to process in this chunk.")
    
    for i, cluster_id in enumerate(this_chunk):
        cluster_file = clusters_dir / f'cluster_{int(cluster_id):04d}.npy'
        if not cluster_file.exists():
            print(f".....Cluster {cluster_id}.....\n")
            snr, mean_wf, std_wf, spike_times, waves, first_spike, last_spike, drift_mses= get_cluster_snr(results_dir, cluster_id)
            
            max_drift_mse = np.max(drift_mses[1:]) if len(drift_mses) > 1 else 0  # skip first self-comparison

            cluster_data = {
                'cluster_id': cluster_id,
                'channel_id': chan_best[cluster_id],
                'x_pos': xpos[cluster_id],
                'y_pos': ypos[cluster_id],
                'temp_amp': template_amplitudes[cluster_id],
                'fr_hz': firing_rates[cluster_id],
                'n_spikes': spike_counts[cluster_id],
                'snr': snr,
                'mean_wf': mean_wf,
                'std_wf': std_wf,
                'spike_times': spike_times,
                'waveforms': waves,
                'first_spike_sec': first_spike,
                'last_spike_sec': last_spike,
                'drift_mses': drift_mses,
                'max_drift_mse': max_drift_mse
            }

            np.save(cluster_file, cluster_data, allow_pickle=True)
            
            elapsed_time = (time.time() - start_time) / 60
            print(f"Cluster {cluster_id}: SNR = {snr:.4f}, Time = {elapsed_time:.4f} min\n")
        else:
            print(f"Cluster {cluster_id} already exists\n")

def get_cluster_snr(results_dir, cluster_id, fs=30000, drift_bin_sec=600):
    results_dir = Path(results_dir)
    ops = load_ops(results_dir / 'ops.npy')

    chan = get_best_channel(results_dir, cluster_id)

    spike_times, _ = get_cluster_spikes(cluster_id, results_dir, n_spikes=np.inf)
    waves = get_spike_waveforms(spike_times, results_dir, chan=chan)
    waves = waves.astype(np.float64)  # shape: (nt, n_spikes)

    if waves.size == 0:
        return np.nan, None, np.array([]), np.array([]), np.array([]), np.nan, np.nan, []
    
    # Fix potential mismatch caused by data cropping at the end
    n_waves = waves.shape[1]
    if len(spike_times) > n_waves:
        spike_times = spike_times[:n_waves]

    mean_wave = np.mean(waves, axis=1)  # (nt,)
    std_wave = np.std(waves, axis=1)    # (nt,)

    A = np.max(mean_wave) - np.min(mean_wave)
    noise = waves - mean_wave[:, np.newaxis]
    snr = A / (2 * np.std(noise.flatten()))

    # First and last spike times in seconds
    spike_times_sec = spike_times / fs
    first_spike_sec = float(spike_times_sec[0])
    last_spike_sec = float(spike_times_sec[-1])

    # Drift analysis: compare mean waveforms in successive 10-minute bins
    drift_bin_samples = drift_bin_sec * fs
    total_spikes = len(spike_times)
    drift_mses = []

    # Get bin edges starting from the first spike
    min_time = spike_times[0]
    max_time = spike_times[-1]
    bin_edges = np.arange(min_time, max_time + drift_bin_samples, drift_bin_samples)

    # Bin waveforms
    binned_means = []
    for i in range(len(bin_edges) - 1):
        start, end = bin_edges[i], bin_edges[i + 1]
        mask = (spike_times >= start) & (spike_times < end)
        if np.sum(mask) > 0:
            mean_bin_wave = np.mean(waves[:, mask], axis=1)
            binned_means.append(mean_bin_wave)

    # Compute MSE from first window
    if binned_means:
        base_wave = binned_means[0]
        drift_mses = [mean_squared_error(base_wave, w) for w in binned_means]

    return snr, mean_wave, std_wave, spike_times, waves, first_spike_sec, last_spike_sec, drift_mses

def merge_clusters_to_csv(results_dir):
    results_dir = Path(results_dir)
    clusters_dir = results_dir / 'clusters'
    cluster_files = sorted(clusters_dir.glob('cluster_*.npy'))

    # Extract cluster_ids from filenames first
    cluster_ids = [int(f.stem.split('_')[-1]) for f in cluster_files]

    if not cluster_ids:
        print("No cluster .npy files found.")
        return

    expected_count = max(cluster_ids) + 1
    actual_count = len(cluster_ids)

    if actual_count != expected_count:
        print(f"Mismatch in cluster count: found {actual_count} .npy files, "
              f"but maximum cluster_id is {max(cluster_ids)} "
              f"(expected {expected_count} files).")
        print("Aborting: one or more cluster files are missing.")
        return

    # If counts match, proceed with loading
    records = []
    for cluster_file in cluster_files:
        cluster_id_str = cluster_file.stem.split('_')[-1]
        cluster_id = int(cluster_id_str)
        print(f".....Cluster {cluster_id}.....\n")

        cluster_data = np.load(cluster_file, allow_pickle=True).item()
        selected_data = {
            'cluster_id': cluster_id,
            'channel_id': cluster_data.get('channel_id'),
            'x_pos': cluster_data.get('x_pos'),
            'y_pos': cluster_data.get('y_pos'),
            'temp_amp': cluster_data.get('temp_amp'),
            'fr_hz': cluster_data.get('fr_hz'),
            'n_spikes': cluster_data.get('n_spikes'),
            'snr': cluster_data.get('snr'),
            'first_spike_sec': cluster_data.get('first_spike_sec'),
            'last_spike_sec': cluster_data.get('last_spike_sec'),
            'max_drift_mse': cluster_data.get('max_drift_mse')
        }
        records.append(selected_data)

    df = pd.DataFrame(records)
    df = df.sort_values(by='cluster_id').reset_index(drop=True)

    csv_path = results_dir / 'cluster_summary.csv'
    df.to_csv(csv_path, index=False)
    print(f"Saved merged cluster summary to {csv_path}")
