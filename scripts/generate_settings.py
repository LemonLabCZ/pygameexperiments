import pandas as pd
import random
import numpy as np
from collections import deque
from enum import Enum
random.seed(2024)
df_stimuli = pd.read_excel("scripts/JuniorStarparameters.xlsx", sheet_name="StimList")
df_stimuli.head()

df_settings = pd.DataFrame(columns=["trial", "filename", "condition",
                                    "block_number", "block_type", "set_number"])

## define block types
class BlockType(Enum):
    Alternating = "Alternating"
    Homogenous = "Homogenous"

    
class TrialType(Enum):
    Czech = "st"
    Ostrava = "nst"


def opposing_type(trial_type):
    # validate trial type being class TrialType
    if trial_type == TrialType.Czech:
        return TrialType.Ostrava
    if trial_type == TrialType.Ostrava:
        return TrialType.Czech


def flatten(lst):
    flattened_list = [item for sublist in lst for item in sublist]
    return flattened_list

# Sentences go either °1 to 6 or 6 to 1
sentence_order_variants = ["ascending", "descending"]

sencence_variants = [1,2,3,4,5,6]
# There will be a total of 6 sets, each with 4 blocks
# The order of the blocks always alternates between Homogenous and Alternating, 
# some starting with Homogenous, others with alternating
# The order blocks is constant throughout the entire experiment

# sample 12 trial types so that each one appears 6 times
# repeat each trial type 6 times and save to a list
set_starting_types = random.sample([TrialType.Czech, TrialType.Ostrava], counts=[6, 6], k=12)

# assign the trial types to the blocks in order
def create_block_trials(starting_trial_type, block_type, block_number):
    if block_type == BlockType.Alternating:
        types = [starting_trial_type, opposing_type(starting_trial_type),
           starting_trial_type, opposing_type(starting_trial_type)] 
    if block_type == BlockType.Homogenous:
        types = [starting_trial_type] * 4
    block_types = [block_type] * 4
    block_number = [block_number] * 4
    return types, block_types, block_number

def create_set_trials(settings_number):
    """_summary_

    Args:
        starting_trial_type (_type_): _description_
        settings_number (_type_): Generally describes which settings in order it is
            The script generates 

    Returns:
        _type_: _description_
    """
    out = deque([create_block_trials(TrialType.Czech, BlockType.Homogenous, 1),
            create_block_trials(TrialType.Ostrava, BlockType.Alternating, 2),
            create_block_trials(TrialType.Czech, BlockType.Homogenous, 3),
            create_block_trials(TrialType.Ostrava, BlockType.Alternating, 4)])
    # Shits the list by the settings number
    out.rotate(settings_number-1)
    out = list(out)
    
    conditions = flatten([item[0] for item in out])
    block_types = flatten([item[1] for item in out])
    block_numbers = flatten([item[2] for item in out])
    return conditions, block_types, block_numbers


def create_experiment_conditions(settings_number):
    df_trials = pd.DataFrame(columns=["trial", "condition", "block_number",
                                      "block_type", "set_number"])
    trial = 1
    for set_number in range(1, 7):
        conditions, block_types, block_numbers = create_set_trials(settings_number)
        conditions = [typ.value for typ in conditions]
        df_set = pd.DataFrame({'trial':range(trial, trial+len(conditions)),
                              'condition': conditions,
                              'block_number': block_numbers,
                              'block_type': block_types,
                              'set_number': set_number})
        df_trials = pd.concat([df_trials, df_set], axis=0)
        trial += len(conditions)
    df_trials = df_trials.set_index("trial", drop=False)
    return df_trials


df_trials = create_experiment_conditions(1)
st_trials = df_trials.loc[df_trials.condition == "st"]["trial"].to_list()
nst_trials = df_trials.loc[df_trials.condition == "nst"]["trial"].to_list()

# Shuffle the table df stimuli
df_stimuli = df_stimuli.sample(frac=1).reset_index()
df_stimuli.loc[df_stimuli.condition == "st", "trial"] = st_trials
df_stimuli.loc[df_stimuli.condition == "nst", "trial"] = nst_trials
df_stimuli["trial"] = df_stimuli["trial"].astype(int)
df_stimuli = df_stimuli.set_index("trial")

df_trials = df_trials.join(df_stimuli, rsuffix="_stim")

df_trials["inter_trial"] = np.array([round(x) for x in (np.random.random(df_trials.shape[0])*200) + 900])

df_trials.file_name.value_counts()
df_trials.to_excel("junior_test_settings.xlsx")
