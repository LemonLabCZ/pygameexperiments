import pygame


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


def wait_for_answer(screen):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return event.key
