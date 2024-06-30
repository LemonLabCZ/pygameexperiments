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

# =======================================================================
# SETTINGS  NEED TO CHANGE FOR EACH PARTICIPANT
PARTICIPANT_ID = 1 # ID of the participant as a number
TRIGGERBOX_COM = 'COM4' # COM port of the trigger box, need to check it before the experiment 
# using the triggerBox software. It generally stays at the same port, but it can change

# =======================================================================
# DEFAULT SETTINGS - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING
# THESE SHOULD BE THE SAME THROUGHOUT THE ENTIRE EXPERIMENTAL RUN 
# changed only between different experiments or for testing purposes
SHOULD_TRIGGER = False # True if you want to send triggers to the EEG
RECALCULATE_INTER_TRIAL = True # True if you want to recalculate the intertrial time between each trial so 
# that the total time of trial sound duration and intertrial is the same for all trials
BLOCK_INTERTRIAL = (15000, 200000) # intertrial interval in miliseconds for the pause between blocks
INTERTRIAL_RANGE = (700) # If touple(2) then randomizes between the two values. If a single value, then keeps it at that value
RANDOM_SEED = 111 # Seed for the intertrials
TRIGGER_DURATION = 0.1
fNIRS_IMPLEMENTED = False # True if you want to send triggers to the fNIRS
# IMPORTS =======================================================================

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
from datetime import datetime
import pandas as pd
from src.syllable_comparison.settings_generation import generate_settings_filename
import os

from src.utils import getScreenSize
import src.core.experimental_flow as flow
import src.syllable_comparison.experiment as experiment

if SHOULD_TRIGGER:
    from src.connections import sendTrigger
    COMPORT = TRIGGERBOX_COM
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

def path_to_stimulus(filename):
    return os.path.join(os.getcwd(), 'stimuli', 'syllable_comparison', filename)

# Loading settings =======================================================
stimuli_filename = generate_settings_filename(PARTICIPANT_ID)
df_stimuli = load_stimuli(stimuli_filename)

# get number of unique values in the set columna nd the block column
n_trials = len(df_stimuli['block_number'])
n_set = len(df_stimuli['set_number'].unique())
n_block = len(df_stimuli['block_number'].unique())
n_blocks = n_set * n_block

block_intertrials = experiment.generate_block_intertrials(PARTICIPANT_ID, BLOCK_INTERTRIAL, n_blocks)
intertrials = experiment.generate_intertrials(PARTICIPANT_ID, INTERTRIAL_RANGE, n_trials)

# initialize pygame and experimental window =============================
screenSize = getScreenSize()
screen = pygame.display.set_mode(screenSize, pygame.HIDDEN)
pygame.display.set_caption('')
pygame.display.update()
pygame.mixer.init()

# Experiment flow =======================================================
start_time = datetime.now()
last_datetime = start_time

df_timings = flow.prepare_log_table(add_fNIRS=fNIRS_IMPLEMENTED)

def play_trial(iTrial, df_stimuli, should_trigger, com, recalculate_inter_trial = False):
    """_summary_
    Args:
        iTrial (int): Trial index, starting from 0
        df_stimuli (pd.DataFrame): Dataframe with all the stimui
        should_trigger (bool): If the triggers should be sent
        com (string): COM port of the trigger box
        recalculate_inter_trial (bool, optional): The trigger box generally adds 17 ms to the trigger 
        duration. If this is set to true, the intertrial time will be recalculated to match the 
        total time of the trial and the intertrial time. Defaults to False.

    Returns:
        list: returns list with timings of the trial
    """
    timings = dict()
    # This will change in case we need to repeat stimuli, now they just play once
    print(f'{iTrial} started')
    iStimulus = iTrial
    inter_trial = intertrials[iTrial]
    timings['trial_start'] = flow.get_time_since_start(start_time)
    sound_path = path_to_stimulus(df_stimuli['stimulus'][iStimulus])
    sound2play = pygame.mixer.Sound(sound_path)
    timings['sound_duration'] = sound2play.get_length()
    timings['sound_started'] = flow.get_time_since_start(start_time)
    sound2play.play(loops = 0)
    waittime_ms = round(timings['sound_duration']*1000)
    if should_trigger:
        timings['trigger_started'] = flow.flow.get_time_since_start(start_time)
        timings['trigger_com_started'] = flow.get_time_since_start(start_time)
        sendTrigger(5, com, TRIGGER_DURATION)
        timings['trigger_com_ended'] = flow.get_time_since_start(start_time)
        if fNIRS_IMPLEMENTED:
            timings['trigger_cpod_started'] = flow.get_time_since_start(start_time)
            # THE CPOD TRIGGER IS FROM fNIRS CPOD box, not implemented in this experiment
            # sendTriggerCPOD(cpod, 5, 0.01)
            timings['trigger_cpod_ended'] = flow.get_time_since_start(start_time)
        timings['trigger_ended'] = flow.get_time_since_start(start_time)
    else:
        timings['trigger_started'] = flow.get_time_since_start(start_time)
        timings['trigger_ended'] = timings['trigger_started']
    # Substracts the extraduration of the trigger from the intertrial time (generally 17 ms for the trigger box)
    if recalculate_inter_trial:
        ms_trigger_delay = round((timings['trigger_ended'] - timings['trigger_started'])*1000)
        pygame.time.delay(waittime_ms + inter_trial - ms_trigger_delay)
    else:
        pygame.time.delay(waittime_ms + inter_trial)
    
    sound2play.stop()
    timings['sound_ended'] = flow.get_time_since_start(start_time)
    timings['real_sound_duration'] = timings['sound_ended'] - timings['sound_started']
    timings['sound_duration_difference'] = timings['real_sound_duration'] - timings['sound_duration']
    timings['real_trial_duration'] = timings['sound_ended'] - timings['trial_start']
    return timings

# Experimental loop -----------------------
timestamp = start_time.strftime('%Y%m%d-%H%M%S')
log_location = os.path.join(os.getcwd(), 'logs', 'syllable_comparison')
os.makedirs(log_location, exist_ok=True)
log_filename = os.path.join(log_location, f'{PARTICIPANT_ID}_{timestamp}_timings.csv')

last_block = 0
for iTrial in range(0, df_stimuli.shape[0]):
    trial_set = df_stimuli['set_number'][iTrial]
    timings = play_trial(iTrial, df_stimuli, SHOULD_TRIGGER, COMPORT, RECALCULATE_INTER_TRIAL)
    df_timings = df_timings._append(timings, ignore_index = True)
    if(last_block != last_block):
        # pause between sets
        print(f'Pause between sets started')
        pygame.time.delay(block_intertrials[trial_set])
        print(f'Pause between sets ended')
    df_timings.to_csv(log_filename, index=False, header=True, mode="w")
    last_set = trial_set

df_timings.to_csv(log_filename, index=False, header=True, mode="w")

pygame.display.quit()
pygame.quit()