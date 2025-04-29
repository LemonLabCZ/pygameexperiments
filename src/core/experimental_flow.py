import pandas as pd
import pygame
from datetime import datetime

def prepare_log_table(add_fNIRS = False):
    list_of_columns = ['trial_start','sound_started','sound_duration', 'sound_ended', 'real_sound_duration',
                        'sound_duration_difference','real_trial_duration','trigger_started', 'trigger_ended',
                        'trigger_com_started', 'trigger_com_ended']
    if add_fNIRS:
        list_of_columns.extend(['trigger_cpod_started', 'trigger_cpod_ended'])

    df_timings = pd.DataFrame(columns=list_of_columns)
    return df_timings


def play_trial(iTrial, start_time, df_stimuli, intertrials, should_trigger, path_to_stimulus, 
               fNIRS_trigger=False, trigger_function=None, com=None, trigger_duration=None,
               recalculate_inter_trial=False):
    """_summary_
    Args:
        iTrial (int): Trial index, starting from 0
        start_time (datetime): Start time of the experiment
        df_stimuli (pd.DataFrame): Dataframe with all the stimui
        intertrials (list): List with the intertrial times
        path_to_stimulus (function): Function that returns the path to the stimulus

        fNIRS_trigger (bool): If the fNIRS trigger should be sent
        should_trigger (bool): If the triggers should be sent
        com (string): COM port of the trigger box
        trigger_duration (float): Duration of the trigger
        recalculate_inter_trial (bool, optional): The trigger box generally adds 17 ms to the trigger duration. 
            If this is set to true, the intertrial time will be recalculated to match the total time of the
            trial and the intertrial time. Defaults to False.

    Returns:
        list: returns list with timings of the trial
    """
    timings = dict()
    # This will change in case we need to repeat stimuli, now they just play once
    print(f'{iTrial} started')
    iStimulus = iTrial
    # TODO - add the intertrial time to the timings
    inter_trial = intertrials[iTrial]
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
        trigger_function(5, com, trigger_duration)
        timings['trigger_com_ended'] = get_time_since_start(start_time)
        if fNIRS_trigger:
            timings['trigger_cpod_started'] = get_time_since_start(start_time)
            # THE CPOD TRIGGER IS FROM fNIRS CPOD box, not implemented in this experiment
            # sendTriggerCPOD(cpod, 5, 0.01)
            timings['trigger_cpod_ended'] = get_time_since_start(start_time)
        timings['trigger_ended'] = get_time_since_start(start_time)
    else:
        timings['trigger_started'] = get_time_since_start(start_time)
        timings['trigger_ended'] = timings['trigger_started']
    # Substracts the extraduration of the trigger from the intertrial time (generally 17 ms for the trigger box)
    if recalculate_inter_trial:
        ms_trigger_delay = round((timings['trigger_ended'] - timings['trigger_started'])*1000)
        pygame.time.delay(waittime_ms + inter_trial - ms_trigger_delay)
    else:
        pygame.time.delay(waittime_ms + inter_trial)
    
    sound2play.stop()
    timings['sound_ended'] = get_time_since_start(start_time)
    timings['real_sound_duration'] = timings['sound_ended'] - timings['sound_started']
    timings['sound_duration_difference'] = timings['real_sound_duration'] - timings['sound_duration']
    timings['real_trial_duration'] = timings['sound_ended'] - timings['trial_start']
    return timings


def get_time_since_start(start_time):
    diff = datetime.now() - start_time
    return diff.total_seconds()