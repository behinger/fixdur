import pygame, sys, os, random
import numpy as np
import trial, tools
import pytrack_fixdur as pytrack

from pygame.locals import *

#path_to_bubble_images = '/../../../../../../net/store/nbp/fixdur/stimuli/single_bubble_images/'
path_to_bubble_images = '../stimuli/single_bubble_images/'
all_images = os.listdir(path_to_bubble_images)
#ratio of 1,2,3,4,5 bubbles displayed per image
num_of_bubbles_ratio = [[i] for i in [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,4,4,5]]
random.shuffle(num_of_bubbles_ratio)
pygame.init()

# set up the window
surf = pygame.display.set_mode((1280, 960), 0, 32)

#connection to eyetracker
track = pytrack.Tracker(surf, 'filename')
