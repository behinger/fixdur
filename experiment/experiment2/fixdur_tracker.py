# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 17:07:09 2016
@author: experiment
"""

from pylink.eyelink import EyeLink
import pylink
import gc
import time
import pygame
import pygame.mixer
import pygame.event
import pygame.image
import pygame.draw
import pygame.mouse
from pygame.constants import *
import os.path
import sys
from psychopy import visual
import numpy as np
class EyeLinkError(Exception): pass
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
#from old_but_gold_EyeLinkCoreGraphicsPsychopy import EyeLinkCoreGraphicsPsychopy as EyeLinkCoreGraphicsPsychoPy




class Tracker(EyeLink):
    """
    Encapsultes calls to the Eyelink II Host
    """
    def __init__(self, surf, filename="TEST.EDF"):
        EyeLink.__init__(self)
        self._disp = surf
        self._filename = filename
        self.openDataFile(filename)

        #self._surfs = [0,0,1920,1080]#
        self._surfs = self._disp.size
        pylink.flushGetkeyQueue()
        
        genv = EyeLinkCoreGraphicsPsychoPy(self, surf)
        pylink.openGraphicsEx(genv)
        
        col = 128
        pylink.setCalibrationColors((0, 0, 0), (col, col, col)) #Sets the calibration target and background color
#        pylink.setTargetSize(int(self._surfs[2]/70), int(self._surfs[3]/300)) #select best size for calibration target
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")
        self.set_calibration()
        self.sendCommand("screen_pixel_coords =  0 0 %d %d" % (self._surfs[0], self._surfs[1]))
        self.sendMessage("DISPLAY_COORDS  0 0 %d %d" % (self._surfs[0], self._surfs[1]))
        self.sendCommand('screen_phys_coords = -266, 149, 266, -149')
        

        #self.sendMessage("heuristic_filter" % (self._surfs[2], self._surfs[3]))
        #assert self.getTrackerVersion() == 2
        self.sendCommand("select_parser_configuration 0")
        self.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        self.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
        self.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        self.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
        
        self.sendCommand("button_function 5 'accept_target_fixation'")

    def set_calibration(self, points=13):
        self.sendCommand('calibration_type=HV%s' % (points))
        #pylink.getEYELINK().sendCommand('calibration_type = HV13')
        #% left, left-middle, middle, middle right right
        scr_w = self._surfs[0]
        scr_h = self._surfs[1]
        l = scr_w/2 + (-2*scr_w/8);
        lm = scr_w/2 + (-1*scr_w/8);
        m = scr_w/2 + (0*scr_w/8);
        mr = scr_w/2 + (1*scr_w/8);
        r = scr_w/2 + (2*scr_w/8);
        #% % top, top-center, center, center-bottom, bottom
        t  =  scr_h/2 + (-2*scr_h/8);
        tc = scr_h/2 + (-1*scr_h/8);
        c  = scr_h/2 + (0*scr_h/8);
        cb = scr_h/2 + (1*scr_h/8);
        b  = scr_h/2 + (2*scr_h/8);
	
        # We use only 5 points.
        #calibTargets = 'calibration_targets  = %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, lm,tc, lm,cb, mr,tc, mr,cb);
        #validTargets = 'validation_targets   = %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, lm,tc, lm,cb, mr,tc, mr,cb);

        calibTargets = 'calibration_targets= %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, lm,tc, lm,cb, mr,tc, mr,cb)
        validTargets = 'validation_targets= %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, lm,tc, lm,cb, mr,tc, mr,cb)

        self.sendCommand(calibTargets)
        self.sendCommand(validTargets)

    def setup(self):
        self.doTrackerSetup()

    def recording(self):
        return self.isRecording() == 0

    def sendMessage(self, arg):
        EyeLink.sendMessage(self, arg)

    def drift(self, x=None, y=None):
        """
        Start Drift Correction
        """
        if x is None:
            x = self._surfs[0]/2
        if y is None:
            y = self._surfs[1]/2
        while 1:
            if not self.isConnected():
                raise EyeLinkError("Not connected")
            try:
                error = self.doDriftCorrect(x, y, 0, 1)
                if error == 27: 
                    self.doTrackerSetup()
                else:
                    break;
            except:
                break

    def metadata(self, key, value):
        """
        Send per-experiment Metadata
        """
        self.sendMessage("METAEX %s %s" % (key, value))
    
    def trialmetadata(self, key, value):
        """
        Send per-trial metadata
        """
        self.sendMessage("METATR %s %s" % (key, value))
    
    def trial(self, id, trial={}):
        """
        Announce a new trial with index 'id' and metadata 'trial'
        """
        self.sendMessage("TRIALID %r" % id)
        for k, v in trial.items():
            time.sleep(0.01)
            self.trialmetadata(k, v)
        self.sendCommand("record_status_message '%s'" % id)

    def start_trial(self):
        """
        Start recording eyetraces
        """
        error = self.startRecording(1,1,1,1)
        if error: raise EyeLinkError("Cannot start recording: %s"%error)

    def end_trial(self):
        """
        Stop recording eyetraces
        """
        time.sleep(0.01)
        self.stopRecording()

    def finish(self):
        """
        Finalize the experiment
        """
        self.setOfflineMode()
        pylink.msecDelay(500)
        self.closeDataFile()
        self.receiveDataFile(self._filename, self._filename)
        self.close()
