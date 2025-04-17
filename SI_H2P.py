import numpy as np
from pathlib import Path
import os

import spikeinterface.full as si
from spikeinterface.sortingcomponents.motion import correct_motion_on_peaks, interpolate_motion
from si_utils import *

#------------------------------------------------------------------------------------------------------------#
def si_h2p(spikeglx_folder, IMEC=0, drift_preset="dredge", plot_figs=False):
    
    print("Step 1: Setting up folders and reading raw recording...")
    motion_folder, figs_folder = make_folder_paths(spikeglx_folder, IMEC, drift_preset)
    stream_names, stream_ids = si.get_neo_streams('spikeglx', spikeglx_folder)
    RAW_RECORDING = si.read_spikeglx(spikeglx_folder, stream_name=f'imec{IMEC}.ap', load_sync_channel=False)

    ######################################### PROCESS RAW RECORDING ##########################################
    print("Step 2: Preprocessing raw recording...")
    if plot_figs:
        plot_noise_hists(RAW_RECORDING, save_path=os.path.join(figs_folder, 'noise_dists.png'))
        RECORDING, bad_channel_ids = preprocess_recording(RAW_RECORDING, save_path=figs_folder)
        peaks, peak_locations = plot_peaks_from_recording(
            RECORDING, save_path=os.path.join(figs_folder, 'peak_times_depths1.png'))
    else:
        RECORDING, bad_channel_ids = preprocess_recording(RAW_RECORDING)

    probe_path = motion_folder / 'probe.prb'
    make_probe_from_recording(RECORDING, probe_path)

    ############################################# ESTIMATE DRIFT #############################################
    print("Step 3: Estimating and applying motion correction...")
    filt1_recording = preprocess_for_drift_correction(RAW_RECORDING, bad_channel_ids=bad_channel_ids)
    drift_recording, motion, motion_info = si.correct_motion(
        recording=filt1_recording,
        preset=drift_preset,
        interpolate_motion_kwargs={'border_mode': 'force_extrapolate'},
        folder=motion_folder)

    if plot_figs:
        plot_motion_correction(RECORDING, motion_info, save_path=os.path.join(figs_folder, 'motion_info.png'))
    
    ########################################### INTERPOLATE DRIFT ########################################### 
    REC_CORRECTED = si.interpolate(
        recording=RECORDING,
        motion=motion,
        **motion_info['parameters']['interpolate_motion_kwargs'])

    if plot_figs:
        plot_peaks_with_drift_correction(
            peaks,
            peak_locations,
            motion,
            RECORDING,
            save_path=os.path.join(figs_folder, 'peak_times_depths2.png'))

    ######################################## SAVE CORRECTED RECORDING ########################################
    print("Step 4: Saving drift-corrected recording to disk...")
    job_kwargs = dict(n_jobs=40, chunk_duration='1s', progress_bar=True)
    REC_CORRECTED = REC_CORRECTED.save(folder=motion_folder, format='binary', **job_kwargs)

    print("Step 5: Done! Drift-corrected recording saved successfully.")

#------------------------------------------------------------------------------------------------------------#