import pandas as pd
import random
import numpy as np
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

# There will be a total of 6 sets, each with 4 blocks
# The order of the blocks always alternates between Homogenous and Alternating, some starting with Homogenous, others with alternating
# The order blocks is constant throughout the entire experiment

# sample 12 trial types so that each one appears 6 times
# repeat each trial type 6 times and save to a list
set_starting_types = random.sample([TrialType.Czech, TrialType.Ostrava], counts=[6, 6], k=12)

# assign the trial types to the blocks in order
def create_block_trials(starting_trial_type, block_type):
    if block_type == BlockType.Alternating:
        types = [starting_trial_type, opposing_type(starting_trial_type),
           starting_trial_type, opposing_type(starting_trial_type)] 
    if block_type == BlockType.Homogenous:
        types = [starting_trial_type] * 4
    block_types = [block_type] * 4
    return types, block_types

def create_set_trials(starting_trial_type):
    out = [create_block_trials(starting_trial_type, BlockType.Homogenous),
            create_block_trials(opposing_type(starting_trial_type), BlockType.Alternating),
            create_block_trials(starting_trial_type, BlockType.Homogenous),
            create_block_trials(opposing_type(starting_trial_type), BlockType.Alternating)]
    conditions = [item[0] for item in out]
    conditions = flatten(conditions)
    block_types = [item[1] for item in out]
    block_types = flatten(block_types)
    # repeat 1 to 4 four times so that i have a list 1111222233334444
    block_number = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]
    return conditions, block_types, block_number

def create_experiment_conditions(set_starting_types):
    df_trials = pd.DataFrame(columns=["trial", "condition", "block_number",
                                      "block_type", "set_number"])
    trial = 1
    set_number = 1
    for starting_type in set_starting_types:
        conditions, block_types, block_number = create_set_trials(starting_type)
        conditions = [typ.value for typ in conditions]
        df_set = pd.DataFrame({'trial':range(trial, trial+16),
                              'condition': conditions,
                              'block_number': block_number,
                              'block_type':block_types,
                              'set_number':set_number})
        df_trials = pd.concat([df_trials, df_set], axis=0)
        trial += len(conditions)
        set_number += 1
    df_trials = df_trials.set_index("trial", drop=False)
    return df_trials

df_trials = create_experiment_conditions(set_starting_types)
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
