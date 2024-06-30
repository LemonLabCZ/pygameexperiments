from src.syllable_comparison import settings_generation as generator

df_trials = generator.create_experiment_trials()
df_trials.head()
df_trials.to_csv("settings/syllable_comparison/settings1.csv")

for i in range(1, 100):
    df_trials = generator.create_experiment_trials(i)
    df_trials.to_csv(generator.generate_settings_filename(i))