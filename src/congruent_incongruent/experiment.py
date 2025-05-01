import pygame
import os
import pandas as pd
from src import utils

def initialize_pygame():
    pygame.init()
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def path_to_stimulus(part, stimulus, type):
    """
    Filename is in a stimuli/congturent_incongruent folder named
    <part>_<id>_<type>.wav where id is id with 0 padding on the left to 2 digits, part is 
    either q for question or a for answer, and type is either initial or final
    """
    return os.path.join(os.getcwd(), 'stimuli', 'congruent_incongruent', f'{part}_{str(stimulus).zfill(2)}_{type}.wav')


def wait_for_answer(screen):
    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_n:
                    return event.key
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        pygame.time.delay(10)

# LOG PREPARATION ===================================

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


# INDIVIDUAL PHASES -------------------------------

def question_phase(screen, question):
    # wait for the answer listening for either A or N (A for yes, N for no)
    screen.fill((0, 0, 0))
    # Add "Stiskněte A pro Ano a N pro Ne" to the question
    question = question + " - Stiskněte A pro Ano a N pro Ne"
    
    utils.show_text(screen, question, 50, (255, 255, 255))
    pygame.display.update()

    answer = wait_for_answer(screen)
    if answer == pygame.K_a:
        answer = 'yes'
    elif answer == pygame.K_n:
        answer = 'no'
    else:
        answer = 'unknown'
    return answer


def pause_phase(screen, duration):
    screen.fill((0, 0, 0))
    utils.show_text(screen, "Pause", 50, (255, 255, 255))
    pause_start = pygame.time.get_ticks()
    while True:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                exit()
        pygame.time.delay(10)
        if pygame.time.get_ticks() - pause_start >= duration * 1000:
            break
    return


def show_fixation_cross(screen):
    screen.fill((0, 0, 0))
    screen = utils.show_text(screen, "+", 50, (255, 255, 255))
    pygame.display.update()
    return
