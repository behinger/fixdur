import pygame
import fixdur_tracker as tracker
import pylink
pygame.init()

# set up the window
surf = pygame.display.set_mode((1280, 960), 0, 32)
pylink.openGraphics()
el = tracker.Tracker(surf,'test1.edf')
el.setup()

el.start_trial()

