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

DEBUG=True
EEG_TRIGGER = True # True if you want to send triggers to the EEG
fNIRS_TRIGGER = True # True if you want to send triggers to the fNIRS
TRIGGER_DURATION = 0.1 # Duration of the trigger in seconds
PAUSE_TRIAL = 3 # Trial number when the pause happens
PAUSE_DURATION = 10 # Duration of the pause in seconds
PAUSE_MOVIE = "stimuli/congruent_incongruent/DONKS_experiment-small.mp4" # Path to the movie for the pause
DEBUG_MESSAGES = False # True if you want to see debug messages

MAX_STIMULUS_ANSWER_INTERVAL = 0.5
MIN_STIMULUS_ANSWER_INTERVAL = 0.4

N_TRIALS = 140
RANDOM_SEED = 42 # DO NOT CHANGE THIS WHEN RUNNING THE EXPERIMENT

# SETUP DO NOT TOUCH BELOW THIS POINT :) 
# ====================================================

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pygame
from pygame.locals import *
import pandas as pd
import os
import threading
import sys
from datetime import datetime

import src.core.experimental_flow as flow
import src.congruent_incongruent.experiment as experiment
import src.congruent_incongruent.generator as generator

## Setup Debugging
if DEBUG:
    EEG_TRIGGER=False
    DEBUG_MESSAGES=True
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

def play_trial(stimulus, question_type, answer_type, inter_trial,
               should_trigger, com, question_trigger, answer_triggers, 
               answer_trigger_delay):
    """ Main building block of the experiment
    Args:
        answer_triggers (list): List of 3 triggers for the answer
        answer_trigger_delay (list): List of 2 delays for the answer triggers. First trigger happens immediately
            the second and the third after given time

    Returns:
        list: returns list with timings of the trial
    """
    timings = dict()
    timings['trial_start'] = flow.get_time_since_start(start_time)
    
    question_sound = experiment.path_to_stimulus('q', stimulus, question_type)
    answer_sound = experiment.path_to_stimulus('a', stimulus, answer_type)

    # STIMULUS question phase ------------
    question_timings, sound = play_stimulus(question_sound)
    timings['question_duration'] = question_timings['sound_duration']
    timings['question_started'] = question_timings['sound_started']
    timings['question_trigger'] = -999
    #if should_trigger:
        # send_trigger(com, question_trigger, TRIGGER_DURATION)
    timings['question_cpod_trigger'] = -999
    # if fNIRS_TRIGGER:           
    #    send_cpod_trigger(CPOD, question_trigger, TRIGGER_DURATION)
    pygame.time.delay(round((timings['question_duration'] + inter_trial)*1000))
    sound.stop()
    timings['question_ended'] = flow.get_time_since_start(start_time)

    ## STIMULUS ANSWER PHASE --------------------
    answer_timings, sound = play_stimulus(answer_sound)
    timings['answer_duration'] = answer_timings['sound_duration']
    timings['answer_started'] = answer_timings['sound_started']
    timings['answer_ended'] = flow.get_time_since_start(start_time)
    
    timings['answer_trigger'] = flow.get_time_since_start(start_time)
    timings['answer_trigger_2'] = timings['answer_trigger'] + answer_trigger_delay[0]
    timings['answer_trigger_3'] = timings['answer_trigger'] + answer_trigger_delay[1]
    if should_trigger:
        send_trigger(com, answer_triggers[0], TRIGGER_DURATION)
        send_trigger(com, answer_triggers[1], TRIGGER_DURATION, delay=answer_trigger_delay[0])
        send_trigger(com, answer_triggers[2], TRIGGER_DURATION, delay=answer_trigger_delay[1])
    timings['answer_cpod_trigger'] = flow.get_time_since_start(start_time)
    if fNIRS_TRIGGER:
        send_cpod_trigger(CPOD, answer_triggers[0], TRIGGER_DURATION)
    pygame.time.delay(round(answer_timings['sound_duration']*1000))
    sound.stop()
    
    return timings


def play_stimulus(stimulus):
    timings = dict()
    sound2play = pygame.mixer.Sound(stimulus)
    timings['sound_started'] = flow.get_time_since_start(start_time)
    timings['sound_duration'] = sound2play.get_length()
    sound2play.play(loops = 0)
    return timings, sound2play


def send_trigger(com, trigger, duration, delay):
    """ Send a trigger to the EEG device via the COM port.

    Args:
        com (str): The COM port to send the trigger to.
        trigger (int): The trigger value to send.
        duration (float): The duration of the trigger in seconds.
    """
    if com is None:
        raise ValueError("COM port is not specified")
    if (DEBUG_MESSAGES):
        print(f"Sending EEG trigger {trigger} to {com}")
    thread = threading.Thread(target=sendTrigger, args=(trigger, com, duration, 0.2, delay))
    thread.start()


def send_cpod_trigger(cpod, trigger, duration):
    if cpod is None:
        raise ValueError("CPOD is not specified")
    if (DEBUG_MESSAGES):
        print(f"Sending fnirs trigger {trigger} to {cpod}")
    thread = threading.Thread(target=sendTriggerCPOD,args=(cpod, trigger, duration))
    thread.start()


# Experiment flow =======================================================
start_time = datetime.now()
last_datetime = start_time
aftertrials = generator.generate_aftertrial_intervals_torsten(seed=RANDOM_SEED)
intertrials = generator.generate_intertrial_intervals(N_TRIALS, MIN_STIMULUS_ANSWER_INTERVAL,
                                                      MAX_STIMULUS_ANSWER_INTERVAL, seed=RANDOM_SEED)
try:
    df_stimuli = generator.generate_stimulus_answer_pairs(seed=PARTICIPANT_ID)
except Exception as e:
    print(f"Error generating stimulus answer pairs. Choose a different Participant ID: {e}")
    sys.exit()

question_trials = generator.generate_question_trials(seed=PARTICIPANT_ID)
questions = generator.generate_potential_questions(seed=PARTICIPANT_ID)
df_triggers = pd.read_csv('src/congruent_incongruent/congruent-incongruent-triggers.csv')

iQuestionTrial = 0
log_timestamp = start_time.strftime("%Y%m%d-%H%M%S")
# generate the folder if it does not exist
if not os.path.exists(os.path.join(os.getcwd(), 'logs', 'congruent_incongruent')):
    os.makedirs(os.path.join(os.getcwd(), 'logs', 'congruent_incongruent'))

log_filename = os.path.join(os.getcwd(), 'logs', 'congruent_incongruent',
                        f'{PARTICIPANT_ID}_{log_timestamp}_behavior.csv')
settings_filename = os.path.join(os.getcwd(), 'logs', 'congruent_incongruent',
                        f'{PARTICIPANT_ID}_{log_timestamp}_settings.csv')
questions_log_filename = os.path.join(os.getcwd(), 'logs', 'congruent_incongruent',  
                        f'{PARTICIPANT_ID}_{log_timestamp}_questions.csv')
df_stimuli.to_csv(settings_filename, index=False, header=True, mode='w')

# Experimental loop -----------------------=========================
screen = experiment.initialize_pygame()

try:
    df_timings = experiment.prepare_trial_log(add_fNIRS=fNIRS_TRIGGER) #$ FIX THIS
    df_questions = experiment.prepare_question_log()
    df_timings.to_csv(log_filename, index=False, header=True, mode='w')
    for iTrial in range(0, df_stimuli.shape[0]):

        # REGULAR TRIAL =============================================
        # returns number, and then initial/final for question and answer
        stimulus, stimulus_question, stimulus_answer = df_stimuli.loc[iTrial, ['stimulus', 'question', 'answer']]
        condition = df_stimuli.loc[iTrial, 'condition']
        # recode condition to 1, 2, 3, 4 (initial-initial, initial-final, final-initial, final-final)
        condition_trigger = {'initial-initial': 10, 'initial-final': 20, 
             'final-final': 30, 'final-initial': 40}.get(condition, 9)
        answer_triggers = [condition_trigger, condition_trigger+1, condition_trigger+2]
        
        # in triggers, find row where stimulus is stimulus, and answer type is in triggers type column
        df_triggers_row = df_triggers.loc[(df_triggers['stimulus'] == stimulus) &
                                          (df_triggers['type'] == stimulus_answer)]
        if (df_triggers_row.shape[0] == 0):
            ValueError(f"Error: No triggers found for stimulus {stimulus} and answer type {stimulus_answer}")
        trigger2_delay, trigger3_delay = (df_triggers_row.iloc[0]['trigger1'], 
                                            df_triggers_row.iloc[0]['trigger2'])
        print(f'Trial {iTrial}: {flow.get_time_since_start(start_time)} stimulus {stimulus}, {stimulus_question}-{stimulus_answer}')
        experiment.show_fixation_cross(screen)
        timings = play_trial(stimulus, stimulus_question, stimulus_answer, 
                             intertrials[iTrial], EEG_TRIGGER, COMPORT, 1, answer_triggers, [trigger2_delay, trigger3_delay])
        df_timings = df_timings._append(timings, ignore_index = True)
        print(f'After trial pause for {aftertrials[iTrial]} seconds')

        # BEHAVIORAL QUESTION ========================================
        if iTrial in question_trials:
            question_time_start = flow.get_time_since_start(start_time)
            question = questions[iQuestionTrial]
            iQuestionTrial += 1
            print(f'Question {iTrial}: {flow.get_time_since_start(start_time)}, question {question}')
            answer = experiment.question_phase(screen, question)
            df_questions = df_questions._append({'question': question, 'answer': answer, 
                                    'time_start': question_time_start,
                                    'time_answered': flow.get_time_since_start(start_time), 
                                    'trial': iTrial}, ignore_index = True)
            df_questions.to_csv(questions_log_filename, index=False, header=True, mode='w')
            df_timings.to_csv(log_filename, index=False, header=True, mode='w')
            experiment.show_fixation_cross(screen)
            pygame.display.flip()
        pygame.time.delay(round(aftertrials[iTrial]*1000))
        # PAUSE AFTER 70 TRIALS =======================================
        if iTrial == PAUSE_TRIAL:
            df_timings.to_csv(log_filename, index=False, header=True, mode='w')
            experiment.pause_phase(screen, PAUSE_DURATION)
finally:
    df_timings.to_csv(log_filename, index=False, header=True, mode='w')

print("Experiment has ended.")
pygame.display.quit()
pygame.quit()
