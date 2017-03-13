
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 11:37:14 2016
@author: jschepers
"""
import numpy as np
from PIL import Image
from psychopy import visual, event
import tools
#import matplotlib.pyplot as plt
#import re
import sys, os
from scipy import spatial, stats
import random

path_to_fixdur_files, path_to_fixdur_code = tools.paths()

# import code for poisson sampling
sys.path.append(path_to_fixdur_code+'poisson_disk_python/src')
import poisson_disk

#define patterns for pattern matching
#p_noise = re.compile('noise')
#p_urban = re.compile('image')

# set parameters for gaussian
bubble_size = 1.1774
size_ex = round(tools.deg_2_px(bubble_size))*3
size_ex = 154 # Hard Code, this is the point where there is no difference between 0 and 1 (on a scale of 255)
size =size_ex
fwhm = round(tools.deg_2_px(bubble_size))

#rectXY = (1920,1080)
#surf = visual.Window(size_ex=rectXY,fullscr=False,winType = 'pyglet', screen=1, units='pix')


def whole_image(chosen_location):
 
    # swap coordinates because mask matrix has different coordinate system
    y = chosen_location[0][1]
    x = chosen_location[0][0] 

    # create gaussian kernel      
    gaussian = makeGaussian()   
    
    # embed gaussian in matrix which has the same size_ex as the image
    #mask_im = np.ones((2048,2048))
    mask_im = np.ones((960,1280))
    
    
    #x = x + (2048-1280)/2.
    #y = y + (2048-960)/2.
    mask_im[int(y-size_ex/2):int(y+size_ex/2),int(x-size_ex/2):int(x+size_ex/2)] = gaussian
    #mask_im[450:630,870:1050] = gaussian
    
    return mask_im


''' copied and modified from Lilli's generate_stimuli file'''

def makeGaussian():
    """ Create a mask stimulus with square gaussian kernel.
 
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """

    x = np.arange(0, size_ex, 1, float)
    y = x[:,np.newaxis]
    
    #if center is None:
    x0 = y0 = size_ex // 2
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
    width = width - size_ex
    height = height - size_ex
    
    p = poisson_disk.sample_poisson_uniform(width, height, 77, 30)

    sample_points = []
    for i in range(len(p)):
        # difference between screen size and image size/2
        diff_x = 0#(1920-1280)/2
        diff_y = 0#(1080-960)/2
        # adjust coordinates ((0,0) is upper left corner)
        x = int(p[i][0]) + diff_x + size_ex/2
        y = int(p[i][1]) + diff_y + size_ex/2
        sample_points.append((x,y))
        #sample_points[i][0] = int(p[i][0])
        #sample_points[i][1] = int(p[i][1])
    return sample_points
 
   
def create_mask(locations, mask_size=(960,1280), MULTIPLE=False):
    
   # mask_size=
    #mon_res = surf.size
    # number of bubbles needed
    num = len(locations)

    
    # create gaussian kernel which is the same for all bubbles
    gaussian = makeGaussian()
    mask_im = np.ones(mask_size)
    
    for i in np.arange(num):
        # swap coordinates because mask matrix has different coordinate system
        y = int(locations[i][1])
        x = int(locations[i][0])
        
        if MULTIPLE:
            x = x + (2048-1280)/2.
            y = y + (2048-960)/2.
                
        # embed gaussian in matrix which has the same size as the window
        # possible error: could not broadcast input array from shape (180,180) into shape (180,0)
        try:
            mask_im[int(y-size_ex/2):int(y+size_ex/2),int(x-size_ex/2):int(x+size_ex/2)] = gaussian
        except:
            print x,y,size_ex
            raise
                        
    # invert matrix to get background with bubbles
    mask_im = -mask_im
    
    return mask_im

def create_mask_fast(locations,surf,gausStim=None):
    # Useable only for a single bubble, but very fast for that one (after the first call)
    # gausMask = tools_extended.create_mask_fast([(150,150)],surf,gausMask)
    #width_img = 1280
    #height_img = 960
    width_img = 2048
    height_img = 2048
    
    
    if gausStim == None:
        import psychopy.visual
        #mask = create_mask([(width_img,height_img)],mask_size=(2048,2048))
        mask = create_mask([(width_img,height_img)],mask_size=(height_img*2,width_img*2))
        #maskimage = Image.new('L',(2048,2048),128)
        maskimage = Image.new('L',(width_img*2,height_img*2),128)
        gausStim = psychopy.visual.ImageStim(surf,maskimage,mask=-mask)
        
    num = len(locations)
    if num != 1:
        raise('locations too long')
    #for i in np.arange(num):
        
    y = locations[0][1]# - width_img/2
    x = locations[0][0]# - height_img/2
    
    x = x + (2048-1280)/2. - 2048/2
    y = y + (2048-960)/2.  - 2048/2
    #print(x,y)
    #if (x>640 or x<-640 or y>480 or y<-480):
    #    print("Too far apart")
    #    print(x,y)
    gausStim.setPos((x,y))
    gausStim.draw()
        
    return(gausStim)

    
    
def choose_locations(whole_image,num, sample_points, remaining_points, prev_loc):

    if whole_image:
        sample_points.append(prev_loc[0])

    # compute number of sample points
    #num_points = len(sample_points)
    
    # compute euclidean distance between all sample points
    #distances = np.empty((num_points,num_points))
    distances = spatial.distance.pdist(sample_points, 'euclidean')
    dist_mat = spatial.distance.squareform(distances)
    
    # minimal distance between center of 2 bubbles = diameter of bubble
    MIN_DIST = 154
    
    # find list index of previous location
    prev_ind = sample_points.index(prev_loc[0])
    # not necessary since prev_loc has distance 0 to prev_loc and will be
    # removed automatically
    #sample_points.remove(prev_loc[0])
    
    # make a copy of the remaining points list for changes in subtrial
    points_copy = list(remaining_points)
    
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
        #points_copy.remove(points_copy[index[0]])
        

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
    if whole_image:
        sample_points.pop(prev_ind)
        
    return next_loc
    
def create_bubble_image(stim, loc,surf):
    
    mask = create_mask(loc)
    stim.mask = mask

    
    return stim

'''display memory task, return displayed bubbles and decision'''        
def memory_task(stim,memory_image,surf,stimList_preload,bubble_image):
    correct = 'No valid answer yet'
    # Sample bubble locations for current image from Poisson distribution
    width, height = stim.size
    sample_points = poisson_sampling(width,height)
    #bubble from shown image for task
    same_pic_rand_bubble_loc = [random.choice(sample_points)]
    #create bubble image
    # same_pic_rand_bubble_loc  = [surf.size/2]
    same_pic_rand_bubble = create_bubble_image(stim, same_pic_rand_bubble_loc,surf)
    #save image and bubble position
    #same_pic_rand_bubble_loc = [bubble_image,same_pic_rand_bubble_loc]
    #bubble from other image
    other_images = os.listdir(path_to_fixdur_files+'stimuli/urban/')
    other_pic_rand_bubble_loc = [random.choice(sample_points)]
    other_pic = random.choice(other_images)
        
    #make sure it is from another image
    while other_pic == bubble_image:
        other_pic = random.choice(other_images)
        
    other_stim = stimList_preload[other_pic]
        
    #other_pic_rand_bubble_loc  = [surf.size/2]
    other_pic_rand_bubble = create_bubble_image(other_stim, other_pic_rand_bubble_loc,surf) #visual.SimpleImageStim(surf,path_to_fixdur_files+'stimuli/single_bubble_images/'+other_pic_rand_bubble_loc[0]+'/'+other_pic_rand_bubble_loc[1])
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
    locations = locations[0]
    
    memory_image.draw(surf)
    #pos = ((image.size[0]/2 - same_pic_rand_bubble_loc[0][0] + same[0]),(image.size[1]/2 - same_pic_rand_bubble_loc[0][1])+ same[1])
    pos = ((width/2 - same_pic_rand_bubble_loc[0][0] + same[0]),(height/2 - same_pic_rand_bubble_loc[0][1])+ same[1])
    same_pic_rand_bubble.pos = pos
    same_pic_rand_bubble.draw(surf)
    same_pic_rand_bubble.pos = (0,0)
    #other_pos = (locations[0][0]-other_pic_rand_bubble_loc[0][0]+surf.size[0]/2,-(-locations[0][1]-other_pic_rand_bubble_loc[0][1]+surf.size[1]/2))
    #other_pos = ((other_pic_rand_bubble_loc[0][0]+surf.size[0]/2),-(surf.size[1]/2 - other_pic_rand_bubble_loc[0][1]))
    other_pos = ((width/2 - other_pic_rand_bubble_loc[0][0]+locations[0]),(height/2 - other_pic_rand_bubble_loc[0][1])+ locations[1])
    other_pic_rand_bubble.pos = other_pos
    other_pic_rand_bubble.draw(surf)
    other_pic_rand_bubble.pos = (0,0)
    #memory_image.blit(same_pic_rand_bubble,same)
    #memory_image.blit(other_pic_rand_bubble,locations[0])
    #surf.blit(memory_image,(320,60))
    surf.flip()
    #pygame.display.update()
    key = event.waitKeys(keyList=['left', 'right'])
    #key = 'right'    ### Needs to be changed
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
        
    same_bubble = [bubble_image,same_pic_rand_bubble_loc]
    other_bubble = [other_pic,other_pic_rand_bubble_loc]

    if same == (-200,0):
    #if same == (386,400):
        left_bubble = same_bubble
        right_bubble = other_bubble
    if same == (200,0):
    #if same == (740,400):
        left_bubble = other_bubble
        right_bubble = same_bubble
        
    return [correct,left_bubble,right_bubble]
    
def tracker_init(surf):
    
    import pylink
    from EyeLinkCoreGraphicsPsychopy import EyeLinkCoreGraphicsPsychopy
    
    # set up a link to the tracker
    tk = pylink.EyeLink('100.1.1.1')

    # graphics
    genv = EyeLinkCoreGraphicsPsychopy(tk, surf)
    pylink.openGraphicsEx(genv)    
    
    # set screen_pixel_coords, not sure if necessary or correct by itself
    pylink.getEYELINK().sendCommand('screen_pixel_coords = 0 0 %d %d'%(surf.size[0],surf.size[1]));
    # If you use Eyelink II you have to specify: (check the numbers! they don't match)
    #eyetracker.sendCommand('marker_phys_coords = -275,165, -275,-165, 275,165, 275,-165')
    pylink.getEYELINK().sendCommand('screen_phys_coords = -266, 149, 266, -149')
	
    pylink.getEYELINK().sendCommand('screen_distance = 800 800') #  distance to top and bottom of screen (I got this with a central viewing distance of 60cm, this assumes the screen is vertically centered on the eye
	
	
    # set calibration to 5 Targets
    pylink.getEYELINK().sendCommand('calibration_type = HV13')
	
    #% % Set custom calibration options
    #% % layout on screen for 13 points:
    #% % 5    1    6
    #% %   9    10
    #% % 3    0    4
    #% %   11   12
    #% % 7    2    8
	
    #% left, left-middle, middle, middle right right
    scr_w = surf.size[0]
    scr_h = surf.size[1]
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

    calibTargets = 'calibration_targets  = %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, lm,tc, lm,cb, mr,tc, mr,cb)
    validTargets = 'validation_targets   = %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d %d,%d'%(m,c, m,t, m,b, l,c, r,c, l,t, r,t, l,b, r,b, lm,tc, lm,cb, mr,tc, mr,cb)

    pylink.getEYELINK().sendCommand(calibTargets)
    pylink.getEYELINK().sendCommand(validTargets)
 

    # doTrackerSetup
    tk.doTrackerSetup()
    
    return tk
    
    
    
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

