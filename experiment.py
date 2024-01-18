"""
Base code provided by
(C) Torsten Wüstenberg 2023
torsten.wuestenberg@psychologie.uni-heidelberg.de
Core Facility for Neuroscience of Self-Regulation (CNSR)
1st Version 0.9 2023-03-03
Final Version 1.0 2023-03-13

Coded by
Lukas Hejtmanek
institute of psychology, Czech Academy of Sciences
hejtmanek praha.psu.cas.cz

"""

# import neccessary python libraries
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
import random
import numpy as np
from datetime import datetime
import pandas as pd
import os
import sys
import time

from src.experiment import stimulus, presentRating
from src.calibrations import mouseCalibration, eyetrackerCalibration, calibrationOK
from src.connections import find_cpod, sendTriggerCPOD, sendTrigger
from src.utils import initScreen, getScreenSize
# =======================================================================
# initialize pygame and experimental window =============================

# read in stimulus list
SHOULD_TRIGGER = True
INTER_TRIAL = 500
RECALCULATE_INTER_TRIAL = True
COMPORT = 'COM8'

def load_stimuli(file_name):
    pth = file_name
    print(f'Loading settings from {pth}')
    out = pd.read_excel(pth)
    print(f'# trial stimuli: {len(out)}')
    return out

def get_time_since_start(start_time):
    diff = datetime.now() - start_time
    return diff.total_seconds()

# Loading stimuli
df_stimuli = load_stimuli('junior_test_settings.xlsx')

screenSize = getScreenSize()
screen = pygame.display.set_mode(screenSize, pygame.HIDDEN)
pygame.display.set_caption('')
pygame.display.update()
pygame.mixer.init()

start_time = datetime.now()
last_datetime = start_time
df_timings = pd.DataFrame(columns=['trial_start','sound_started','sound_duration',
                                   'sound_ended', 'real_sound_duration',
                                   'sound_duration_difference','real_trial_duration','trigger_started', 'trigger_ended',
                                   'trigger_com_started', 'trigger_com_ended', 'trigger_cpod_started', 'trigger_cpod_ended'])

def play_trial(iTrial, df_stimuli, should_trigger, com, cpod, recalculate_inter_trial = False):
    timings = dict()
    # This will change in case we need to repeat stimuli, now they just play once
    print(f'{iTrial} started')
    iStimulus = iTrial
    inter_trial = round(df_stimuli['inter_trial'][iStimulus])
    timings['trial_start'] = get_time_since_start(start_time)
    # say word and log onseg
    sound_path = os.path.join(os.getcwd(), 'stimuli', 'Lg_discrimination_stimuli', df_stimuli['file_name'][iStimulus])
    sound2play = pygame.mixer.Sound(sound_path)
    timings['sound_duration'] = sound2play.get_length()
    timings['sound_started'] = get_time_since_start(start_time)
    sound2play.play(loops = 0)
    waittime_ms = round(timings['sound_duration']*1000)
    if should_trigger:
        timings['trigger_started'] = get_time_since_start(start_time)
        timings['trigger_com_started'] = get_time_since_start(start_time)
        sendTrigger(5, com, 0.01)
        timings['trigger_com_ended'] = get_time_since_start(start_time)
        timings['trigger_cpod_started'] = get_time_since_start(start_time)
        #sendTriggerCPOD(cpod, 5, 0.01)
        timings['trigger_cpod_ended'] = get_time_since_start(start_time)
        timings['trigger_ended'] = get_time_since_start(start_time)
    if recalculate_inter_trial:
        ms_delay = round((timings['trigger_ended'] - timings['trigger_started'])*1000)
        pygame.time.delay(waittime_ms + inter_trial - ms_delay)
    else:
        pygame.time.delay(waittime_ms + inter_trial)
    
    sound2play.stop()
    timings['sound_ended'] = get_time_since_start(start_time)
    timings['real_sound_duration'] = timings['sound_ended'] - timings['sound_started']
    timings['sound_duration_difference'] = timings['real_sound_duration'] - timings['sound_duration']
    timings['real_trial_duration'] = timings['sound_ended'] - timings['trial_start']
    return timings

# Experimental loop -----------------------
for iTrial in range(0, df_stimuli.shape[0]):
#for iTrial in range(0, 4):
    timings = play_trial(iTrial, df_stimuli, SHOULD_TRIGGER, COMPORT, None, RECALCULATE_INTER_TRIAL)
    df_timings = df_timings.append(timings, ignore_index = True)

timestamp = start_time.strftime('%Y%m%d-%H%M%S')
df_timings.to_csv(f'logs/{timestamp}_timings.csv', index=False, header=True)
pygame.display.quit()
pygame.quit()

