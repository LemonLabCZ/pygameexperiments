import pandas as pd
import numpy as np
from enum import Enum
import os
from collections import defaultdict
import random

N_STANDARD_TRIALS_START = 5
N_DEVIANT_TRIALS = 5
N_STANDARD_TRIALS = 15

POOL = defaultdict(list)

class TrialType(Enum):
    language_spectral = "language_spectral"
    language_duration = "language_duration"
    nonlanguage_spectral = "nonlanguage_spectral"
    nonlanguage_duration = "nonlanguage_duration"


class StimulusType(Enum):
    standard = "standard"
    deviant = "deviant"


def create_experiment_trials(participant_seed=1111):
    """Creates a set of 5 sets 
    """
    # TODO this should be a parameter in the set function and not a global thing
    np.random.seed(participant_seed)
    df_trials = pd.DataFrame(columns = ["trial", "set_number", "block_number",
                                        "trial_type", "stimulus_type"])
    iTrial = 1
    for i in range(1, 5):
        cannot_start_with = None if i == 1 else set_trial_types[-1]
        set_block_numbers, set_trial_types, set_stimulus_types = create_set_trials(i, participant_seed, cannot_start_with=cannot_start_with)
        set_triggers = [int(10*(list(TrialType).index(trial_type) + 1) + list(StimulusType).index(stim_type)) for trial_type, stim_type in zip(set_trial_types, set_stimulus_types)]
        df_set = pd.DataFrame({'trial': range(iTrial, iTrial + len(set_trial_types)),
                               'set_number': i,
                               'block_number': set_block_numbers,
                               'trial_type': set_trial_types,
                               'stimulus_type': set_stimulus_types,
                               'trigger': set_triggers})
        df_set["stimulus"] = df_set.apply(lambda x: generate_stimulus_filename(x["trial_type"], x["stimulus_type"]), axis=1)
        df_trials = pd.concat([df_trials, df_set], axis=0)
        df_trials["trigger"] = df_trials["trigger"].astype(int)
        iTrial += len(set_trial_types)
    return df_trials


def create_set_trials(set_number, participant_seed, cannot_start_with=None):
    """Creates a set of four blocks
    """
    set_trial_types = []
    set_stimulus_types = []
    set_block_numbers = []
    block_order = [TrialType.language_spectral, TrialType.language_duration,
                   TrialType.nonlanguage_spectral, TrialType.nonlanguage_duration]
    # This should be a parameter in the function to make it reproducible
    # Currently the seed is set hidden in the create_experiment_trials, so it should be fine, but just to be sure
    np.random.shuffle(block_order)
    if cannot_start_with is not None and cannot_start_with == block_order[0]:
        block_order.remove(cannot_start_with)
        block_order.insert(np.random.randint(1, 3), cannot_start_with)
    iBlock = 1
    for block in block_order:
        # block seed is set number + index of the trial type. This ensures that language short
        # in the first set will always have the same order of trials
        block_seed = set_number + list(TrialType).index(block) + participant_seed
        # change: we want the order to be different for each child and every block so we use a different seed for every child and every block
        trial_types, stimulus_types = create_block_trials(block, block_seed)
    #    POOL[block].append(stimulus_types)
        set_trial_types.extend(trial_types)
        set_stimulus_types.extend(stimulus_types)
        set_block_numbers.extend([iBlock] * 25)
        iBlock += 1
    return set_block_numbers, set_trial_types, set_stimulus_types


def create_block_trials(trial_type, seed, block=1):
    """Creates a block of 25 trials

    Args:
        trial_type (TrialType): The type of the trial
        seed (int): Seed used to allow same random order across multiple participants
    """
    trial_types = [trial_type] * 25
    stimuli_second_phase = [StimulusType.standard] * (N_DEVIANT_TRIALS + N_STANDARD_TRIALS)
    stimuli_second_phase = insert_deviants(stimuli_second_phase, trial_type,seed)
    if stimuli_second_phase is None:
        raise Exception('Could not distribute deviants')
    stimulus_types = [StimulusType.standard] * N_STANDARD_TRIALS_START
    stimulus_types.extend(stimuli_second_phase)
    return trial_types, stimulus_types


def no_doubles(pauses):
    """
    Checks that two consecutive pauses between deviants are not the same length (so the patricipant does not anticipate the deviant sound)

    Args:
        (list of int): A list of standard counts between deviants
    """
    for i in range(len(pauses)-1):
        if pauses[i] == pauses[i+1]:
            return False
    return True

def insert_deviants(trial_sequence, trial_type, seed):
    """
    Inserts the correct number of deviants with given standard pausses  into a list of standard stimli
    
    Args:
        trial_sequence (list of StimulusType): A list of stimulus types
    """
    # fixed number of standards between deviant - 2, 3, 4 and 5, shuffled randomly
    pauses = [2,3,4,5]
    rand = random.Random(seed)
    for i in range(100):
        # Shuffle until you find such a placement where two adjacent pauses between deviants are not the same length
        pauses = rand.sample(pauses,len(pauses))
        # Check the POOL to see if we used this order for this block type before and keep suffling if we did (we do not want the same participant to hear the identical sequence)
        if no_doubles(pauses) and str(pauses) not in POOL[trial_type]:
            break
    if i == 100:
        return None

    index = 0
    trial_sequence[index] = StimulusType.deviant
    for p in pauses:
        index += p + 1
        trial_sequence[index] = StimulusType.deviant
    # penultimate stimulus must always be deviant
    assert index == 18
    POOL[trial_type].append(str(pauses))

    
    return trial_sequence
        

def count_consecutive_elements(elements):
    result = [1]  # Initialize the result list with 1 for the first element
    for i in range(1, len(elements)):
        if elements[i] == elements[i-1]:
            result.append(result[-1] + 1)  # Increment the count for consecutive elements
        else:
            result.append(1)  # Reset the count for a new element
    return result


def count_consecutive_deviants(elements):
    consecutive = count_consecutive_elements(elements)
    deviant_positions = [index for index, element in enumerate(elements) if element == StimulusType.deviant]
    deviant_counts = [consecutive[i] for i in deviant_positions]
    return deviant_counts


def max_consecutive_deviants(elements):
    return max(count_consecutive_deviants(elements))


def generate_stimulus_filename(trial_type, stimulus_type):
    """Creates a trial
    """
    return f'{trial_type.value}_{stimulus_type.value}.wav'
    
def settings_folder():
    return os.path.join(os.getcwd(), 'settings', 'syllable_comparison')


def generate_settings_filename(participant_id):
    stimuli_filename = os.path.join(settings_folder(), f'settings{participant_id}.csv')
    return stimuli_filename
