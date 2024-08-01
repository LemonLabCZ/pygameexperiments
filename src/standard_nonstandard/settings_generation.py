from enum import Enum
from collections import deque
import pandas as pd
import numpy as np
from dataclasses import dataclass
import random

@dataclass
class Parameters:
    n_repetitions = 4
    n_stimuli_per_block = 4


class BlockType(Enum):
    Alternating = "Alternating"
    Homogenous = "Homogenous"

    
class TrialType(Enum):
    Czech = "st"
    Ostrava = "d"


def opposing_type(trial_type):
    # validate trial type being class TrialType
    if trial_type == TrialType.Czech:
        return TrialType.Ostrava
    if trial_type == TrialType.Ostrava:
        return TrialType.Czech


def flatten(lst):
    flattened_list = [item for sublist in lst for item in sublist]
    return flattened_list


# assign the trial types to the blocks in order
def create_block_trials(starting_trial_type, block_type, block_number):
    if block_type == BlockType.Alternating:
        types = [starting_trial_type, opposing_type(starting_trial_type),
           starting_trial_type, opposing_type(starting_trial_type)] 
    if block_type == BlockType.Homogenous:
        types = [starting_trial_type] * Parameters.n_stimuli_per_block
    block_types = [block_type] * Parameters.n_stimuli_per_block
    block_number = [block_number] * Parameters.n_stimuli_per_block
    return types, block_types, block_number
    

def create_set_trials(shift_number):
    """_summary_
    Args:
        starting_trial_type (_type_): _description_
        settings_number (_type_): Generally describes which settings in order it is
            The script generates same order for two consecutive settings 

    Returns:
        _type_: _description_
    """
    out = deque([create_block_trials(TrialType.Czech, BlockType.Homogenous, 1),
            create_block_trials(TrialType.Czech, BlockType.Alternating, 2),
            create_block_trials(TrialType.Ostrava, BlockType.Homogenous, 3),
            create_block_trials(TrialType.Ostrava, BlockType.Alternating, 4)])
    # Shits the list by the settings number positives shift to the right, negatives to the left
    out.rotate(-(shift_number))
    out = list(out)
    
    conditions = flatten([item[0] for item in out])
    block_types = flatten([item[1] for item in out])
    block_numbers = flatten([item[2] for item in out])
    return conditions, block_types, block_numbers


def draw_stimuli(seed):
    stimuli_all = list(range(1,98)) + list(range(99, 134))
  
    return random.sample(stimuli_all, 64)
    
def create_experiment_trials(settings_number):
    """Generate dataframe with all trial settings

    Args:
        settings_number (_type_): _description_

    Returns:
        _type_: _description_
    """
    df_trials = pd.DataFrame(columns=["trial", "condition", "block_number",
                                      "block_type", "set_number", "stimulus_number",
                                      "stimulus"])
    trial = 1
    # shifting number is 0 for 1 and 2, 1 for 3 and 4, 2 for 5 and 6 and so on
    shift_number = np.floor((settings_number - 1) / 2).astype(int)
    
    sentence_variants = draw_stimuli(settings_number)

    for set_number in range(1, Parameters.n_repetitions + 1):
        conditions, block_types, block_numbers = create_set_trials(shift_number)
        triggers = [int(10 * block_number + (n % 4 + 1)) for n, block_number in enumerate(block_numbers)]
        df_set = pd.DataFrame({'trial': range(trial, trial + len(conditions)),
                              'condition': conditions,
                              'block_number': block_numbers,
                              'block_type': block_types,
                              'set_number': set_number,
                              'stimulus_number': sentence_variants[trial - 1 : trial - 1 + len(conditions)],
                              'trigger': triggers})
        # stimulus is a f'{condition}_{stimulus_number}.wav' for each row
        df_set["stimulus"] = df_set.apply(lambda x: generate_stimulus_filename(x["condition"], x["stimulus_number"]), axis=1)
        df_trials = pd.concat([df_trials, df_set], axis=0)
        trial += len(conditions)

    df_trials = df_trials.set_index("trial", drop=False)
    # Not generating intertrials at this point
    # df_trials["inter_trial"] = np.array([round(x) for x in (np.random.random(df_trials.shape[0]) * 200) + 900])
    return df_trials


def create_experiment_inter_trials(rang, settings_number):
    """Generates inter trial intervals for the experiment

    Args:
        rang (_type_): _description_
        settings_number (_type_): _description_

    Returns:
        _type_: _description_
    """
    np.random.seed(1111)
    df_inter_trials = pd.DataFrame(columns=["block", "inter_trial"])
    df_inter_trials["block"] = range(1, Parameters.n_repetitions)
    df_inter_trials["inter_trial"] = np.random.randint(rang[0], rang[1], size=Parameters.n_repetitions - 1)
    return df_inter_trials


def generate_stimulus_filename(condition, stimulus_number):
    """_summary_

    Args:
        condition (Enum.TrialType): Enum of TrialType (Czech, Ostrava)
        stimulus_number (int): just a number

    Returns:
        string : name of the file with the stimulus
    """
    return f"{stimulus_number:02}_{condition.value}_4.wav"

