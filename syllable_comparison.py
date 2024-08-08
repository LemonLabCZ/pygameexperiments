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
PARTICIPANT_ID = 14 # ID of the participant as a number
TRIGGERBOX_COM = 'COM3' # COM port of the trigger box, need to check it before the experiment 
# using the triggerBox software. It generally stays at the same port, but it can change
MOVIE_WINDOWS_NAME = 'Amalka.mp4 - Multimediální přehrávač VLC' # This is the name of the window


# =======================================================================
# DEFAULT SETTINGS - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING
# THESE SHOULD BE THE SAME THROUGHOUT THE ENTIRE EXPERIMENTAL RUN 
# changed only between different experiments or for testing purposes
# that the movie is played in. It can be found out by running the list_open_windows.py script in the root
MOVIE_REQUIRED = True # True if you want to play a movie during the experiment. Generally
EEG_TRIGGER = True # True if you want to send triggers to the EEG
fNIRS_TRIGGER = True # True if you want to send triggers to the fNIRS
RECALCULATE_INTER_TRIAL = True # True if you want to recalculate the intertrial time between each trial so 
# that the total time of trial sound duration and intertrial is the same for all trials
BLOCK_INTERTRIAL = (15000, 20000) # intertrial interval in miliseconds for the pause between blocks
INTERTRIAL_RANGE = [400, 600]
RANDOM_SEED = 111 # Seed for the intertrials
TRIGGER_DURATION = 0.1


# IMPORTS =======================================================================

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
from datetime import datetime
import pandas as pd
from src.syllable_comparison.settings_generation import generate_settings_filename
import os
import threading

from src.utils import getScreenSize
import src.core.experimental_flow as flow
import src.syllable_comparison.experiment as experiment


if MOVIE_REQUIRED:
    import src.core.video_control as VideoControl
import random

if EEG_TRIGGER:
    from src.connections import sendTrigger
    COMPORT = TRIGGERBOX_COM
else:
    COMPORT = None

    
if fNIRS_TRIGGER:
    from src.connections import sendTriggerCPOD, find_cpod
    CPOD = find_cpod()[1][0]

    
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


def play_trial(iTrial, df_stimuli, intertrials, should_trigger, com, recalculate_inter_trial = False):
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
    inter_trial = intertrials[iTrial]
    
    # This will change in case we need to repeat stimuli, now they just play once
    trial_info = df_stimuli.iloc[iTrial]
    timings['trial_start'] = flow.get_time_since_start(start_time)
    sound_path = path_to_stimulus(trial_info['stimulus'])
    print(f'Trial {iTrial}: Type: {trial_info["trial_type"]}, --- stimulus: {trial_info["stimulus_type"]}')
    sound2play = pygame.mixer.Sound(sound_path)
    timings['sound_duration'] = sound2play.get_length()
    timings['sound_started'] = flow.get_time_since_start(start_time)
    sound2play.play(loops = 0)
    #waittime_ms = round(timings['sound_duration']*1000)
    waittime_ms = round(timings['sound_duration']*1000)
    trigger = int(trial_info['trigger'])
    timings['trigger_started'] = flow.get_time_since_start(start_time)
    if should_trigger:       
        timings['trigger_com_started'] = flow.get_time_since_start(start_time)
        thread = threading.Thread(target=sendTrigger,args=(trigger, com, TRIGGER_DURATION))
        thread.start()
        timings['trigger_com_ended'] = flow.get_time_since_start(start_time)
    if fNIRS_TRIGGER:           
        timings['trigger_cpod_started'] = flow.get_time_since_start(start_time)
        # Sending CPOD trigger takes cca 20ms, execute in a separate thread
        thread = threading.Thread(target=sendTriggerCPOD,args=(CPOD, trigger, TRIGGER_DURATION*1000))
        thread.start()
        timings['trigger_cpod_ended'] = flow.get_time_since_start(start_time)        
    timings['trigger_ended'] = flow.get_time_since_start(start_time)

    # Substracts the extra duration of the trigger from the intertrial time (generally 17 ms for the trigger box)
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

# Loading settings =======================================================
stimuli_filename = generate_settings_filename(PARTICIPANT_ID)
df_stimuli = load_stimuli(stimuli_filename)

# get number of unique values in the set columna nd the block column
n_trials = len(df_stimuli['block_number'])
n_set = len(df_stimuli['set_number'].unique())
n_block = len(df_stimuli['block_number'].unique())
n_blocks = n_set * n_block

## Setting initial parameters ========================================
start_time = datetime.now()
last_datetime = start_time

block_intertrials = experiment.generate_block_intertrials(PARTICIPANT_ID, BLOCK_INTERTRIAL, n_blocks)

# Randomizes intertrial times or keeps it at a fixed value if the length is one
if len(INTERTRIAL_RANGE) == 1:
    intertrials = [INTERTRIAL_RANGE[0]] * n_trials
if len(INTERTRIAL_RANGE) == 2:
    intertrials = random.choices(range(INTERTRIAL_RANGE[0], INTERTRIAL_RANGE[1]), k=n_trials)

df_timings = flow.prepare_log_table(add_fNIRS=fNIRS_TRIGGER)
timestamp = start_time.strftime('%Y%m%d-%H%M%S')

# Experimental loop -----------------------
log_location = os.path.join(os.getcwd(), 'logs', 'syllable_comparison')
os.makedirs(log_location, exist_ok=True)
log_filename = os.path.join(log_location, f'{PARTICIPANT_ID}_{timestamp}_timings.csv')

# initialize pygame and experimental window =============================
screenSize = getScreenSize()
screen = pygame.display.set_mode(screenSize, pygame.HIDDEN)
pygame.display.set_caption('')
pygame.display.update()
pygame.mixer.init()

# Video Control =======================================================
if MOVIE_REQUIRED:
    VideoControl.start_playing_video(MOVIE_WINDOWS_NAME)

# Main loop =======================================================
try:
    last_block = 1 # used to check if the block has changed to initiate the pause between blocks
    for iTrial in range(0, df_stimuli.shape[0]):
        trial_set = df_stimuli['set_number'][iTrial]
        this_block = df_stimuli['block_number'][iTrial]
        block_order = (trial_set - 1) * 4 + this_block
        if(last_block != this_block):
            block_intertrial = int(block_intertrials[block_order - 1])
            print(f'Pause between blocks started for {block_intertrial/1000}s')
            pygame.time.delay(block_intertrial)
            print(f'Pause ended')
            df_timings.to_csv(log_filename, index=False, header=True, mode="w")
        timings = play_trial(iTrial, df_stimuli, intertrials, EEG_TRIGGER, COMPORT, RECALCULATE_INTER_TRIAL)
        df_timings = df_timings._append(timings, ignore_index = True)
        last_block = this_block
finally:
    df_timings.to_csv(log_filename, index=False, header=True, mode="w")

pygame.display.quit()
pygame.quit()