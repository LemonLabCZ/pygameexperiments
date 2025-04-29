import pygame
import os
import pandas as pd


def initialize_pygame():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def show_text(screen, text, font_size, color, x, y):
    if screen is None:
        raise ValueError("Screen is not initialized")
    center = screen.get_rect().center
    font = pygame.font.Font("freesansbold.ttf", font_size)
    text = font.render(text, True, color)
    screen.blit(text, (center[0] - text.get_width()/2, center[1] - text.get_height()/2))
    pygame.display.update()


def path_to_stimulus(part, stimulus, type):
    """
    Filename is in a stimuli/congturent_incongruent folder named
    <part>_<id>_<type>.wav where id is id with 0 padding on the left to 2 digits, part is 
    either q for question or a for answer, and type is either initial or final
    """
    return os.path.join(os.getcwd(), 'stimuli', 'congruent_incongruent', f'{part}_{str(stimulus).zfill(2)}_{type}.wav')


def wait_for_answer(screen):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_n:
                    return event.key
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        pygame.time.delay(10)


def prepare_question_log():
    # create a dataframe with the columns: question, answer, time, trial
    df = pd.DataFrame(columns=['question', 'answer', 'time_start', 
                               'time_answered', 'trial'])
    return df

def prepare_trial_log(add_fNIRS = False):
    list_of_columns = ['trial_start','question_started','question_duration', 'question_ended', 'real_question_duration',
                        'answer_started', 'answer_duration', 'answer_ended', 'real_answer_duration',
                        'question_trigger', 'question_cpod_trigger', 'answer_trigger', 'answer_cpod_trigger',
                        'answer_trigger_2', 'answer_trigger_3']
    if add_fNIRS:
        list_of_columns.extend(['trigger_cpod_started', 'trigger_cpod_ended'])

    df_timings = pd.DataFrame(columns=list_of_columns)
    return df_timings