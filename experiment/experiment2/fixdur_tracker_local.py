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
import array
import Image
from pygame.constants import *
import os.path
import sys
from psychopy import visual

class EyeLinkError(Exception): pass




class Tracker(EyeLink):
    """
    Encapsultes calls to the Eyelink II Host
    """
    def __init__(self, display, filename="TEST.EDF"):
        import numpy as np
        EyeLink.__init__(self)
        self._disp = display
        self._filename = filename
        self.openDataFile(filename)

        self._surfs = np.append(display.pos,display.size);#[0,0,1920,1080]#self._disp.get_rect()
        pylink.flushGetkeyQueue()
        
        col = 128
        print "1"
        pylink.setCalibrationColors((0, 0, 0), (col, col, col)) #Sets the calibration target and background color
        print int(self._surfs[3]/300)
#        pylink.setTargetSize(int(self._surfs[2]/70), int(self._surfs[3]/300)) #select best size for calibration target
        print "12"
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")

        self.sendCommand("screen_pixel_coords =  0 0 %d %d" % (self._surfs[2], self._surfs[3]))
        self.sendMessage("DISPLAY_COORDS  0 0 %d %d" % (self._surfs[2], self._surfs[3]))
        
        #self.sendMessage("heuristic_filter" % (self._surfs[2], self._surfs[3]))
        #assert self.getTrackerVersion() == 2
        self.sendCommand("select_parser_configuration 0")
        self.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
        self.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")
        self.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON")
        self.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS")
        print "2"
        self.sendCommand("button_function 5 'accept_target_fixation'")

    def set_calibration(self, points):
        self.sendCommand('calibration_type=HV%s' % (points)) 

    def setup(self):
        pylink.openGraphics((self._surfs[2]+1680,self._surfs[3]),32)
        self.doTrackerSetup()
        pylink.closeGraphics()

    def recording(self):
        return self.isRecording() == 0

    def sendMessage(self, arg):
        EyeLink.sendMessage(self, arg)

    def drift(self, x=None, y=None):
        """
        Start Drift Correction
        """
        if x is None:
            x = self._surfs[2]/2
        if y is None:
            y = self._surfs[3]/2
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
