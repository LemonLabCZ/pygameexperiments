import pandas as pd
import numpy as np
from enum import Enum
import os

N_STANDARD_TRIALS_START = 5
N_DEVIANT_TRIALS = 7
N_STANDARD_TRIALS = 13


class TrialType(Enum):
    language_spectral = "language_spectral"
    language_duration = "language_duration"
    nonlanguage_spectral = "nonlanguage_spectral"
    nonlanguage_duration = "nonlanguage_duration"


class StimulusType(Enum):
    standard = "standard"
    deviant = "deviant"


def create_experiment_trials(random_seed=1111):
    """Creates a set of 5 sets 
    """
    # TODO this should be a parameter in the set function and not a global thing
    np.random.seed(random_seed)
    df_trials = pd.DataFrame(columns = ["trial", "set_number", "block_number",
                                        "trial_type", "stimulus_type"])
    iTrial = 1
    for i in range(1, 6):
        cannot_start_with = None if i == 1 else set_trial_types[-1]
        set_block_numbers, set_trial_types, set_stimulus_types = create_set_trials(i, cannot_start_with=cannot_start_with)
        df_set = pd.DataFrame({'trial': range(iTrial, iTrial + len(set_trial_types)),
                               'set_number': i,
                               'block_number': set_block_numbers,
                               'trial_type': set_trial_types,
                               'stimulus_type': set_stimulus_types})
        df_set["stimulus"] = df_set.apply(lambda x: generate_stimulus_filename(x["trial_type"], x["stimulus_type"]), axis=1)
        df_trials = pd.concat([df_trials, df_set], axis=0)
        iTrial += len(set_trial_types)
    return df_trials


def create_set_trials(set_number, cannot_start_with=None):
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
        block_seed = set_number + list(TrialType).index(block)
        trial_types, stimulus_types = create_block_trials(block, block_seed)
        set_trial_types.extend(trial_types)
        set_stimulus_types.extend(stimulus_types)
        set_block_numbers.extend([iBlock] * 25)
        iBlock += 1
    return set_block_numbers, set_trial_types, set_stimulus_types


def create_block_trials(trial_type, seed):
    """Creates a block of 25 trials

    Args:
        trial_type (TrialType): The type of the trial
        seed (int): Seed used to allow same random order across multiple participants
    """
    trial_types = [trial_type] * 25
    stimulus_types = [StimulusType.standard] * 25
    stimulus_types[6] = stimulus_types[9]  = stimulus_types[13] = stimulus_types[15] = stimulus_types[18] = stimulus_types[20]  = stimulus_types[23] = StimulusType.deviant
    stimuli_second_phase = [StimulusType.deviant] * N_DEVIANT_TRIALS + [StimulusType.standard] * N_STANDARD_TRIALS
    stimuli_second_phase = distribute_deviants(stimuli_second_phase, seed)
    if stimuli_second_phase is None:
        raise Exception('Could not distribute deviants')
    stimulus_types = [StimulusType.standard] * N_STANDARD_TRIALS_START
    stimulus_types.extend(stimuli_second_phase)
    return trial_types, stimulus_types


def distribute_deviants(trial_sequence, seed):
    """This will be a bruteforce method to distribute deviants. 
    I just shuffle until the condition is met. Generally takes only 1-10 iterations.

    Args:
        trial_sequence (list of StimulusType): A list of stimulus types
    """
    local_random = np.random.default_rng(seed)
    for i in range(100):
        trial_sequence = local_random.permutation(trial_sequence)
        if max_consecutive_deviants(trial_sequence) <= 2:
            return trial_sequence
    return None


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
