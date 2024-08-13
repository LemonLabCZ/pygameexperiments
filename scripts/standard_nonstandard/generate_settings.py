import random
import os
from src.standard_nonstandard import settings_generation as generator

random.seed(2024)

# There will be a total of 6 sets, each with 4 blocks
# The order of the blocks always alternates between Homogenous and Alternating, 
# some starting with Homogenous, others with alternating
# The order blocks is constant throughout the entire experiment

os.makedirs("settings/standard_nonstandard", exist_ok=True)
for i in range(1, 100):
    df_trials = generator.create_experiment_trials(i)
    df_trials.to_csv(f"settings/standard_nonstandard/settings{i}.csv")

