import os
from src.syllable_comparison import settings_generation as generator

os.makedirs(generator.settings_folder(), exist_ok=True)

df_trials = generator.create_experiment_trials()
df_trials.head()
df_trials.to_csv(generator.generate_settings_filename(1))

for i in range(1, 100):
    df_trials = generator.create_experiment_trials(i)
    df_trials.to_csv(generator.generate_settings_filename(i))