import pygame
import sys
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
    # write a text in the middle of the screen
    font = pygame.font.Font("freesansbold.ttf", 40)
    text = font.render("Press space to quit", True, (255, 255, 255))
    screen.blit(text, (screen.get_width()/2 - text.get_width()/2, screen.get_height()/2 - text.get_height()/2))
    pygame.display.update()

game_loop()

