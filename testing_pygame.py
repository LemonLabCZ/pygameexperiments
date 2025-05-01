import pygame
import sys
import src.utils as utils

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

def game_loop():
    running = True
    while running:
      check_events()
      update()
      draw()

def check_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # pass this event to the main loop in while running
            # retur lambda to be evaluated in the main loop
            game_quit()

def game_quit():
    sys.exit()


def update():
    check_for_key_press()


def check_for_key_press():
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        pygame.event.post(pygame.event.Event(pygame.QUIT))


def draw():
    utils.show_text(screen, "Press SPACE to quit", 50, (255, 255, 255))

game_loop()

