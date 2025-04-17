import spikeinterface.full as si

def preprocess_for_drift_correction(rec, bad_channel_ids=None):
    rec1 = rec.astype('float32')
    
    rec2 = si.bandpass_filter(rec1, freq_min=300.0, freq_max=5000.0)
    rec3 = si.common_reference(rec2, reference="global", operator="median")

    if bad_channel_ids is not None:
        rec4 = rec3.remove_channels(bad_channel_ids)
        print('bad_channel_ids', bad_channel_ids)
    else:
        rec4 = rec3
    
    return rec4