import src.syllable_comparison.experiment as experiment


def test_block_intertrial_generation():
    duration_range, size = (1000, 2000), 100
    block_intertrials = experiment.generate_block_intertrials(1, duration_range, size)
    duration = block_intertrials.sum()

    for i in range(1, 10):
        block_intertrials = experiment.generate_block_intertrials(i, duration_range, size)
        assert all(block_intertrials >= 1000)
        assert all(block_intertrials <= 2000)
        assert block_intertrials.sum() == duration


def test_intertrial_generation():
    participant_id, duration_range, size = 1, 100, 100
    assert True