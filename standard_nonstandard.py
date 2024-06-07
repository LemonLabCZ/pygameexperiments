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
hejtmanek@praha.psu.cas.cz
"""

# import neccessary python libraries
# =======================================================================
# SETTINGS  NEED TO CHANGE FOR EACH PARTICIPANT
# read in stimulus list
PARTICIPANT_ID = 1 # ID of the participant as a number

# =======================================================================
# DEFAULT SETTINGS - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING
# THESE SHOULD BE THE SAME THROUGHOUT THE ENTIRE EXPERIMENTAL RUN 
# changed only between different experiments or for testing purposes
SHOULD_TRIGGER = False # True if you want to send triggers to the EEG
RECALCULATE_INTER_TRIAL = True # True if you want to recalculate the intertrial time between each trial so 
# that the total time of trial sound duration and intertrial is the same for all trials
BLOCK_INTERTRIAL = (14, 20) # Intertrial interval in seconds for the pause between blocks
RANDOM_SEED = 111 # Seed for the intertrials
# IMPORTS =======================================================================

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
from datetime import datetime
import pandas as pd
import random
import os

from src.experiment import stimulus, presentRating
from src.calibrations import mouseCalibration, eyetrackerCalibration, calibrationOK
from src.utils import initScreen, getScreenSize

if SHOULD_TRIGGER:
    from src.connections import find_cpod, sendTriggerCPOD, sendTrigger
    COMPORT = 'COM8'
else:
    COMPORT = None
## =======================================================================
# FUNCTIONS

def load_stimuli(file_name):
    pth = file_name
    print(f'Loading settings from {pth}')
    out = pd.read_csv(pth)
    print(f'# trial stimuli: {len(out)}')
    return out

def get_time_since_start(start_time):
    diff = datetime.now() - start_time
    return diff.total_seconds()

def path_to_stimulus(filename):
    return os.path.join(os.getcwd(), 'stimuli', 'standard_nonstandard', filename)

# Loading settings =======================================================

stimuli_filename = os.path.join(os.getcwd(), 'settings', 'standard_nonstandard',
                                f'settings{PARTICIPANT_ID}.csv')
df_stimuli = load_stimuli(stimuli_filename)
# get number of unique values in the set columna nd the block column
n_set = len(df_stimuli['set_number'].unique())
n_block = len(df_stimuli['block_number'].unique())
n_blocks = n_set * n_block

random.seed(RANDOM_SEED) # We want all 
block_intertrials = random.choices(range(BLOCK_INTERTRIAL[0], BLOCK_INTERTRIAL[1]), k=n_blocks)

# initialize pygame and experimental window =============================
screenSize = getScreenSize()
screen = pygame.display.set_mode(screenSize, pygame.HIDDEN)
pygame.display.set_caption('')
pygame.display.update()
pygame.mixer.init()

# Experiment flow =======================================================
start_time = datetime.now()
last_datetime = start_time
df_timings = pd.DataFrame(columns=['trial_start','sound_started','sound_duration', 'sound_ended', 'real_sound_duration',
                                   'sound_duration_difference','real_trial_duration','trigger_started', 'trigger_ended',
                                   'trigger_com_started', 'trigger_com_ended', 'trigger_cpod_started', 'trigger_cpod_ended'])

def play_trial(iTrial, df_stimuli, should_trigger, com, recalculate_inter_trial = False):
    """_summary_
    Args:
        iTrial (_type_): _description_
        df_stimuli (_type_): _description_
        should_trigger (_type_): _description_
        com (_type_): _description_
        cpod (_type_): _description_
        recalculate_inter_trial (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    timings = dict()
    # This will change in case we need to repeat stimuli, now they just play once
    print(f'{iTrial} started')
    iStimulus = iTrial
    # TODO - add the intertrial time to the timings
    inter_trial = 1100
    timings['trial_start'] = get_time_since_start(start_time)
    # say word and log onseg
    sound_path = path_to_stimulus(df_stimuli['stimulus'][iStimulus])
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
    else:
        timings['trigger_started'] = get_time_since_start(start_time)
        timings['trigger_ended'] = timings['trigger_started']
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
timestamp = start_time.strftime('%Y%m%d-%H%M%S')

for iTrial in range(0, df_stimuli.shape[0]):
    timings = play_trial(iTrial, df_stimuli, SHOULD_TRIGGER, COMPORT, RECALCULATE_INTER_TRIAL)
    df_timings = df_timings._append(timings, ignore_index = True)

df_timings.to_csv(f'logs/standard_nonstandard/{PARTICIPANT_ID}_{timestamp}_timings.csv', 
                  index=False, header=True, )
pygame.display.quit()
pygame.quit()