import pandas as pd
import random
from ...src.standard_nonstandard import settings_generation as generator

random.seed(2024)
df_stimuli = pd.read_excel("scripts/JuniorStarparameters.xlsx", sheet_name="StimList")
df_stimuli.head()

# There will be a total of 6 sets, each with 4 blocks
# The order of the blocks always alternates between Homogenous and Alternating, 
# some starting with Homogenous, others with alternating
# The order blocks is constant throughout the entire experiment

df_trials = generator.create_experiment_trials(1)
df_trials.to_csv("settings/standard_nonstandard/settings1.csv")

for i in range(1, 64):
    df_trials = generator.create_experiment_trials(i)
    df_trials.to_csv(f"settings/standard_nonstandard/settings{i}.csv")