import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from pathlib import Path
import shutil
import os

import spikeinterface.full as si  # import core only
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks
from spikeinterface.sortingcomponents.motion import correct_motion_on_peaks, estimate_motion, interpolate_motion

from probeinterface import ProbeGroup, write_prb

from kilosort import io

def si_h2p(spikeglx_folder,IMEC=0):

    #spikeglx_folder = f"/ix1/pmayo/lab_NHPdata/{IN1}/"

    motion_folder = str(Path(spikeglx_folder) / f"{Path(spikeglx_folder).name}_imec{IMEC}" / 'motion')
    DATA_DIRECTORY = Path(spikeglx_folder) / f"{Path(spikeglx_folder).name}_imec{IMEC}" / 'corrected'
    
    preprocess_folder = spikeglx_folder+"figs/preprocess"
    os.makedirs(preprocess_folder, exist_ok=True)

    stream_names, stream_ids = si.get_neo_streams('spikeglx', spikeglx_folder)

    ########################## READ RAW RECORDING ##########################
    RAW_REC = si.read_spikeglx(spikeglx_folder, stream_name=f'imec{IMEC}.ap', load_sync_channel=False)

    # we can estimate the noise on the scaled traces (microV) or on the raw one (which is in our case int16).
    noise_levels_microV = si.get_noise_levels(RAW_REC, return_scaled=True)
    noise_levels_int16 = si.get_noise_levels(RAW_REC, return_scaled=False)
    
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
    
    output_path = os.path.join(preprocess_folder, 'noise_dists.png')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig) 

    ########################## PREPROCESS RECORDING ##########################
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

    REC, bad_channel_ids = preprocess_recording(RAW_REC, save_path=preprocess_folder)

    probe_path = DATA_DIRECTORY / 'probe.prb'
    probe = REC.get_probe()  # From SpikeInterface tutorial, or recording.get_probe()
    pg = ProbeGroup()
    pg.add_probe(probe)
    write_prb(probe_path, pg)
    print(probe)

    noise_levels_int16 = si.get_noise_levels(REC, return_scaled=False)

    job_kwargs = dict(n_jobs=40, chunk_duration='1s', progress_bar=True)
    peaks = detect_peaks(REC,  method='locally_exclusive', noise_levels=noise_levels_int16,
                         detect_threshold=5, radius_um=50., **job_kwargs)
    peak_locations = localize_peaks(REC, peaks, method='center_of_mass', radius_um=50., **job_kwargs)

    # check for drifts
    fs = REC.sampling_frequency
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(peaks['sample_index'] / fs, peak_locations['y'], color='k', marker='.',  alpha=0.002)
    
    output_path = os.path.join(preprocess_folder, 'peak_times_depths1.png')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close(fig) 

    ########################## MOTION DETECTION ##########################
    def preprocess_for_drift_correction(raw_rec, bad_channel_ids):
        rec1 = raw_rec.astype('float32')
        
        rec2 = si.bandpass_filter(rec1, freq_min=300.0, freq_max=5000.0)
        rec3 = si.common_reference(rec2, reference="global", operator="median")
    
        rec4 = rec3.remove_channels(bad_channel_ids)
        print('bad_channel_ids', bad_channel_ids)
        
        return rec4

    FILT_REC1 = preprocess_for_drift_correction(RAW_REC, bad_channel_ids)
    DRIFT_REC = si.correct_motion(recording=FILT_REC1, preset="dredge", folder=motion_folder)

    motion_info = si.load_motion_info(motion_folder)
    motion = motion_info["motion"]

    fig = plt.figure(figsize=(14, 8))
    si.plot_motion_info(motion_info, FILT_REC1, figure=fig, depth_lim=(400, 1000), color_amplitude=True, amplitude_cmap="inferno", scatter_decimate=10,)
    
    output_path = os.path.join(preprocess_folder, 'motion_info.png')
    plt.savefig(output_path)
    plt.close(fig) 

    fig, axs = plt.subplots(ncols=2, figsize=(12, 8), sharey=True)
    ax = axs[0]
    si.plot_probe_map(FILT_REC1, ax=ax)
    
    peaks = motion_info["peaks"]
    sr = FILT_REC1.get_sampling_frequency()
    time_lim0 = 750.0
    time_lim1 = 1500.0
    mask = (peaks["sample_index"] > int(sr * time_lim0)) & (peaks["sample_index"] < int(sr * time_lim1))
    sl = slice(None, None, 5)
    amps = np.abs(peaks["amplitude"][mask][sl])
    amps /= np.quantile(amps, 0.95)
    c = plt.get_cmap("inferno")(amps)
    axs[0].set_title('Estimated peak locations (pre-dredge)')
    
    color_kargs = dict(alpha=0.2, s=2, c=c)
    
    peak_locations = motion_info["peak_locations"]
    # color='black',
    ax.scatter(peak_locations["x"][mask][sl], peak_locations["y"][mask][sl], **color_kargs)
    
    peak_locations2 = correct_motion_on_peaks(peaks, peak_locations, motion, FILT_REC1)
    
    ax = axs[1]
    si.plot_probe_map(FILT_REC1, ax=ax)
    #  color='black',
    ax.scatter(peak_locations2["x"][mask][sl], peak_locations2["y"][mask][sl], **color_kargs)
    axs[1].set_title('Corrected peak locations (post-dredge)')
    
    ax.set_ylim(400, 600)
    
    output_path = os.path.join(preprocess_folder, 'spatial_spread.png')
    plt.savefig(output_path)
    plt.close(fig)

    ########################## MOTION CORRECTION ##########################    
    REC_CORRECTED = interpolate_motion(recording=REC, motion=motion_info['motion'], **motion_info['parameters']['interpolate_motion_kwargs'])
    
    job_kwargs = dict(n_jobs=40, chunk_duration='1s', progress_bar=True)
    REC_CORRECTED = REC_CORRECTED.save(folder=DATA_DIRECTORY, format='binary', **job_kwargs)


    