import pygame
import os
import pandas as pd
from src import utils
import time
from moviepy import VideoFileClip

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
    list_of_columns = ['trial_start','question_started','question_duration', 'question_ended', 
                        'answer_started', 'answer_duration', 'answer_ended',
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


def video_phase(screen, video):
    play_video(screen, video)


def pause_phase(screen, duration):
    screen.fill((0, 0, 0))
    utils.show_text(screen, "Pauza", 50, (255, 255, 255))
    pause_start = pygame.time.get_ticks()
    while True:
        ## every second update text showing remaining time
        remaining_time = duration - (pygame.time.get_ticks() - pause_start) // 1000
        if remaining_time > 0 and remaining_time < (duration - 5):
            screen.fill((0, 0, 0))
            utils.show_text(screen, f"{remaining_time}", 50, (255, 255, 255))
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


def play_video(screen, video_path):
    clock = pygame.time.Clock()
    clip = VideoFileClip(video_path)

    # Resize the video to fit the screen
    video_width, video_height = clip.size
    screen_width, screen_height = screen.get_size()
    scale_w = screen_width / video_width
    scale_h = screen_height / video_height
    scale_factor = min(scale_w, scale_h) # Use the smaller scale factor to fit entirely
    clip = clip.resized(scale_factor)
    scaled_video_width = int(video_width * scale_factor)
    scaled_video_height = int(video_height * scale_factor)

    # Calculate the new dimensions of the scaled video
    scaled_video_width = int(video_width * scale_factor)
    scaled_video_height = int(video_height * scale_factor)

    # Calculate the top-left position to center the scaled video on the fullscreen
    blit_x = (screen_width - scaled_video_width) // 2
    blit_y = (screen_height - scaled_video_height) // 2
        
    start_time = time.time()
    frame_count = 0

    # Play the video frame by frame
    for frame in clip.iter_frames(fps=60, dtype="uint8"):
        # Convert the frame (numpy array) to a Pygame surface
        frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        scaled_frame = pygame.transform.smoothscale(frame_surface, (scaled_video_width, scaled_video_height)) # Use smoothscale for better quality
        # Blit the frame onto the screen
        screen.blit(scaled_frame, (blit_x, blit_y))
        pygame.display.flip()
        clock.tick(clip.fps)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                exit()

    end_time = time.time()
    actual_duration = end_time - start_time
    actual_fps = frame_count / actual_duration if actual_duration > 0 else 0
    print(f"Pause video finished. Actual duration: {actual_duration:.2f}s, Actual avg FPS: {actual_fps:.2f}")
    clip.close()
