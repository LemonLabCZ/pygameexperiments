"""
LAnguage Specific Assessment of emotional words (LASA)
A collaboration project between
(1) Chez Academy of Science, Psychological Institute
(2) Heidelberg University Language and Cognition Lab (HULC)
(3) Core Facility for Neuroscience of Self-Regulation (CNSR)

Coded by 
(C) Torsten Wüstenberg 2023
torsten.wuestenberg@psychologie.uni-heidelberg.de
Core Facility for Neuroscience of Self-Regulation (CNSR)
1st Version 0.9 2023-03-03
Final Version 1.0 2023-03-13
"""

# import neccessary python libraries
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pygame
from pygame.locals import *
import numpy as np
from datetime import datetime
import pandas as pd
import tkinter as tk
from tkinter import simpledialog
import os

# =======================================================================
# initialize pygame and experimental window =============================
def initScreen(screenSize, screenColor):
    # input variables:
    # screenSize: screen size tuple: (width, height)
    # screenColor: screen color tuple: (R,G,B)
    screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
    pygame.display.set_caption('LASA')
    screen.fill(screenColor)
    pygame.display.update()
    return screen

# =======================================================================           
# input window for subject ID
def getSID(conf):
    # input variable
    # configuration dict
    sid = ''
    ROOT = tk.Tk()
    ROOT.withdraw()
    return sid, (ROOT.winfo_screenwidth(),ROOT.winfo_screenheight())

################################################################
# read in configuration File and print parameters .... and write it's content to dictionary
configFile = pd.read_excel(os.path.join("settings", "LASAparameters.xlsx"))
config = {}
print('\n\n-------------------------------------------------------------\n')
print(f'Experimental setup:')
for ii in range(len(configFile)):
    config[configFile["parameter"][ii]] = configFile["value"][ii]
    print(f'{configFile["parameter"][ii].ljust(12)}:{configFile["value"][ii]}')
print('-------------------------------------------------------------\n')

# read in stimulus list
def load_stimuli(file_name):
    pth = os.path.join("settings", file_name)
    print(f'Loading settings from {pth}')
    out = pd.read_excel(pth)
    print(f'# trial stimuli: {len(out)}')
    return out

trialList = load_stimuli(config["trialList"])
stimList = load_stimuli(config["stimList"])
print('-------------------------------------------------------------\n')

# set SID
sid, screenSize = getSID(config)
print(screenSize)
screenCenter = (round(screenSize[0]/2),round(screenSize[1]/2))
screenColor = (0,0,0)
startTime = datetime.now()

# initialize screen and audio line
print('Initializing components.')
screen = initScreen(screenSize, screenColor)
pygame.mixer.init()
pygame.font.init()          
print('Done!\n')
print('-------------------------------------------------------------\n')   

#for ii in range(len(order)):
for ii in range(len(stimList)):
    # say word and log onseg
    word = stimList[config['language'] + '_word'][ii]
    sound2play = pygame.mixer.Sound(os.path.join(os.getcwd(), 'stimuli', 'soundStimuli', config['language'], word) + '.wav')
    wordStart = datetime.now()
    pygame.mixer.Sound.play(sound2play)
    pygame.time.wait(5000)
    pygame.mixer.Sound.stop(sound2play)