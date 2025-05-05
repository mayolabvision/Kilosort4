from pathlib import Path
import numpy as np
import pandas as pd
from kilosort.io import load_ops

def make_cluster_summary_table(results_dir):
    """
    Load summary information from a Kilosort4 results directory and save it as a CSV.

    Parameters:
        results_dir (str or Path): Path to the Kilosort4 output directory.

    Returns:
        pd.DataFrame: Summary dataframe with cluster metadata.
    """
    results_dir = Path(results_dir)
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

    cluster_ids, spike_counts = np.unique(clu, return_counts=True)
    firing_rates = spike_counts * fs / st.max()

    depth = np.array([
        pos[clu == i, 1].mean() if np.any(clu == i) else np.nan
        for i in cluster_ids
    ])

    df = pd.DataFrame.from_dict({
        'cluster': cluster_ids,
        'chan': chan_best,
        'depth': depth,
        'fr': firing_rates,
        'amp': template_amplitudes,
        'n_spikes': spike_counts
    }).set_index('cluster')

    # Save to CSV
    csv_path = results_dir / 'cluster_summary.csv'
    df.to_csv(csv_path)

    print(f"Saved cluster summary to: {csv_path}")
