import os
import matplotlib.pyplot as plt
import spikeinterface.full as si

def preprocess_recording(raw_rec, save_path=None):
    raw_rec = raw_rec.astype('float32')
    
    rec1 = si.highpass_filter(raw_rec, freq_min=400.)
    bad_channel_ids, channel_labels = si.detect_bad_channels(rec1)
    rec2 = rec1.remove_channels(bad_channel_ids)
    print('bad_channel_ids', bad_channel_ids)
    
    rec3 = si.phase_shift(rec2)
    rec4 = si.common_reference(rec3, operator="median", reference="global")
    rec = rec4

    if save_path is not None:
        # here we use static plot using matplotlib backend
        fig, axs = plt.subplots(ncols=3, figsize=(20, 10))
        
        si.plot_traces(rec1, backend='matplotlib',  clim=(-50, 50), ax=axs[0])
        si.plot_traces(rec3, backend='matplotlib',  clim=(-50, 50), ax=axs[1])
        si.plot_traces(rec4, backend='matplotlib',  clim=(-50, 50), ax=axs[2])
        for i, label in enumerate(('hp filter', 'phase shift', 'cmr')):
            axs[i].set_title(label)
    
        
            output_path = os.path.join(save_path, 'preprocess_steps.png')
            plt.tight_layout()
            plt.savefig(output_path)
    
        # plot some channels
        fig, ax = plt.subplots(figsize=(20, 10))
        some_chans = rec.channel_ids[[100, 150, 200, ]]
        si.plot_traces({'filter':rec1, 'cmr': rec4}, backend='matplotlib', mode='line', ax=ax, channel_ids=some_chans)

        output_path = os.path.join(save_path, 'preprocess_chans.png')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close(fig) 

    return rec, bad_channel_ids