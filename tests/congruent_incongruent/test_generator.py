import src.congruent_incongruent.generator as generator


def test_generate_intertrial_intervals():
    min_interval, max_interval = 0.5, 1.5
    intertrial_intervals = generator.generate_intertrial_intervals(100, min_interval, max_interval)
    assert len(intertrial_intervals) == 100
    assert all(min_interval <= x <= max_interval for x in intertrial_intervals)
    

def test_generate_intertrial_intervals_torsten():
    # assert that it has the length of 69
    intertrial_intervals = generator.generate_intertrial_intervals_torsten()
    assert len(intertrial_intervals) == 69


def test_generate_question_trials():
    question_trials = generator.generate_question_trials()
    # assert that the max is 140
    assert question_trials.max() == 140
    # assert that the min is larger than 0
    assert question_trials.min() > 0
    # assert that there are 35 of them
    assert len(question_trials) == 35
    # assert that no two are next to each other
    assert all(abs(question_trials[i] - question_trials[i + 1]) > 1 for i in range(len(question_trials) - 1))


def test_generate_stimulus_ansewr_pairs():
    stimulus_answer_intervals = generator.generate_stimulus_answer_pairs(seed=42)
    # assert it is a data frame with 140 rows and 3 columns (stimulus, question, answer)
    assert stimulus_answer_intervals.shape == (140, 4)
    # assert that the stimulus is between 1 and 35
    assert all(stimulus_answer_intervals['stimulus'].between(1, 35))
    # assert that the question is either initial or final
    assert all(stimulus_answer_intervals['question'].isin(['initial', 'final']))
    # assert that the answer is either initial or final
    assert all(stimulus_answer_intervals['answer'].isin(['initial', 'final']))
    # assert that the stimulus is repeated 4 times
    assert all(stimulus_answer_intervals['stimulus'].value_counts() == 4)
    assert all(stimulus_answer_intervals['condition'].isin(['initial-initial', 
                                                            'initial-final', 
                                                            'final-initial', 
                                                            'final-final']))
    # assert that the question_answer is repeated 4 times
    assert all(stimulus_answer_intervals['condition'].value_counts() == 35)
    # generate unique combinations of stimulus and question_answer
    stimulus_answer_intervals['stimulus_question_answer'] = (
        stimulus_answer_intervals['stimulus'].astype(str) + '-' + stimulus_answer_intervals['condition'])
    # assert that the stimulus_question_answer is unique
    assert stimulus_answer_intervals['stimulus_question_answer'].is_unique
    # assert that no two consecutive rows have the same stimulus (first is always Nan
    assert all(stimulus_answer_intervals['stimulus'].diff().abs()[1:] > 0)

