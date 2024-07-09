import random
from src.syllable_comparison import settings_generation as generator


def test_distribute_deviants():
    trial_sequence = [generator.StimulusType.standard] * 13 + [generator.StimulusType.deviant] * 7
    assert generator.max_consecutive_deviants(trial_sequence) == 7
    for i in range(50):
        trial_sequence = generator.distribute_deviants(trial_sequence, 999)
        assert generator.max_consecutive_deviants(trial_sequence) <= 2


def test_create_block_trials():
    """This tests whether the block of trials is created correctly withe the correct number of deviants and standards.
    """
    for i in range(10):
        trial_type = random.choice(list(generator.TrialType.__members__.values()))
        trial_types, stimulus_types = generator.create_block_trials(trial_type, 999)
        assert len(trial_types) == 25
        assert len(stimulus_types) == 25
        # assert all trial types are trial_type
        assert all(trial == trial_type for trial in trial_types)
        assert sum(stimulus == generator.StimulusType.deviant for stimulus in stimulus_types) == generator.N_DEVIANT_TRIALS
        assert sum(stimulus == generator.StimulusType.standard for stimulus in stimulus_types) == generator.N_STANDARD_TRIALS + generator.N_STANDARD_TRIALS_START
        assert all(stimulus == generator.StimulusType.standard for stimulus in stimulus_types[:5])


def test_set_not_starting_with_previous():
    for i in range(100):
        _, trial_types, _ = generator.create_set_trials(1, cannot_start_with=generator.TrialType.language_duration)
        assert trial_types[0] != generator.TrialType.language_duration
    

def test_create_set_trials():
    block_numbers, trial_types, stimulus_types = generator.create_set_trials(1)
    assert len(trial_types) == 100


def test_create_experiment_trials():
    for i in range(10):
        df_trials = generator.create_experiment_trials(i)
        assert len(df_trials) == 500
        assert all(df_trials["trial"].unique() == range(1, 501))
        assert all(df_trials["block_number"].unique() == range(1, 5))
        assert all(df_trials["set_number"].unique() == range(1, 6))
        assert all(df_trials["stimulus_type"].unique() == [generator.StimulusType.standard, generator.StimulusType.deviant])
        assert all(df_trials["stimulus"].apply(lambda x: x.endswith(".wav")))


def test_same_stimuli_order():
    """This tests whether in two experiments the order of standard and deviant trials in each
    trial type is the same. 
    """
    def get_stimuli(df_trials, type, set):
        stimuli = df_trials.loc[(df_trials["trial_type"] == type) & (df_trials["set_number"] == set)]["stimulus_type"]
        return stimuli
    # generate 10 different pairs of experiments
    for i in range(0,10):
        df_trials1 = generator.create_experiment_trials(i)
        df_trials2 = generator.create_experiment_trials(i + 10)
        # compare the order of stimuli for each type and for each set
        # the order of deviant/standard should be the same in each settings
        for set in range(1, 6):
                for type in generator.TrialType:
                    stimuli1 = get_stimuli(df_trials1, type, set)
                    stimuli2 = get_stimuli(df_trials2, type, set)
                    assert all(stimuli1.values == stimuli2.values)


def test_different_block_order():
    """This tests whether in two experiments the order of the blocks is different for each participant.
    The order of 
    """
    for i in range(0,10):
        df_trials1 = generator.create_experiment_trials(i)
        df_trials2 = generator.create_experiment_trials(i + 10)
        trial_order1 = df_trials1["trial_type"].values
        trial_order2 = df_trials2["trial_type"].values
        assert not all(trial_order1 == trial_order2)