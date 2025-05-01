import pygame
import tkinter as tk
from tkinter import simpledialog

def getScreenSize(): 
    sid = '' 
    ROOT = tk.Tk() 
    ROOT.withdraw() 
    return (ROOT.winfo_screenwidth(),ROOT.winfo_screenheight())


def initScreen(screenSize, screenColor):
    # input variables:
    # screenSize: screen size tuple: (width, height)
    # screenColor: screen color tuple: (R,G,B)
    screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
    pygame.display.set_caption('')
    screen.fill(screenColor)
    pygame.display.update()
    return screen


def show_text(screen, text, font_size, color):
    if screen is None:
        raise ValueError("Screen is not initialized")
    screen_size = get_screen_size(screen)
    center = (screen_size[0] / 2, screen_size[1] / 2)
    font = pygame.font.Font("freesansbold.ttf", font_size)
    text = font.render(text, True, color)
    screen.blit(text, (center[0] - text.get_width()/2, center[1] - text.get_height()/2))
    return screen


def get_screen_size(screen: pygame.Surface):
    if screen is None:
        raise ValueError("Screen is not initialized")
    return (screen.get_width(), screen.get_height())


