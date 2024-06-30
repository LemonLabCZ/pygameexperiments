import numpy as np

def generate_block_intertrials(participant_id, intertrial_range, size):
    """The goal is to have the experiment the same length, but wary between participants.
    So we first generate the same random set of intertrials for all participants, and then
    permutate it per participant.

    Args:
        participant_id (int): Integer to be used as a seed
        intertrial_range (tuple): Tuple with the minimum and maximum intertrial time
        size(int): Number of intertrials to generate

    Returns:
        list(int): List with the intertrial times as milliseconds
    """
    # generate nbew random generator
    common_rng = np.random.default_rng(9999)
    # generate the random times
    block_intertrials = common_rng.integers(intertrial_range[0], intertrial_range[1], size=size)
    unique_rng = np.random.default_rng(participant_id)
    unique_rng.shuffle(block_intertrials)
    return block_intertrials


def generate_intertrials(participant_id, intertrial_range, size):
    """Generates the intertrial times for a participant

    Args:
        participant_id (int): Integer to be used as a seed
        intertrial_range (tuple): Tuple with the minimum and maximum intertrial time
        size(int): Number of intertrials to generate

    Returns:
        list(int): List with the intertrial times as milliseconds
    """
    rng = np.random.default_rng(participant_id)

    if isinstance(intertrial_range, int):
        return [intertrial_range] * size
    if len(intertrial_range) == 1:
        return  [intertrial_range[0]] * size
    if len(intertrial_range) == 2:
        return rng.choices(range(intertrial_range[0], intertrial_range[1]), k=size)
    raise ValueError('Intertrial range should have 1 or 2 values')

