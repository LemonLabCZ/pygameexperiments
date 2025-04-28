import pygame
import os


def initialize_pygame():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    return screen


def show_text(screen, text, font_size, color, x, y):
    # check if screen is initialized
    if screen is None:
        raise ValueError("Screen is not initialized")
    # get center of the screen
    center = screen.get_rect().center
    font = pygame.font.Font("freesansbold.ttf", font_size)
    text = font.render(text, True, color)
    screen.blit(text, (center[0] - text.get_width()/2, center[1] - text.get_height()/2))
    pygame.display.update()


def path_to_stimulus(part, type, id):
    """
    Filename is in a stimuli/congturent_incongruent folder named
    <part>_<id>_<type>.wav where id is id with 0 padding on the left to 2 digits, part is 
    either q for question or a for answer, and type is either initial or final
    """
    return os.path.join(os.getcwd(), 'stimuli', 'congruent_incongruent', f'{part}_{str(id).zfill(2)}_{type}.wav')


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
