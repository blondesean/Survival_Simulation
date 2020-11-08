import pygame as pg
import sys
import os
import math
import numpy as np
import random 
from pygame.math import Vector2

#Dimensions of window
display_width = 300
display_height = 300

#Sizing information
tile_size = 25
animal_size = 10

gameDisplay = pg.display.set_mode((display_width,display_height))

#Volume of creatures
N = 100
foxFreq = .01
rabbitFreq = .99
FPS = 60

#Simple grab random integer or probability 1 / given integer
def randInt(range, prob = False):
    verbose("Range was " + str(range), False)
    range = math.ceil(range)
    verbose("Range is " + str(range), False)
    if range < 1:
        p = 0
        verbose("0 Probability Given", False)
    elif prob:
        p = 1.0 * random.randint(1,range) / range
        verbose("Random Probability = " + str(p), False) 
    elif range != 0:
        p = random.randint(1,range)
        verbose("Random Value = " + str(p), False)
    else:
        p = 1
        verbose("Random Value = " + str(p), False)
    return p

#convenient switch for debut text
def verbose(printMe,loudOption = False):
    if loudOption:
        print(printMe)
