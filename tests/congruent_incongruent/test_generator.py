from src.congruent_incongruent.generator import generate_intertrial_intervals
import numpy as np
from scipy import stats


def test_generate_intertrial_intervals():
    min_interval, max_interval = 0.5, 1.5
    intertrial_intervals = generate_intertrial_intervals(100, min_interval, max_interval)
    assert len(intertrial_intervals) == 100
    assert all(min_interval <= x <= max_interval for x in intertrial_intervals)
    