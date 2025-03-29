import random
import numpy as np


def generate_intertrial_intervals(n_trials, min_intertrial_interval, max_intertrial_interval, seed=None):
  """This is a function that generates a list of intertrial intervals.
  The interprials should follow an exponential distribution between min and max in seconds.

  Args:
      n_trials (int): Number of trials
      min_intertrial_interval (float): Minimum intertrial interval in seconds
      max_intertrial_interval (float): Maximum intertrial interval in seconds
      seed (int, optional): Seed for the random number generator. Defaults to None.
  """
  intertrial_intervals = []

  if seed is not None:
    random.seed(seed)

  possible_intervals = np.linspace(min_intertrial_interval, max_intertrial_interval, 50)
  weights = np.exp(-possible_intervals / min_intertrial_interval)
  weights /= weights.sum()

  for i in range(n_trials):
    intertrial_intervals.append(np.random.choice(possible_intervals, p=weights))

  return intertrial_intervals
