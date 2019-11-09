#!/usr/bin/env python3
#coding:utf-8
"""
  Author:  Arnaud Desvachez --<arnaud.desvachez@gmail.com>
  Purpose: Online protocol for deep meditation state neurofeedback.
  Created: 14.10.2019
"""

import mne
import os
import sys
import time
import numpy as np
import multiprocessing as mp

from importlib import import_module
from scipy.signal import argrelextrema, detrend

import matplotlib.pyplot as plt

import neurodecode.utils.pycnbi_utils as pu

from neurodecode import logger
from neurodecode.utils import q_common as qc
from neurodecode.gui.streams import redirect_stdout_to_queue
from neurodecode.stream_receiver.stream_receiver import StreamReceiver

os.environ['OMP_NUM_THREADS'] = '1' # actually improves performance for multitaper
mne.set_log_level('ERROR')          # DEBUG, INFO, WARNING, ERROR, or CRITICAL


#----------------------------------------------------------------------
def check_config(cfg):
    """
    Ensure that the config file contains the parameters
    """
    critical_vars = {
        'COMMON': ['DATA_PATH']
        }

    optional_vars = {
        'AMP_NAME':None,
        'AMP_SERIAL':None,
        'GLOBAL_TIME': 1.0 * 60,
        'NJOBS': 1,
    }

    for key in critical_vars['COMMON']:
        if not hasattr(cfg, key):
            logger.error('%s is a required parameter' % key)
            raise RuntimeError

    for key in optional_vars:
        if not hasattr(cfg, key):
            setattr(cfg, key, optional_vars[key])
            logger.warning('Setting undefined parameter %s=%s' % (key, getattr(cfg, key)))


#----------------------------------------------------------------------
def find_lsl_stream(cfg, state):
    """
    Find the amplifier name and its serial number to connect to

    cfg = config file
    state = GUI sharing variable
    """
    if cfg.AMP_NAME is None and cfg.AMP_SERIAL is None:
        amp_name, amp_serial = pu.search_lsl(state, ignore_markers=True)
    else:
        amp_name = cfg.AMP_NAME
        amp_serial = cfg.AMP_SERIAL

    return amp_name, amp_serial

#----------------------------------------------------------------------
def connect_lsl_stream(cfg, amp_name, amp_serial):
    """
    Connect to the lsl stream corresponding to the provided amplifier
    name and serial number

    cfg = config file
    amp_name =  amplifier's name to connect to
    amp_serial = amplifier's serial number
    """
    sr = StreamReceiver(window_size=cfg.WINDOWSIZE, buffer_size=cfg.STREAMBUFFER, amp_serial=amp_serial, eeg_only=False, amp_name=amp_name)

    return sr

#----------------------------------------------------------------------
def run(cfg, state=mp.Value('i', 1), queue=None):
    """
    Online protocol for Alpha/Theta neurofeedback.
    """
    redirect_stdout_to_queue(logger, queue, 'INFO')

    # Wait the recording to start (GUI)
    while state.value == 2: # 0: stop, 1:start, 2:wait
        pass

    # Protocol runs if state equals to 1
    if not state.value:
        sys.exit(-1)

#----------------------------------------------------------------------

def print_perc(percent):
    white = (255, 255, 255)
    # create a font object.
    # 1st parameter is the font file
    # which is present in pygame.
    # 2nd parameter is size of the font
    font = pygame.font.Font('freesansbold.ttf', 22)

    # create a text suface object,
    # on which text is drawn on it.
    text = font.render(str(percent/10) + '%', True,white)

    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()

    # set the center of the rectangular object.
    textRect.center = (w // 4, h // 4)

    screen.blit(text,textRect)

    #----------------------------------------------------------------------
    # LSL stream connection
    #----------------------------------------------------------------------
    # chooose amp
    amp_name, amp_serial = find_lsl_stream(cfg, state)

    # Connect to lsl stream
    sr = connect_lsl_stream(cfg, amp_name, amp_serial)

    # Get sampling rate
    sfreq = sr.get_sample_rate()

    # Get trigger channel
    trg_ch = sr.get_trigger_channel()


    #----------------------------------------------------------------------
    # Main
    #----------------------------------------------------------------------
    global_timer = qc.Timer(autoreset=False)
    internal_timer = qc.Timer(autoreset=True)

    while state.value == 1 and global_timer.sec() < cfg.GLOBAL_TIME:

        #----------------------------------------------------------------------
        # Data acquisition
        #----------------------------------------------------------------------
        sr.acquire()
        raw, tslist = sr.get_window()       # [samples x channels]
        raw = raw.T                         # [channels x samples]

        # Check if proper real-time acquisition
        tsnew = np.where(np.array(tslist) > last_ts)[0]
        if len(tsnew) == 0:
            logger.warning('There seems to be delay in receiving data.')
            time.sleep(1)
            continue

        #----------------------------------------------------------------------
        # Data processing
        #----------------------------------------------------------------------

        # Compute the GFP
        gfp = np.abs(detrend(np.mean(raw, 0)))    # [1 x samples]

        # Find GFP's peak
        gfp_peaks = argrelextrema(gfp, np.greater, order=15)     # Order needs to be optimized

        # Assign dominant microstate
        count = 0

        #  Missing first and last microstate --> TO change

        for p in range(1, len(gfp_peaks[0])-1):
            correletion = np.array()

            for i in range(len(micro_template)):
                correletion.append(np.corrcoef(raw[:, p], micro_template[i]))

            if np.argmax(correletion) == cfg.MICRO2REGULATE:
                start = gfp_peaks[0][p - 1] + (gfp_peaks[0][p] - gfp_peaks[0][p-1]) / 2
                end = gfp_peaks[0][p] + (gfp_peaks[0][p+1] - gfp_peaks[0][p]) / 2
                count = count + len(range(start, end))

        # Percentage of the microstate of interest
        percent = count / raw.shape[1] * 100

        # Feedback
        

        pygame.init()

        pygame.display.set_caption('EEG microstate')

        background = pygame.image.load('stars2.png')

        background_size = background.get_size()
        background_rect = background.get_rect()
        screen = pygame.display.set_mode(background_size)
        w,h = background_size



        x = 0
        y = 0

        x1 = 0
        y1 = -h

        ship = pygame.image.load("space.png")
        shiprect = ship.get_rect()
        shiprect.center = (w//2,h//2)
        running = True
        i = 0



        # set the pygame window name
        pygame.display.set_caption('EEG microstate')




        screen.blit(background,background_rect)


        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        y1 += percent
        y += percent
        screen.blit(background,(x,y))
        screen.blit(background,(x1,y1))
        if y > h:
            y = -h
        if y1 > h:
            y1 = -h



        screen.blit(ship,shiprect)
        print_perc(percent)
        pygame.display.flip()
        pygame.display.update()


# ----------------------------------------------------------------------
def load_config(cfg_file):
    """
    Dynamic loading of a config file.
    Format the lib to fit the previous developed neurodecode code if subject specific file (not for the templates).
    cfg_file: tuple containing the path and the config file name.
    """
    cfg_file = os.path.split(cfg_file)
    sys.path.append(cfg_file[0])
    cfg_module = import_module(cfg_file[1].split('.')[0])

    return cfg_module

#----------------------------------------------------------------------
def batch_run(cfg_module):
    """
    For batch script
    """
    cfg = load_config(cfg_module)
    check_config(cfg)
    run(cfg)

#----------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        cfg_module = input('Config module name? ')
    else:
        cfg_module = sys.argv[1]
    batch_run(cfg_module)
