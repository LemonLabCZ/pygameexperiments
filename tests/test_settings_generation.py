from ..src.standard_nonstandard import settings_generation as generator

def test_generate_stimulus_filename():
    assert generator.generate_stimulus_filename(generator.TrialType.Czech, 1) == "st1.wav"
    assert generator.generate_stimulus_filename(generator.TrialType.Ostrava, 2) == "nst2.wav"
    assert generator.generate_stimulus_filename(generator.TrialType.Czech, 3) == "st3.wav"
    assert generator.generate_stimulus_filename(generator.TrialType.Ostrava, 4) == "nst4.wav"


def test_create_alternating_block_trials():
    types, block_types, block_number = generator.create_block_trials(generator.TrialType.Czech, 
                                                                     generator.BlockType.Alternating, 1)
    # assert that the types are czech, ostrava, czech, ostrava
    assert types == [generator.TrialType.Czech, generator.TrialType.Ostrava,
                     generator.TrialType.Czech, generator.TrialType.Ostrava]
    assert block_types == [generator.BlockType.Alternating] * 4
    assert block_number == [1] * 4


def test_create_homogenous_block_trials():
    types, block_types, block_number = generator.create_block_trials(generator.TrialType.Czech, 
                                                                     generator.BlockType.Homogenous, 4)
    # assert that the types are czech, czech, czech, czech
    assert types == [generator.TrialType.Czech] * 4
    assert block_types == [generator.BlockType.Homogenous] * 4
    assert block_number == [4] * 4


def test_create_set_trials():
    conditions, block_types, block_numbers = generator.create_set_trials(0)
    czech_homogenous_expected = [generator.TrialType.Czech] * 4
    czech_alternating_expected = [generator.TrialType.Czech, generator.TrialType.Ostrava, 
                                  generator.TrialType.Czech, generator.TrialType.Ostrava]
    assert len(conditions) == 16
    assert conditions[0:4] == czech_homogenous_expected
    assert block_types[0:4] == [generator.BlockType.Homogenous] * 4
    assert block_numbers[0:4] == [1] * 4
    
    assert conditions[4:8] == czech_alternating_expected
    assert block_types[4:8] == [generator.BlockType.Alternating] * 4
    assert block_numbers[4:8] == [2] * 4

    conditions, block_types, block_numbers = generator.create_set_trials(1)
    assert conditions[0:4] == czech_alternating_expected
    assert conditions[12:16] == czech_homogenous_expected


def test_create_experiment_trials():
    df_trials1 = generator.create_experiment_trials(1)
    df_trials2 = generator.create_experiment_trials(2)
    assert df_trials1.shape[0] == 96
    assert (df_trials1["condition"] == df_trials2["condition"]).all()
    assert (df_trials1.tail(1)["stimulus_number"] == 6).all()
    assert (df_trials2.tail(1)["stimulus_number"] == 1).all()

