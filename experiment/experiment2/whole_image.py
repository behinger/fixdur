# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:37:14 2016

@author: jschepers
"""
import numpy as np
from PIL import Image
from psychopy import visual
import tools
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import ImageDraw


path_to_fixdur_files, path_to_fixdur_code = tools.paths()

rectXY = (1920,1080);
surf = visual.Window(size=rectXY,fullscr=False,winType = 'pyglet', screen=1, units='pix')

# set parameters for gaussian
bubble_size = 1.1774
size = round(tools.deg_2_px(bubble_size))*3
fwhm = round(tools.deg_2_px(bubble_size))
center = None

x = np.arange(0, size, 1, float)
y = x[:,np.newaxis]
    
if center is None:
   x0 = y0 = size // 2
else:
   x0 = center[0]
   y0 = center[1]
    
gaussian = np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)
#gaussian = gaussian * 255
gaussian = -(gaussian*2-1)


#imgplot = plt.imshow(gaussian)

#mask_im = Image.new('RGB', (1280,960), 'red')
#mask_im = visual.Circle(surf, units='pix', radius=100)

mask_im = np.ones((1080,1920))
#mask_im = np.ones((960,1280))
#mask_im[380:560,550:730] = gaussian
mask_im[450:630,870:1050] = gaussian
#imgplot = plt.imshow(mask_im)


original = Image.open(path_to_fixdur_files+'stimuli/natural/image_5.bmp')
#original = original.resize((1920,1080))


imgplot = plt.imshow(mask_im)

# Source: https://opensource.com/life/15/2/resize-images-python
basewidth = 1920
wpercent = (basewidth / float(original.size[0]))
hsize = int((float(original.size[1]) * float(wpercent)))
#original = original.resize((basewidth, hsize), Image.ANTIALIAS)
black_white = original.convert('L')
# imgplot = plt.imshow(original)


original_im = visual.ImageStim(surf, image=black_white, mask=mask_im, units='pix')
#original_im = visual.ImageStim(surf, image=path_to_fixdur_files+'stimuli/natural/image_5.bmp', mask=-gaussian)
#grating = visual.GratingStim(win=surf, mask='circle', size=300, pos=[-4,0], sf=3)

#grating.draw()
#background = Image.new("RGB", (1280, 960), "gray")
#black_white = original_im.convert('L')
original_im.draw()
surf.flip()



