"""
  Coded by
Lukas Hejtmanek
institute of psychology, Czech Academy of Sciences
hejtmanek@praha.psu.cas.cz
"""

# =======================================================================
# SETTINGS  NEED TO CHANGE FOR EACH PARTICIPANT
PARTICIPANT_ID = 0 # ID of the participant as a number
TRIGGERBOX_COM = 'COM3' # COM port of the trigger box, need to check it before the experiment 
# using the triggerBox software. It generally stays at the same port, but it can change

# =======================================================================
# DEFAULT SETTINGS - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING
# THESE SHOULD BE THE SAME THROUGHOUT THE ENTIRE EXPERIMENTAL RUN 
# changed only between different experiments or for testing purposes

DEBUG=False
EEG_TRIGGER = True # True if you want to send triggers to the EEG
fNIRS_TRIGGER = True # True if you want to send triggers to the fNIRS
RECALCULATE_INTER_TRIAL = True # True if you want to compensate for potential trigger delays caused by the serial communication


MAX_INTERTRIAL_INTERVAL = 15
MIN_INTERTRIAL_INTERVAL = 3
MAX_STIMULUS_ANSWER_INTERVAL = 0.5
MIN_STIMULUS_ANSWER_INTERVAL = 0.4

N_TRIALS = 140
RANDOM_SEED = 42 # DO NOT CHANGE THIS WHEN RUNNING THE EXPERIMENT
# =======================================================================

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
from datetime import datetime
import pandas as pd
import random
import os
import threading
import sys

from src.utils import getScreenSize
import src.core.experimental_flow as flow
import src.neuro3_syllables.experiment as experiment
import src.congruent_incongruent.generator as generator

## Setup Debugging
if DEBUG:
    EEG_TRIGGER=False
    fNIRS_TRIGGER=False
    if PARTICIPANT_ID > 0:
        PARTICIPANT_ID = 0
        print("WARNING: RUNNING IN DEBUG MODE")


if PARTICIPANT_ID == 0 and not DEBUG:
    print("ERROR: Participant ID was not set")
    sys.exit()

if EEG_TRIGGER:
    from src.connections import sendTrigger
    COMPORT = TRIGGERBOX_COM
else:
    COMPORT = None

if fNIRS_TRIGGER:
    from src.connections import sendTriggerCPOD, find_cpod
    CPOD = find_cpod()[1][0]
    if not CPOD:
        print("ERROR: No CPOD found and required for fNIRS triggering")
        sys.exit()


##  Preparation of the experiment
## open a window with pygame




intertrial_intervals = generator.generate_intertrial_intervals(N_TRIALS, MIN_INTERTRIAL_INTERVAL,
                                                              MAX_INTERTRIAL_INTERVAL, seed=RANDOM_SEED)

stimulus_answer_intervals = generator.generate_stimulus_answer_intervals(N_TRIALS, MIN_STIMULUS_ANSWER_INTERVAL,
                                                                         MAX_STIMULUS_ANSWER_INTERVAL, seed=RANDOM_SEED)

def path_to_stimulus(filename):
    return os.path.join(os.getcwd(), 'stimuli', 'congruent_incongruent', filename)


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
    trigger = int(df_trial['trigger'])
    
    print(f'{flow.get_time_since_start(start_time)}: Trial {iTrial}. {df_trial["block_type"]}. {df_trial["condition"]}. Stimulus {stim}. Trigger: {df_trial["trigger"]}')

    sound2play = pygame.mixer.Sound(sound_path)
    timings['sound_duration'] = sound2play.get_length()
    timings['sound_started'] = flow.get_time_since_start(start_time)
    sound2play.play(loops = 0)
    waittime_ms = round(timings['sound_duration']*1000)
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


def question_phase(iTrial, df_stimul):
    # using pygame pose a quesiton
    # wait for the answer
