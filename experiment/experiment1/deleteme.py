# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 16:36:49 2015

@author: tracking
"""

import pygame, sys, os, random, math, string, glob, pdb
import pylink
import numpy as np
import cPickle as pickle
import fixdur_tracker as tracker
import trial, tools
from collections import deque
from pygame.locals import *

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()
for k in range(10):
    trial_mat = tools.randomization('test',6000)