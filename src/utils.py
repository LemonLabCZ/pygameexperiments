import pygame
import tkinter as tk
from tkinter import simpledialog

def initScreen(screenSize, screenColor):
    # input variables:
    # screenSize: screen size tuple: (width, height)
    # screenColor: screen color tuple: (R,G,B)
    screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
    pygame.display.set_caption('')
    screen.fill(screenColor)
    pygame.display.update()
    return screen


def getScreenSize():
    sid = ''
    ROOT = tk.Tk()
    ROOT.withdraw()
    return (ROOT.winfo_screenwidth(),ROOT.winfo_screenheight())