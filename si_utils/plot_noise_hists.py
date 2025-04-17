import os
import matplotlib.pyplot as plt
import spikeinterface.full as si

def plot_noise_hists(rec, save_path=None)
# we can estimate the noise on the scaled traces (microV) or on the raw one (which is in our case int16).
    noise_levels_microV = si.get_noise_levels(rec, return_scaled=True)
    noise_levels_int16 = si.get_noise_levels(rec, return_scaled=False)
    
    print(noise_levels_int16.shape)

    # Create subplots side by side
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot scaled traces (microV)
    axes[0].hist(noise_levels_microV, bins=np.arange(5, 30, 2.5))
    axes[0].set_title('scaled traces (microV)')
    axes[0].set_xlabel('noise [microV]')
    
    # Plot raw traces (int16)
    axes[1].hist(noise_levels_int16, bins=np.arange(5, 30, 2.5))
    axes[1].set_title('raw traces (int16)')
    axes[1].set_xlabel('noise [int16 units]')

    if save_path is not None:
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close(fig) 