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
MOVIE_WINDOWS_NAME = 'Krtek.mp4 - Multimediální přehrávač VLC' # This is the name of the window


# =======================================================================
# DEFAULT SETTINGS - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING
# THESE SHOULD BE THE SAME THROUGHOUT THE ENTIRE EXPERIMENTAL RUN 
# changed only between different experiments or for testing purposes
SHOULD_TRIGGER = False # True if you want to send triggers to the EEG
RECALCULATE_INTER_TRIAL = True # True if you want to compensate for potential trigger delays caused by the serial communication
BLOCK_INTERTRIAL = (15000, 20000) # intertrial interval in milliseconds for the pause between blocks
INTERTRIAL_RANGE = [900, 1100] # If list(2) then randomizes between the two values. If a single value, then keeps it at that value
RANDOM_SEED = 111 # Seed for the intertrials
TRIGGER_DURATION = 0.1
fNIRS_IMPLEMENTED = False # True if you want to send triggers to the fNIRS
MOVIE_REQUIRED = False # True if you want to play a movie during the experiment. Generally
# set to false during debugging

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
import src.core.experimental_flow as flow

if SHOULD_TRIGGER:
    from src.connections import sendTrigger
    COMPORT = TRIGGERBOX_COM
else:
    COMPORT = None


if MOVIE_REQUIRED:
    from src.core.video_control import VideoControl
## =======================================================================
# FUNCTIONS
def load_stimuli(file_name):
    pth = file_name
    print(f'Loading settings from {pth}')
    out = pd.read_csv(pth)
    print(f'# trial stimuli: {len(out)}')
    return out


def path_to_stimulus(filename):
    return os.path.join(os.getcwd(), 'stimuli', 'standard_nonstandard', filename)


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
    timings['trial_start'] = flow.get_time_since_start(start_time)
    
    df_trial = df_stimuli.iloc[iTrial]
    stim = df_trial['stimulus']
    sound_path = path_to_stimulus(stim)
    
    print(f'{flow.get_time_since_start(start_time)}: Trial {iTrial}. {df_trial["block_type"]}. {df_trial["condition"]}. Stimulus {stim}')

    sound2play = pygame.mixer.Sound(sound_path)
    timings['sound_duration'] = sound2play.get_length()
    timings['sound_started'] = flow.get_time_since_start(start_time)
    sound2play.play(loops = 0)
    waittime_ms = round(timings['sound_duration']*1000)
    if should_trigger:
        timings['trigger_started'] = flow.get_time_since_start(start_time)
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

# Loading settings =======================================================
stimuli_filename = os.path.join(os.getcwd(), 'settings', 'standard_nonstandard',
                                f'settings{PARTICIPANT_ID}.csv')
df_stimuli = load_stimuli(stimuli_filename)

# get number of unique values in the set columna nd the block column
n_trials = len(df_stimuli['block_number'])
n_set = len(df_stimuli['set_number'].unique())
n_block = len(df_stimuli['block_number'].unique())
n_blocks = n_set * n_block

random.seed(RANDOM_SEED) # We want all participants to have the same intertrials
block_intertrials = random.choices(range(BLOCK_INTERTRIAL[0], BLOCK_INTERTRIAL[1]), k=n_blocks)

# Randomizes intertrial times or keeps it at a fixed value if the length is one
if len(INTERTRIAL_RANGE) == 1:
    intertrials = [INTERTRIAL_RANGE[0]] * n_trials
if len(INTERTRIAL_RANGE) == 2:
    intertrials = random.choices(range(INTERTRIAL_RANGE[0], INTERTRIAL_RANGE[1]), k=n_trials)

# initialize pygame and experimental window =============================
screenSize = getScreenSize()
screen = pygame.display.set_mode(screenSize, pygame.HIDDEN)
pygame.display.set_caption('')
pygame.display.update()
pygame.mixer.init()

# Video Control =======================================================
if MOVIE_REQUIRED:
    VideoControl.start_playing_video(MOVIE_WINDOWS_NAME)

# Experiment flow =======================================================
start_time = datetime.now()
last_datetime = start_time

# Experimental loop -----------------------
timestamp = start_time.strftime('%Y%m%d-%H%M%S')
df_timings = flow.prepare_log_table(add_fNIRS=fNIRS_IMPLEMENTED)

last_setblock = df_stimuli['set_number'][0]+df_stimuli['block_number'][0]
current_block = 0
for iTrial in range(0, df_stimuli.shape[0]):
    setblock = df_stimuli['set_number'][iTrial]+df_stimuli['block_number'][iTrial]
    if(last_setblock != setblock):
        print(f'Pause between blocks started for {block_intertrials[current_block]/1000} seconds')
        pygame.time.delay(block_intertrials[current_block])
        print(f'Pause between blocks ended')
        current_block += 1
        df_timings.to_csv(f'logs/standard_nonstandard/{PARTICIPANT_ID}_{timestamp}_timings.csv', 
                  index=False, header=True, mode='w')
    timings = play_trial(iTrial, df_stimuli, intertrials, SHOULD_TRIGGER, COMPORT, RECALCULATE_INTER_TRIAL)
    df_timings = df_timings._append(timings, ignore_index = True)
    last_setblock = setblock

df_timings.to_csv(f'logs/standard_nonstandard/{PARTICIPANT_ID}_{timestamp}_timings.csv', 
                  index=False, header=True, mode='w')
pygame.display.quit()
pygame.quit()
