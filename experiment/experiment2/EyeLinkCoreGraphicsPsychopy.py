# -*- coding: utf-8 -*-# Copyright (C) 2011 Jason Locklin# Copyright (C) 2016 Zhiguo Wang# This piece of code was based on "eyeTracker.py" originally developted by# Jason Locklin and released under the GNU General Public License (GPL).# To my understanding, "eyeTracker.py" was based on "EyelinkCoreGraphicPygame.py"# that comes with "pylink".# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE, DATA, OR# PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.# Redistributions in binary form must reproduce the above copyright# notice, this list of conditions and the following disclaimer in# the documentation and/or other materials provided with the distribution.from psychopy import visual, monitors, event, core, soundfrom numpy import linspacefrom math import sin, cos, piimport array, string, Image, pylinkclass EyeLinkCoreGraphicsPsychopy(pylink.EyeLinkCustomDisplay):    def __init__(self, tracker, win):#        '''Initialize a Custom EyeLinkCoreGraphics for         tracker: the TRACKER()         display: the Psychopy display             '''        pylink.EyeLinkCustomDisplay.__init__(self)        self.display = win        self.mouse = event.Mouse(visible=True)        #self.__target_beep__ = sound.Sound('type.wav')        #self.__target_beep__done__ = sound.Sound('qbeep.wav')        #self.__target_beep__error__ = sound.Sound('error.wav')        self.imagebuffer = array.array('l')        self.pal = None	        self.size = (384, 320)        self.bg_color = [0, 0, 0]        self.sizeX = win.size[0]        self.sizeY = win.size[1]        self.setTracker(tracker)        self.display.mouseVisible = False        self.ms = event.Mouse(visible=False)        self.last_mouse_state = -1        # image title        self.title = visual.TextStim(self.display,'')        # lines        self.line = visual.Line(self.display, start=(0, 0), end=(0,0),                           lineWidth=2.0, lineColor=[0,0,0])            def setTracker(self, tracker):        self.tracker = tracker        self.tracker_version = tracker.getTrackerVersion()        if(self.tracker_version >=3):            self.tracker.sendCommand("enable_search_limits=YES")            self.tracker.sendCommand("track_search_limits=YES")            self.tracker.sendCommand("autothreshold_click=YES")            self.tracker.sendCommand("autothreshold_repeat=YES")            self.tracker.sendCommand("enable_camera_position_detect=YES")     def setup_cal_display(self):#        '''This function is called just before entering calibration or validation modes'''        self.display.color = self.bg_color        self.title.autoDraw = False        self.display.flip()    def clear_cal_display(self):#        '''Clear the calibration display'''        self.display.color = self.bg_color            def exit_cal_display(self):#        '''This function is called just before exiting calibration/validation mode'''        self.clear_cal_display()    def record_abort_hide(self):#        '''This function is called if aborted'''        pass    def erase_cal_target(self):#        '''Erase the calibration or validation target drawn by previous call to draw_cal_target()'''        self.display.color = self.bg_color        self.display.flip()    def draw_cal_target(self, x, y):#        '''Draw calibration/validation target'''        #print x, y, self.sizeX, self.sizeY        cal_target_out = visual.GratingStim(self.display, tex='none', mask='circle',                                            size=25.0/2000*self.sizeX, color=[1.0,1.0,1.0])        cal_target_in = visual.GratingStim(self.display, tex='none', mask='circle',                                           size=25.0/4000*self.sizeX, color=[-1.0,-1.0,-1.0])        cal_target_out.setPos((x - 0.5*self.sizeX, 0.5*self.sizeY - y))        cal_target_in.setPos((x - 0.5*self.sizeX, 0.5*self.sizeY - y))        cal_target_out.draw()        cal_target_in.draw()        self.display.flip()    def play_beep(self, beepid):#        ''' Play a sound during calibration/drift correct.'''        pass        #if beepid == pylink.CAL_TARG_BEEP or beepid == pylink.DC_TARG_BEEP:        #    self.__target_beep__.play()        #if beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:        #    self.__target_beep__error__.play()        #if beepid in [pylink.CAL_GOOD_BEEP, pylink.DC_GOOD_BEEP]:        #    self.__target_beep__done__.play()    def getColorFromIndex(self, colorindex):         '''Return psychopy colors for varius objects'''         if colorindex    ==  pylink.CR_HAIR_COLOR:                  return (1, 1, 1)         elif colorindex ==  pylink.PUPIL_HAIR_COLOR:              return (1, 1, 1)         elif colorindex ==  pylink.PUPIL_BOX_COLOR:               return (-1, 1, -1)         elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (1, -1, -1)         elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (1, -1, -1)         else:                                                                            return (0,0,0)    def draw_line(self, x1, y1, x2, y2, colorindex):        '''Draw a line to the display screen. This is used for drawing crosshairs'''        color = self.getColorFromIndex(colorindex)        self.line.start       = (x1 - self.size[0]*0.5, self.size[1]*0.5-y1)        self.line.end        = (x2 - self.size[0]*0.5, self.size[1]*0.5-y2)        self.line.lineColor = color        self.line.draw()    def draw_lozenge(self, x, y, width, height, colorindex):        '''Draw the cross hair at (x,y) '''        color = self.getColorFromIndex(colorindex)        x1 = x - self.size[0]*0.5 + width/2.0        y1 = self.size[1]*0.5- y - height/2.0                Xs = [width/2.0*cos(t) + x1 for t in linspace(0, 2*pi, 72)]        Ys = [height/2.0*sin(t) + y1 for t in linspace(0, 2*pi, 72)]        lozenge = visual.ShapeStim(self.display, vertices = zip(Xs, Ys),                                   lineWidth=2.0, lineColor=color)        lozenge.draw()    def get_mouse_state(self):#        '''Get the current mouse position and status'''        pos = self.mouse.getPos()        pos = (self.sizeX/2 + pos[0], self.sizeY/2 - pos[1])        state = self.mouse.getPressed()[0]        return (pos, state)    #the newest function of getting key fron jiye    def get_input_key(self):        ky=[]        for keycode in event.getKeys():            k= pylink.JUNK_KEY            if keycode   == 'f1': k = pylink.F1_KEY            elif keycode == 'f2': k = pylink.F2_KEY            elif keycode == 'f3': k = pylink.F3_KEY            elif keycode == 'f4': k = pylink.F4_KEY            elif keycode == 'f5': k = pylink.F5_KEY            elif keycode == 'f6': k = pylink.F6_KEY            elif keycode == 'f7': k = pylink.F7_KEY            elif keycode == 'f8': k = pylink.F8_KEY            elif keycode == 'f9': k = pylink.F9_KEY            elif keycode == 'f10': k = pylink.F10_KEY            elif keycode == 'pageup': k = pylink.PAGE_UP            elif keycode == 'pagedown': k = pylink.PAGE_DOWN            elif keycode == 'up': k = pylink.CURS_UP            elif keycode == 'down': k = pylink.CURS_DOWN            elif keycode == 'left': k = pylink.CURS_LEFT            elif keycode == 'right': k = pylink.CURS_RIGHT            elif keycode == 'backspace': k = ord('\b')            elif keycode == 'return': k = pylink.ENTER_KEY            elif keycode == 'space': k = ord(' ')            elif keycode == 'escape': k = pylink.ESC_KEY            elif keycode == 'tab': k = ord('\t')            elif keycode in string.ascii_letters: k = ord(keycode)            elif k== pylink.JUNK_KEY: key = 0            # getKeys does not retrun key modifiers, this workaround doe not work            if keycode in ['lshift', 'rshift']: mod = 1            else: mod = 0                        ky.append(pylink.KeyInput(k, mod))        return ky    def exit_image_display(self):#        '''Called to end camera display'''        self.clear_cal_display()        self.display.flip()    def alert_printf(self,msg):#        '''Print error messages.'''        print "alert_printf"    def setup_image_display(self, width, height): # 384 x 320 pixels        self.size = (width,height)        self.clear_cal_display()        self.title.autoDraw = True        self.last_mouse_state = -1    def image_title(self, text):#        '''Draw title text at the top of the screen for camera setup'''        self.clear_cal_display()        title_pos = (0, 0-self.size[0]/2-20)        self.title.pos = title_pos        self.title.text = text    def draw_image_line(self, width, line, totlines, buff):#        '''Display image given pixel by pixel'''        i =0        while i <width:            self.imagebuffer.append(self.pal[buff[i]])            i= i+1        if line == totlines:            if totlines == 160:                imgsz = (self.size[0]/2,self.size[1]/2)            else:                imgsz = (self.size[0],self.size[1])            bufferv = self.imagebuffer.tostring()            img =Image.fromstring("RGBX", imgsz, bufferv)            img = img.resize(self.size)                                        img = visual.ImageStim(self.display, image=img)            img.draw()            self.draw_cross_hair()            self.display.flip()            self.imagebuffer = array.array('l')                def set_image_palette(self, r,g,b): #        '''Given a set of RGB colors, create a list of 24bit numbers representing the pallet.        I.e., RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111'''        self.imagebuffer = array.array('l')        self.clear_cal_display()        sz = len(r)        i =0        self.pal = []        while i < sz:            rf = int(b[i])            gf = int(g[i])            bf = int(r[i])            self.pal.append((rf<<16) | (gf<<8) | (bf))            i = i+1