from psychopy import visual, core, event, monitors,logging
import pygame, sys, os, random, math, string, glob, pdb
import pylink
import numpy as np
import cPickle as pickle
import fixdur_tracker as tracker
import trial, tools
from collections import deque
from pygame.locals import *
import time

pygame.quit()
pygame.init()
pyg =0
rectXY = (1920,1080);
#flags = pygame.FULLSCREEN |  pygame.RLEACCEL | pygame.HWSURFACE | pygame.DOUBLEBUF 
flags = pygame.RLEACCEL | pygame.HWSURFACE | pygame.DOUBLEBUF
if pyg:
    surf =pygame.display.set_mode(rectXY, flags, 0)
    rect = [pygame.Rect(100,100,154,154),pygame.Rect(100,300,154,154),pygame.Rect(100,500,154,154),pygame.Rect(300,100,154,154),pygame.Rect(300,300,154,154),pygame.Rect(300,500,154,154), pygame.Rect(600,100,154,154),pygame.Rect(600,300,154,154),pygame.Rect(600,500,154,154),pygame.Rect(800,100,154,154),pygame.Rect(800,300,154,154),pygame.Rect(800,500,154,154)]
else:
    rectXY = (1920,1080);
    surf = visual.Window(size=rectXY,fullscr=False,winType = 'none',waitBlanking=False)
    rect = [visual.Rect(surf,300,200,pos=[-100,200])]
#surf = pygame.display.set_mode(rectXY, 0, 32)
a = pygame.display.Info()
path_to_fixdur_files, path_to_fixdur_code = tools.paths()
#fix_cross = pygame.image.load(path_to_fixdur_code+'images/fixationcross.png').convert()


print a
for k in range(10000):

    if pyg:
        surf.fill((random.randint(0,255),128,128))
    
        #surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        start = time.time()
        pygame.display.update(rect)
        #pygame.display.update((rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        print (time.time() - start)*1000
        pygame.time.delay(20)
    
        #pygame.time.delay(20)    
    else:
        #rect[0].setFillColor( (random.randint(0,255),128,128), 'rgb255')
        

        rect[0].draw()
        start = time.time()
        surf.flip()
        print (time.time() - start)*1000

        #pygame.time.delay(20)

pygame.quit()
