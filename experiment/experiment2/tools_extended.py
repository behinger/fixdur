# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:37:14 2016

@author: jschepers
"""
import numpy as np
from PIL import Image
from psychopy import visual, event
import tools
import matplotlib.pyplot as plt
import re
import sys, os
from scipy import spatial, stats
import random

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


def whole_image(chosen_location):
 
    # swap coordinates because mask matrix has different coordinate system
    x = chosen_location[0][1]
    y = chosen_location[0][0] 

    # create gaussian kernel      
    gaussian = makeGaussian()   
    
    # embed gaussian in matrix which has the same size as the window
    mask_im = np.ones((1080,1920))
    mask_im[int(x-size/2):int(x+size/2),int(y-size/2):int(y+size/2)] = gaussian
    #mask_im[450:630,870:1050] = gaussian
    
    return mask_im


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

    sample_points = []
    for i in range(len(p)):
        # difference between screen size and image size/2
        diff_x = (1920-1280)/2
        diff_y = (1080-960)/2
        # adjust coordinates ((0,0) is upper left corner)
        x = int(p[i][0]) + diff_x + size/2
        y = int(p[i][1]) + diff_y + size/2
        sample_points.append((x,y))
        #sample_points[i][0] = int(p[i][0])
        #sample_points[i][1] = int(p[i][1])
    return sample_points
 
   
def create_mask(locations, mask_size=(1080,1920)):
    #mon_res = surf.size
    # number of bubbles needed
    num = len(locations)
    
    # create gaussian kernel which is the same for all bubbles
    gaussian = makeGaussian()
    mask_im = np.ones(mask_size)
    
    for i in np.arange(num):
        # swap coordinates because mask matrix has different coordinate system
        x = locations[i][1]
        y = locations[i][0]
    
        # embed gaussian in matrix which has the same size as the window
        # possible error: could not broadcast input array from shape (180,180) into shape (180,0)
        mask_im[int(x-size/2):int(x+size/2),int(y-size/2):int(y+size/2)] = gaussian
    # invert matrix to get background with bubbles
    mask_im = -mask_im
    
    return mask_im

    
def choose_locations(num, sample_points, prev_loc):
    # compute number of sample points
    num_points = len(sample_points)
    
    # compute euclidean distance between all sample points
    distances = np.empty((num_points,num_points))
    distances = spatial.distance.pdist(sample_points, 'euclidean')
    dist_mat = spatial.distance.squareform(distances)
    
    # minimal distance between center of 2 bubbles = diameter of bubble
    MIN_DIST = 154
    
    # find list index of previous location
    prev_ind = sample_points.index(prev_loc[0])
    # not necessary since prev_loc has distance 0 to prev_loc and will be
    # removed automatically
    #sample_points.remove(prev_loc[0])
    
    # make a copy of the sample point list for changes in subtrial
    points_copy = list(sample_points)
    
    # distances of all locations to previous location
    dist_to_prev = dist_mat[prev_ind,:]    
    
    # remove all locations which would yield overlapping bubbles        
    remove_from_copy = np.where(dist_to_prev < MIN_DIST)
    dist_to_prev_list = list(dist_to_prev)
    for item in remove_from_copy[0]:
        if sample_points[item] in points_copy:
            points_copy.remove(sample_points[item])
            dist_to_prev_list.remove(dist_to_prev[item])
    
    # draw new locations from possible locations according to probability 
    # distribution (higher likelihood for closer bubbles) 
    next_loc = []
    for i in np.arange(num): # for each new location
        weights = 1 - (dist_to_prev_list-np.min(dist_to_prev_list))/np.ptp(dist_to_prev_list)
        weights = weights/sum(weights)
        custm = stats.rv_discrete(name='custm', values=(np.arange(len(points_copy)), weights))
    
        index = custm.rvs(size=1)
        next_loc.append(points_copy[index[0]])
        points_copy.remove(points_copy[index[0]])
        
        # delete locations which would yield overlappings with the newly
        # chosen location
        new_ind = sample_points.index(next_loc[i])
        dist_to_new = dist_mat[new_ind,:]
        remove_from_copy = np.where(dist_to_new < MIN_DIST)
        #dist_to_prev_list = list(dist_to_prev)
        for item in remove_from_copy[0]:
            if sample_points[item] in points_copy:
                points_copy.remove(sample_points[item])
                dist_to_prev_list.remove(dist_to_prev[item])
        
    return next_loc
    
def create_bubble_image(image, loc):
    
    size_inv = (image.size[1],image.size[0])
    background = Image.new('L',image.size)
    mask_im = create_mask(loc, size_inv)
    mask_im = -(mask_im/2+1)*255
    #background.paste(image, mask=mask_im)
    image.paste('gray',mask=mask_im)    
    
    return background

'''display memory task, return displayed bubbles and decision'''        
def memory_task(image,memory_image,surf):
    correct = 'No valid answer yet'
    # Sample bubble locations for current image from Poisson distribution
    width, height = image.size
    sample_points = poisson_sampling(width,height)
    #bubble from shown image for task
    same_pic_rand_bubble_loc = [random.choice(sample_points)]
    #create bubble image
    same_pic_rand_bubble = create_bubble_image(image, same_pic_rand_bubble_loc)
    plt.show(same_pic_rand_bubble)
    #save image and bubble position
    #same_pic_rand_bubble_loc = [bubble_image,same_pic_rand_bubble_loc]
    #bubble from other image
    other_images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/')
    other_pic_rand_bubble_loc = [random.choice(sample_points)]
    other_pic = random.choice(other_images)
    #make sure it is from another image
    while other_pic == image:
        other_pic = random.choice(other_images)
    #load bubble 
    other_pic_rand_bubble = create_bubble_image(other_pic, other_pic_rand_bubble_loc) #visual.SimpleImageStim(surf,path_to_fixdur_files+'stimuli/single_bubble_images/'+other_pic_rand_bubble_loc[0]+'/'+other_pic_rand_bubble_loc[1])
    #other_pic_rand_bubble =  
    #save image and bubble position
    #other_pic_rand_bubble_loc = [other_pic_rand_bubble_loc[0],[int(other_pic_rand_bubble_loc[1].split('_',1)[1].split('_')[0]),int(other_pic_rand_bubble_loc[1].split('_',1)[1].split('_')[1].split('.')[0])] ]    
    #mon_res = surf.size
    #locations = [(mon_res[1]/2,mon_res[0]/2-300),(mon_res[1]/2,mon_res[0]/2+300)] 
    #locations = [(mon_res[0]/2-300,mon_res[1]/2),(mon_res[0]/2+300,mon_res[1]/2)]    
    #print locations
    locations = [(-200,0),(200,0)]    
    #locations = [(386,400),(740,400)]
    same = random.choice(locations)   
    locations.remove(same)
    
    
    memory_image.draw(surf)
    same_pic_rand_bubble.pos = same
    same_pic_rand_bubble.draw(surf)
    
    other_pic_rand_bubble.pos = locations[0]
    other_pic_rand_bubble.draw(surf)
    
    #memory_image.blit(same_pic_rand_bubble,same)
    #memory_image.blit(other_pic_rand_bubble,locations[0])
    #surf.blit(memory_image,(320,60))
    surf.flip()
    #pygame.display.update()
    key = event.waitKeys(keyList=['left', 'right'])    
    #key = wait_for_key(keylist = [K_LEFT,K_RIGHT])
    #if left bubble is correct and left bubble was choosen
    
    if (((same == (-200,0)) and (key == ['left'])) or \
    #if (((same == (386,400)) and (pygame.key.name(key.key) == 'left')) or \
    #if right bubble is correct and right bubble was choosen
    ((same == (200,0)) and (key == ['right']))):    
    #((same == (740,400)) and (pygame.key.name(key.key) == 'right'))):
        correct = True
    else:
        correct = False
    if same == (-200,0):
    #if same == (386,400):
        left_bubble = same_pic_rand_bubble_loc
        right_bubble = other_pic_rand_bubble_loc
    if same == (200,0):
    #if same == (740,400):
        left_bubble = other_pic_rand_bubble_loc
        right_bubble = same_pic_rand_bubble_loc
        
    return [correct,left_bubble,right_bubble]
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



