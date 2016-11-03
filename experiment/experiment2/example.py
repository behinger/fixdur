# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 17:48:35 2016

@author: experiment
"""
import pylink as pl

def eyeTrkInit (sp):
        el = pl.EyeLink()
        el.sendCommand("screen_pixel_coords = 0 0 %d %d" %sp)
        el.sendMessage("DISPLAY_COORDS  0 0 %d %d" %sp)
        el.sendCommand("select_parser_configuration 0")
        el.sendCommand("scene_camera_gazemap = NO")
        el.sendCommand("pupil_size_diameter = %s"%("YES"))
        return(el)

def eyeTrkCalib (el,sp,cd=32):
     pl.openGraphics(sp,cd)
     pl.setCalibrationColors((255,255,255),(0,0,0))
     pl.setTargetSize(int(sp[0]/70), int(sp[1]/300)) 
     pl.setCalibrationSounds("","","")
     pl.setDriftCorrectSounds("","off","off")
     el.doTrackerSetup()
     pl.closeGraphics()
     #el.setOfflineMode()
     
el = eyeTrkInit((1920,1080))
eyeTrkCalib(el,(1920,1080))

#http://stackoverflow.com/questions/35071433/psychopy-and-pylink-example