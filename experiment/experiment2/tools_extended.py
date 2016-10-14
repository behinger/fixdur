# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:37:14 2016

@author: jschepers
"""
import numpy as np
from PIL import Image
from psychopy import visual
import tools
import matplotlib.pyplot as plt
import re
import sys
from scipy import spatial

path_to_fixdur_files, path_to_fixdur_code = tools.paths()

# import code for poisson sampling
sys.path.append(path_to_fixdur_code+'poisson_disk_python/src')
import poisson_disk
#from enhanced_grid import *

#define patterns for pattern matching
p_noise = re.compile('noise')
#p_urban = re.compile('image')

# set parameters for gaussian
bubble_size = 1.1774
size = round(tools.deg_2_px(bubble_size))*3
fwhm = round(tools.deg_2_px(bubble_size))

#rectXY = (1920,1080)
#surf = visual.Window(size=rectXY,fullscr=False,winType = 'pyglet', screen=1, units='pix')


def whole_image(surf,bubble_image,chosen_bubble):
    
    # find out if the current image is a noise or an urban image
    #Fehlerbehandlung hinzufügen?
    if p_noise.match(bubble_image) != None:
        image = Image.open(path_to_fixdur_files+'stimuli/noise/post_shine/'+bubble_image)
    else:
        image = Image.open(path_to_fixdur_files+'stimuli/urban/'+bubble_image)
        # convert image to grayscale
        image = image.convert('L')
    
    gaussian = makeGaussian()
    
     # embed gaussian in matrix which has the same size as the window
    mask_im = np.ones((1080,1920))
    mask_im[int(x-size/2):int(x+size/2),int(y-size/2):int(y+size/2)] = gaussian
    #mask_im[450:630,870:1050] = gaussian
    
    stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
    stim.draw()
    surf.flip()


''' copied and modified from Lili's generate_stimuli file'''

def makeGaussian():
    """ Create a mask stimulus with square gaussian kernel.
 
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """

    x = np.arange(0, size, 1, float)
    y = x[:,np.newaxis]
    
    #if center is None:
    x0 = y0 = size // 2
    #else:
    #    x0 = center[0]
    #    y0 = center[1]
    
    gaussian = np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)
    
    # translate entries between 0 and 1 to values between -1 (only background)
    # and 1 (only image)
    gaussian = -(gaussian*2-1)
    
    return gaussian

def poisson_sampling(width, height):
    
    # substract margin to make sure there is enough space for bubbles    
    width = width - size
    height = height - size
    
    p = poisson_disk.sample_poisson_uniform(width, height, 77, 30)
    #sample_points = np.empty((len(p),2))
    sample_points = []
    for i in range(len(p)):
        # add 1/2 size to get empty margin ??
        sample_points.append((int(p[i][0]),int(p[i][1])))
        #sample_points[i][0] = int(p[i][0])
        #sample_points[i][1] = int(p[i][1])
    return sample_points
 
   
def create_mask(surf,image, location):
    #mon_res = surf.size
    
    # create gaussian kernel which is the same for all bubbles
    gaussian = makeGaussian()
    
    # swap coordinates because mask matrix has different coordinate system
    x = location[0][1]
    y = location[0][0]
    
    # embed gaussian in matrix which has the same size as the window
    # possible error: could not broadcast input array from shape (180,180) into shape (180,0)
    mask_im = np.ones((1080,1920))
    mask_im[int(x-size/2):int(x+size/2),int(y-size/2):int(y+size/2)] = gaussian
    
    return mask_im
    
def choose_locations(num, sample_points, prev_loc):
    # compute number of sample points
    num_points = len(sample_points)
    #points_mat = np.empty((num_points,2))
    #points_mat[:][:] = sample_points[:]
    
    # compute euclidean distance between all sample points
    distances = np.empty((num_points,num_points))
    distances = spatial.distance.pdist(sample_points, 'euclidean')
    dist_mat = spatial.distance.squareform(distances)
    
    # minimal distance between center of 2 bubbles = diameter of bubble
    MIN_DIST = 154
    
    prev_ind = sample_points.index(prev_loc[0])
    #sample_points.remove(prev_loc[0])
    
    points_copy = sample_points
    #delete all bubbles that have overlap with chosen bubble from prev subtrial
    #remove_from_copy = [np.where(dist_mat[prev_ind,:] < MIN_DIST)]
    remove_from_copy = dist_mat[prev_ind,:] < MIN_DIST
    remove_from_copy = points_copy[remove_from_copy]
    points_copy.remove(remove_from_copy)
    return distances

#imgplot = plt.imshow(gaussian)

#mask_im = Image.new('RGB', (1280,960), 'red')
#mask_im = visual.Circle(surf, units='pix', radius=100)
#mask_im = np.ones((960,1280))
#mask_im[380:560,550:730] = gaussian
#imgplot = plt.imshow(mask_im)


#original = Image.open(path_to_fixdur_files+'stimuli/natural/image_5.bmp')
#original = original.resize((1920,1080))


#imgplot = plt.imshow(mask_im)

# Source: https://opensource.com/life/15/2/resize-images-python
#basewidth = 1920
#wpercent = (basewidth / float(original.size[0]))
#hsize = int((float(original.size[1]) * float(wpercent)))
#original = original.resize((basewidth, hsize), Image.ANTIALIAS)
#black_white = original.convert('L')
# imgplot = plt.imshow(original)


#original_im = visual.ImageStim(surf, image=black_white, mask=mask_im, units='pix')
#original_im = visual.ImageStim(surf, image=path_to_fixdur_files+'stimuli/natural/image_5.bmp', mask=-gaussian)
#grating = visual.GratingStim(win=surf, mask='circle', size=300, pos=[-4,0], sf=3)

#grating.draw()
#background = Image.new("RGB", (1280, 960), "gray")
#black_white = original_im.convert('L')
#original_im.draw()
#surf.flip()



