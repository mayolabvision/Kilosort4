import os
import numpy as np
import sys

def get_params(i,params):
    line = np.loadtxt(params)[i]
    print(line)
    bs  = int(line[1])          # batch_size
    wh  = int(line[2])          # whitening_range
    tu  = int(line[3])          # Th_universal
    tl  = int(line[4])          # Th_learned
    at  = int(line[5])/100      # acg_threshold
    ct  = int(line[6])/100      # ccg_threshold
    return bs,wh,tu,tl,at,ct
 
def make_name(l,bs,wh,tu,tl,at,ct,dirpath):
    run_name = "{:05d}-bs{:03d}-wh{:03d}-tu{:02d}-tl{:02d}-at{:03d}-ct{:03d}".format(l,int(bs/30000),wh,tu,tl,int(at*100),int(ct*100))
    run_path = dirpath / 'kilosort4_sweep' / run_name
    run_path.mkdir(parents=True, exist_ok=True)
    return run_path

def make_name_from_lineID(line_id,params,dirpath):
    bs,wh,tu,tl,at,ct = get_params(int(line_id),params)
    run_path = make_name(int(line_id),bs,wh,tu,tl,at,ct,dirpath)
    
    return run_path

