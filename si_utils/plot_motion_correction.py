import os
import matplotlib.pyplot as plt
import spikeinterface.full as si

def plot_motion_correction(rec,motion_info,save_path=None):
    
    fig = plt.figure(figsize=(14, 8))
    si.plot_motion_info(motion_info, rec, figure=fig, depth_lim=(400, 1000), color_amplitude=True, amplitude_cmap="inferno", scatter_decimate=10,)

    if save_path is not None:
        plt.savefig(save_path)
        plt.close(fig) 