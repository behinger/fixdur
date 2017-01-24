#!/usr/bin/env python
#
# Copyright (c) 1996-2011, SR Research Ltd., All Rights Reserved
#
#
# For use by SR Research licencees only. Redistribution and use in source
# and binary forms, with or without modification, are NOT permitted.
#
#
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Date: 2011/04/13 18:48:21 $
# 
#


import pylink

import ctypes
import math
import sys
import array

from psychopy import visual, misc

from OpenGL.GL import *
from OpenGL.GLU import *
#from pyglet.gl import *

import Image

from pygame import *
import pygame.mixer
import pygame.event
from pygame.constants import *

import numpy as np    

class EyeLinkCoreGraphicsOpenGL(pylink.EyeLinkCustomDisplay):
	def __init__(self,window):
		self.window=window
		self.keys = []
				
		if sys.byteorder == 'little':
			self.byteorder = 1
		else:
			self.byteorder = 0
		
		pylink.EyeLinkCustomDisplay.__init__(self)
		
		self.__target_beep__ = None
		self.__target_beep__done__ = None
		self.__target_beep__error__ = None
	
		self.imagebuffer = array.array('I')
		self.pal = None	
		
		self.width, self.height =window.size
			
		self.pos = []
		self.state = 0
                self.inner = visual.PatchStim(window, tex = None, mask = 'circle',
                    units = 'pix', size = 5, color = window.color)
                self.outer =  visual.PatchStim(window, tex = None, mask = 'circle',
                    units = 'pix', size = 20, color = [128,128,128])
                self.image_patch = visual.PatchStim(window)
                self.label = None

        def _draw_fix_mark(self, pos):
                self.outer.setPos(pos)
                self.inner.setPos(pos)
                self.outer.draw()
                self.inner.draw()

	def setup_cal_display (self):
		self.window.flip()
				
	def exit_cal_display(self): 
		self.clear_cal_display()
		
	def record_abort_hide(self):
		pass

	def clear_cal_display(self): 
		self.window.flip()


	def erase_cal_target(self):
		self.window.flip()
		
	def draw_cal_target(self, x, y):
                x = x - self.width/2
                y = y - self.height/2
                self._draw_fix_mark((x,y)) 
                self.window.flip()
 
	def play_beep(self,beepid):
		''' Play a sound during calibration/drift correct.'''
                pass
 
        def translate_key_message(self,event):
		if event.type == KEYDOWN:
			if event.key == K_F1:  
				key = pylink.F1_KEY;
			elif event.key == K_F2:  
				key = pylink.F2_KEY;
			elif event.key == K_F3:  
				key = pylink.F3_KEY;
			elif event.key == K_F4:  
				key = pylink.F4_KEY;
			elif event.key == K_F5:  
				key = pylink.F5_KEY;
			elif event.key == K_F6:  
				key = pylink.F6_KEY;
			elif event.key == K_F7:  
				key = pylink.F7_KEY;
			elif event.key == K_8:  
				key = pylink.F8_KEY;
			elif event.key == K_F9:  
				key = pylink.F9_KEY;
			elif event.key == K_F10:  
				key = pylink.F10_KEY;
			elif event.key == K_PAGEUP:  
				key = pylink.PAGE_UP;
			elif event.key == K_PAGEDOWN:  
				key = pylink.PAGE_DOWN;
			elif event.key == K_UP:  
				key = pylink.CURS_UP;
			elif event.key == K_DOWN:  
				key = pylink.CURS_DOWN;
			elif event.key == K_LEFT:  
				key = pylink.CURS_LEFT;
			elif event.key == K_RIGHT:  
				key = pylink.CURS_RIGHT;
			elif event.key == K_BACKSPACE:  
				key = '\b';
			elif event.key == K_RETURN:  
				key = pylink.ENTER_KEY;
			#elif event.key == K_ESCAPE:  
			#	key = pylink.ESC_KEY;
			elif event.key == K_TAB:  
				key = '\t';			
			else:
 				key = event.key;

			if key == pylink.JUNK_KEY:
				return 0
                        return key	
		return 0

        def get_input_key(self):
		ky=[]
		for key in pygame.event.get([KEYDOWN]):
			try:
				tkey = self.translate_key_message(key)
				ky.append(pylink.KeyInput(tkey,key.mod))
			except Exception, err:
				print err
		return ky
	
	def get_mouse_state(self):
		pos = pygame.mouse.get_pos()
		state = pygame.mouse.get_pressed()
		return (pos,state[0])	

	def exit_image_display(self):
		#self.window.draw()
		self.window.flip()
		
	def alert_printf(self,msg): 
            print msg 
	
	def setup_image_display(self, width, height):
		self.img_size = (width,height)
		#self.window.draw()
		
	def image_title(self, text): 
		self.label = text
			    	

	def draw_image_line(self, width, line, totlines,buff):
		i =0
		while i <width:
			if buff[i]>=len(self.pal): 
				buff[i]=len(self.pal)-1							
			self.imagebuffer.append(self.pal[buff[i]&0x000000FF])  
			i = i+1
		if line == totlines:
                        padded_size =  (2**(np.ceil(np.log2(max(self.img_size)))),
                                       2**(np.ceil(np.log2(max(self.img_size)))),4)
                        resize_factor = float(padded_size[0])/max(self.img_size)  
                        img = Image.new("RGBX", self.img_size)	
                        img.fromstring(self.imagebuffer.tostring())
                        img = img.resize((img.size[0]*resize_factor, 
                                          img.size[1]*resize_factor))  
                        img = np.array(img)
                        pad_img = np.zeros(padded_size)
                        pad_img[:img.shape[0],:img.shape[1],:] = img
                        self.image_patch.setTex(pad_img)
                        self.image_patch.draw()
                        self.window.flip()
                        self.imagebuffer = array.array('I')
 
	def draw_line(self,x1,y1,x2,y2,colorindex):
		if colorindex   ==  pylink.CR_HAIR_COLOR:          color = (1.0,1.0,1.0,1.0)
		elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       color = (1.0,1.0,1.0,1.0)
		elif colorindex ==  pylink.PUPIL_BOX_COLOR:        color = (0.0,1.0,0.0,1.0)
		elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: color = (1.0,0.0,0.0,1.0)
		elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     color = (1.0,0.0,0.0,1.0)
		else: color =(0.0,0.0,0.0,0.0)
		
		#asp = ((float)(self.size[1]))/((float)(self.size[0]))
		asp = 1
		r = (float)(self.width*0.5-self.width*0.5*0.75)
		l = (float)(self.width*0.5+self.width*0.5*0.75)
		t = (float)(self.height*0.5+self.height*0.5*asp*0.75)
		b = (float)(self.height*0.5-self.height*0.5*asp*0.75)
				
		x11= float(float(x1)*(l-r)/float(self.img_size[0]) + r)		
		x22= float(float(x2)*(l-r)/float(self.img_size[0]) + r)	
		y11= float(float(y1)*(b-t)/float(self.img_size[1]) + t)	
		y22= float(float(y2)*(b-t)/float(self.img_size[1]) + t)	

		glBegin(GL_LINES)
		glColor4f(color[0],color[1],color[2],color[3] )
		glVertex2f(x11,y11)
		glVertex2f(x22,y22)
		glEnd()
		
	def draw_lozenge(self,x,y,width,height,colorindex):
		if colorindex   ==  pylink.CR_HAIR_COLOR:          color = (1.0,1.0,1.0,1.0)
		elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       color = (1.0,1.0,1.0,1.0)
		elif colorindex ==  pylink.PUPIL_BOX_COLOR:        color = (0.0,1.0,0.0,1.0)
		elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: color = (1.0,0.0,0.0,1.0)
		elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     color = (1.0,0.0,0.0,1.0)
		else: color =(0.0,0.0,0.0,0.0)
		
		width=int((float(width)/float(self.img_size[0]))*self.img_size[0])
		height=int((float(height)/float(self.img_size[1]))*self.img_size[1])

		#asp = ((float)(self.size[1]))/((float)(self.size[0]))
		asp = 1
		r = (float)(self.width*0.5-self.width*0.5*0.75)
		l = (float)(self.width*0.5+self.width*0.5*0.75)
		t = (float)(self.height*0.5+self.height*0.5*asp*0.75)
		b = (float)(self.height*0.5-self.height*0.5*asp*0.75)

		x11= float(float(x)*(l-r)/float(self.img_size[0]) + r)		
		x22= float(float(x+width)*(l-r)/float(self.img_size[0]) + r)	
		y11= float(float(y)*(b-t)/float(self.img_size[1]) + t)	
		y22= float(float(y+height)*(b-t)/float(self.img_size[1]) + t)	

		r=x11
		l=x22
		b=y11
		t=y22
	
		glColor4f(color[0],color[1],color[2],color[3])
			
		xw = math.fabs(float(l-r))
		yw = math.fabs(float(b-t))
		sh = min(xw,yw)
		rad = float(sh*0.5)
		
		x = float(min(l,r)+rad)
		y = float(min(t,b)+rad)
		
		if xw==sh:        
			st = 180
		else:
			st = 90	
		glBegin(GL_LINE_LOOP)
		i=st
		degInRad = (float)(float(i)*(3.14159/180.0))
		
		for i in range (st, st+180):		
			degInRad = (float)(float(i)*(3.14159/180.0))
			glVertex2f((float)(float(x)+math.cos(degInRad)*rad),float(y)+(float)(math.sin(degInRad)*rad))
					
		if xw == sh:    #short horizontally
			y = (float)(max(t,b)-rad)
		else:  		  # short vertically
			x = (float)(max(l,r)-rad)

		i = st+180			
   		for i in range (st+180, st+360): 		
			degInRad = (float)(float(i)*(3.14159/180.0))
			glVertex2f((float)(float(x)+math.cos(degInRad)*rad),float(y)+(float)(math.sin(degInRad)*rad))
			
		glEnd()
				

	def set_image_palette(self, r,g,b):
		self.imagebuffer = array.array('I')
		self.clear_cal_display()
		sz = len(r)
		i =0
		self.pal = []
		while i < sz:
			rf = int(r[i])
			gf = int(g[i])
			bf = int(b[i])
			if self.byteorder:
				self.pal.append(0xff<<24|(bf<<16)|(gf<<8)|(rf))
			else:
				self.pal.append((rf<<24)|(gf<<16)|(bf<<8)|0xff)
			i = i+1
