import random
import numpy as np
import pandas as pd
from typing import Optional

def generate_stimulus_answer_pairs(seed=None):
  """This is a function that generates a list of stimulus answer pairs.
  trial types are four different types, either initial or final. 
  The stimulus is a number between 1 and 35. The trials are structured in a way that the stimulus 1
  should come with all 4 different conditions ((congruent, congruent), 
  (congruent, incongruent), (incongruent, congruent), (incongruent, incongruent)).
  """
  if seed is not None:
    random.seed(seed)
  df_possible_stimuli = pd.DataFrame(columns=['stimulus', 'question', 'answer'], 
                                     index = range(140))
  df_possible_stimuli['stimulus'] = np.tile(np.arange(1, 36), 4)
  df_possible_stimuli['question'] = np.concatenate([np.tile(['initial'], 70), 
                                                   np.tile(['final'], 70)])
  df_possible_stimuli['answer'] = np.concatenate([np.tile(['initial'], 35), 
                                                  np.tile(['final'], 35), 
                                                  np.tile(['initial'], 35), 
                                                  np.tile(['final'], 35)])
  df_possible_stimuli['condition'] = df_possible_stimuli['question'] + '-' + df_possible_stimuli['answer']
  shuffled_stimuli = shuffle_with_constraints_greedy(df_possible_stimuli, max_restarts=10)
  if shuffled_stimuli is None:
    raise ValueError("Could not generate a valid stimulus-answer pair.")
  df_possible_stimuli = shuffled_stimuli
  return df_possible_stimuli
  

def check_constraints(df: pd.DataFrame) -> bool:
    """
    Checks if a DataFrame satisfies the constraints:
    - No two consecutive rows have the same 'stimulus'.
    - No two consecutive rows have the same 'condition'.

    Args:
        df (pd.DataFrame): The DataFrame to check.

    Returns:
        bool: True if constraints are satisfied, False otherwise.
    """
    # Iterate through the DataFrame starting from the second row
    for i in range(1, len(df)):
        # Check if the current ID is the same as the previous one
        if df.iloc[i]['stimulus'] == df.iloc[i-1]['stimulus']:
            return False
        # Check if the current Condition is the same as the previous one
        if df.iloc[i]['condition'] == df.iloc[i-1]['condition']:
            return False
    # If the loop completes without returning False, constraints are met
    return True


def shuffle_with_constraints_greedy(df: pd.DataFrame, max_restarts: int = 10) -> Optional[pd.DataFrame]:
    """
    Attempts to shuffle the rows of a DataFrame using a greedy algorithm,
    ensuring that no two consecutive rows have the same 'ID' or 'Condition'.

    Args:
        df (pd.DataFrame): The input DataFrame with 'ID' and 'Condition' columns.
        max_restarts (int): The maximum number of times to restart the greedy
                           process if it gets stuck.

    Returns:
        Optional[pd.DataFrame]: The shuffled DataFrame satisfying the constraints,
                                or None if a valid shuffle wasn't found within max_restarts.
    """
    if not {'stimulus', 'condition'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'stimulus' and 'condition' columns.")

    n_rows = len(df)
    if n_rows <= 1:
        return df.copy() # No shuffling needed

    original_indices = list(df.index)
    
    for attempt in range(max_restarts):
        print(f"Greedy Shuffle Attempt: {attempt + 1}/{max_restarts}")
        
        # Make a copy of available indices for this attempt
        available_indices = original_indices[:]
        random.shuffle(available_indices) # Shuffle available indices

        # Start with a random row
        first_index = available_indices.pop(0)
        result_indices = [first_index]
        
        stuck = False
        while len(result_indices) < n_rows:
            last_index = result_indices[-1]
            last_row = df.loc[last_index]
            last_id = last_row['stimulus']
            last_condition = last_row['condition']

            # Find valid next candidates from the remaining available indices
            valid_next_indices = [
                idx for idx in available_indices
                if df.loc[idx]['stimulus'] != last_id and df.loc[idx]['condition'] != last_condition
            ]

            if not valid_next_indices:
                # Greedy approach got stuck, break and restart
                print(f"  Stuck at step {len(result_indices)}. No valid next row found.")
                stuck = True
                break

            # Choose a random valid next index
            next_index = random.choice(valid_next_indices)
            result_indices.append(next_index)
            available_indices.remove(next_index) # Remove chosen index from available pool

        if not stuck:
            # Successfully placed all rows
            print("Successfully found a valid greedy shuffle.")
            shuffled_df = df.loc[result_indices].reset_index(drop=True)
            return shuffled_df

    # If all restart attempts failed
    print(f"Warning: Could not find a valid shuffle satisfying the constraints after {max_restarts} restarts.")
    return None


def generate_aftertrial_intervals(n_trials, min_intertrial_interval, 
                                  max_intertrial_interval, seed=None):
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


def generate_aftertrial_intervals_torsten(seed=None):
  """This is a function that generates a list of intertrial intervals.
  The interprials should follow an exponential distribution between min and max in seconds.

  Args:
      seed (int, optional): Seed for the random number generator. Defaults to None.
  """
  if seed is not None:
    random.seed(seed)
  intertrials = [2] * 37 + [4] * 19 + [8] * 10 + [16] * 3
  return np.random.choice(intertrials, 69, replace=False).tolist()


def generate_intertrial_intervals(n_trials, min_s, max_s, seed=None):
  """ Generate times between min adn max (in seconds), uniform distribution
  """
  if seed is not None:
    random.seed(seed)
  intertrial_intervals = np.random.uniform(min_s, max_s, n_trials)
  return intertrial_intervals.tolist()


def generate_potential_questions(seed=None):
  """This is a function that generates a potential question for the trial.
  The question is generated by adding a random number to the trial index.

  Args:
      trial_index (int): Trial index
      seed (int, optional): Seed for the random number generator. Defaults to None.
  """
  if  seed is not None:
    random.seed(seed)
  potential_questions = ["Bylo v odpovědi vlastní jméno?", 
                         "Říkal odpověď muž?",
                         "Říkal odpověď žena?", 
                         "Byla odpověď v minulém čase?",
                         "Byla odpověď v přítomném čase?"]
  potential_questions = potential_questions * 7
  return random.sample(potential_questions, len(potential_questions))


def generate_question_trials(seed=None):
  """This is a function that generates a list of question trials.
  the question trials come every 2 3 or 4 trials. There should be 35 trials in total

  Args:
      n_trials (int): Number of trials
      seed (int, optional): Seed for the random number generator. Defaults to None.
  """
  if seed is not None:
    random.seed(seed)
  question_trials = [2] * 5 + [3] * 8 + [4] * 9 + [5] * 8 + [6] * 5
  random.shuffle(question_trials)
  question_trials = np.cumsum(question_trials)
  return question_trials
  