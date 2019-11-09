#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  Arnaud Desvachez --<arnaud.desvachez@gmail.com>
  Purpose: Trainer protocol for deep meditation state neurofeedback
  
  It finds the subject's alpha and theta peaks, define the alpha and
  theta bands and compute the referencePSD in both alpha and theta bands.
  
  Created: 16.10.2019
"""
import sys
import os

import numpy as np
import multiprocessing as mp
from importlib import import_module
import mne
import microstates

import pycnbi.decoder.features as features

import pycnbi.utils.pycnbi_utils as pu

from pycnbi import logger
from pycnbi.triggers.trigger_def import trigger_def
from pycnbi.gui.streams import redirect_stdout_to_queue


#----------------------------------------------------------------------
def check_config(cfg):
    """
    Ensure that the config file contains the parameters
    """
    critical_vars = {
        'COMMON': ['DATA_PATH'],
    }
    optional_vars = {
    }
    
    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError
    
    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))
    
    return cfg

#----------------------------------------------------------------------
def run(cfg, state=mp.Value('i', 1), queue=None):
    """
    Training protocol for Alpha/Theta neurofeedback.
    """
    redirect_stdout_to_queue(logger, queue, 'INFO')

    # add tdef object
    cfg.tdef = trigger_def(cfg.TRIGGER_FILE)

    # Extract features
    if not state.value:
        sys.exit(-1)

    raw = mne.io.read_raw_brainvision(cfg.DATA_PATH, preload=True)
    outfile = cfg.OUT_MICROSTATES_FILE

    ch_names = ['P3', 'C3', 'F3', 'Fz', 'F4', 'C4', 'P4', 'Cz', 'Pz', 'Fp1', 'Fp2', 'T3', 'T5', 'O1', 'O2', 'F7', 'F8',
                'T6', 'T4']
    raw.pick_channels(ch_names)

    raw.set_montage('standard_1005')
    raw.set_eeg_reference('average')
    raw.filter(1, 30)
    maps, segmentation = microstates.segment(raw.get_data(), n_states=4, max_n_peaks=10000000, max_iter=5000,
                                             normalize=True)
    np.savetxt(outfile, maps, delimiter=" ")
    #----------------------------------------------------------------------        
    # ADD YOUR CODE HERE
    #----------------------------------------------------------------------


# ----------------------------------------------------------------------
def load_config(cfg_file):
    """
    Dynamic loading of a config file.
    Format the lib to fit the previous developed pycnbi code if subject specific file (not for the templates).
    cfg_file: tuple containing the path and the config file name.
    """
    cfg_file = os.path.split(cfg_file)
    sys.path.append(cfg_file[0])
    cfg_module = import_module(cfg_file[1].split('.')[0])

    return cfg_module  
    
#----------------------------------------------------------------------
def batch_run(cfg_module):
    """
    For batch run
    """
    cfg = load_config(cfg_module)
    cfg = check_config(cfg)
    run(cfg)    

if __name__ == '__main__':
    # Load parameters
    if len(sys.argv) < 2:
        cfg_module = input('Config module name? ')
    else:
        cfg_module = sys.argv[1]
    batch_run(cfg_module)