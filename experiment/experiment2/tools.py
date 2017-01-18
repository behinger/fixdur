import numpy as np
#import pygame
import random, scipy, os
from psychopy import visual, core, event, monitors
from math import atan2, degrees,sqrt,atan,sin,cos,exp,log
from scipy import stats, spatial
from pygame.locals import *
from collections import deque
#import tools_extended as tools_ex

try:
    import fixdur_tracker as tracker
    import pylink
except ImportError:
    print 'pylink and fixdur_tracker cannot be imported'

#import collections
#from numpy.compat import long

TRIAL_LENGTH = 20000    #how long do we want to wait for a saccade:

TRACKING_FREQ = 500
PPD = 50 
#PPD = 76
MAT = 154





def paths():
    '''return paths'''
    if os.path.exists('/home_local/thesis/fixdur_git/experiment/'):
        path_to_fixdur_files = '/home_local/thesis/fixdur_git/experiment/'
        path_to_fixdur_code = '/home_local/thesis/fixdur_git/experiment/experiment2/'
    elif os.path.exists('/net/store/nbp/projects/fixdur/'):
        path_to_fixdur_files = '/net/store/nbp/projects/fixdur/'
        path_to_fixdur_code = '/home/student/j/jschepers/thesis/fixdur_git/experiment/experiment2/'
    elif os.path.exists('/home/jschepers/Dokumente/bachelor_thesis/fixdur/'):
        path_to_fixdur_files = '/home/jschepers/Dokumente/bachelor_thesis/'
        path_to_fixdur_code = '/home/jschepers/Dokumente/bachelor_thesis/'
    if os.path.exists('/home/experiment/experiments/fixdur/experiment/'):
        path_to_fixdur_files = '/home/experiment/experiments/fixdur/cache/'
        path_to_fixdur_code = '/home/experiment/experiments/fixdur/experiment/experiment2/'

    
    return path_to_fixdur_files, path_to_fixdur_code

def deg_2_px(visual_degree):
    """ Convert given Visual Degree Size into Number of Pixels """
    r = 1080 # Vertical resolution of the monitor
    h = (.276*r)/10 # Monitor height in cm (1px = 0.276mm)
    d = 80 # Distance between monitor and participant in cm
    size_in_deg = visual_degree # The stimulus size in visual_degree
    # number of degrees that correspond to a single pixel
    deg_per_px = degrees(atan2(.5*h, d)) / (.5*r)
    #print '%s degrees correspond to a single pixel' % deg_per_px
    # Calculate the size of the stimulus in degrees
    size_in_px = size_in_deg / deg_per_px
    #print 'The size of the stimulus is %s pixels and %s visual degrees' \
    #% (size_in_px, size_in_deg)
    return size_in_px

''' generize, save and return randomization for given subject'''
def randomization(subject, trial_time):

    # 32 trials in control condition + 64 with variation of num of bubbles = 96
    
    #images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/')
    
    # dimensions of output array: 
    trials = []         # image number
    num_bubbles = []    # number of bubbles
    disp_time = []      # time of bubble display
    control_list = []   # information if control condition is applied
    trial_num = []

    for condition in range(2):
        
        images = os.listdir(path_to_fixdur_files+'stimuli/urban/')
        # control condition in the first 32 trials
        #if (0 <= trial_num < 32):
        #    control = 1
        #else:
        #    control = 0
        
        if condition == 0:
            
            # control condition is set true
            control = 1
            
            # for the first part (control condition) choose 32 images from all images (32 trials) 
            images = random.sample(images,32)
            
            # for the first 32 trials set num of bubbles to 1-5
            xk = [1,2,3,4,5]
            # uniform distribution of number of bubbles
            pk = np.empty(len(xk))
            pk.fill(1./len(xk))
            custm = stats.rv_discrete(name='custm', values=(xk, pk))
            
            #  whole image condition is false
            whole_img = np.empty(len(images))
            whole_img.fill(False)
            
       
        if condition == 1:
            
            control = 0
            
            # for the second part (variation of num of bubbles) take all images
            np.random.shuffle(images)
            
             # for the trials 33 to 98 set num of bubbles to 2,4,8,16 or whole (0)
            xk = [1,2,4,8,16]
            # uniform distribution of number of bubbles
            pk = np.empty(len(xk))
            pk.fill(1./len(xk))
            custm = stats.rv_discrete(name='custm', values=(xk, pk))
            
            whole_img = np.empty(len(images))
            whole_img[0:(len(images)/2)] = False
            whole_img[(len(images)/2):len(images)] = True
            np.random.shuffle(whole_img)
            
       # trial_num_list = list(range(32+64))
        
        for i,image in enumerate(images):
            

            # reset counter
            time = 0
        
            while time<trial_time:
                # image
                trials = np.append(trials,image)
            
                # probability that control condition is applied is 1/2
                #if time == 0:            
                #    control = np.random.randint(2)
                control_list.append(control)            
            
                # num of bubbles
                if whole_img[i] == True:
                    num_bubble = [np.random.choice([0,1,2,4,8,16])]
                else:
                    num_bubble = custm.rvs(size=1)
                num_bubbles = np.append(num_bubbles,num_bubble[0])

                # display time of bubble
                disp = scipy.random.exponential(295,1)
                disp_time = np.append(disp_time,int(disp))
            
                if control == 0:
                    tIdx = 32+i
                else:
                    tIdx = i
                trial_num = np.append(trial_num,tIdx)
                # increase counter
                if int(disp) == 0:
                    disp = 1
                time = time + int(disp)
            #i = i+1
 
    #control = np.random.randint(2,size=(len(trials),1))
    trials = np.reshape(trials,(len(trials),1))
    #trial_type = np.reshape(trial_type,(len(trial_type),1))
    num_bubbles = np.reshape(num_bubbles,(len(num_bubbles),1))
    disp_time = np.reshape(disp_time,(len(disp_time),1))
    control_list = np.reshape(control_list,(len(control_list),1))
    trial_num = np.reshape(trial_num,(len(trial_num),1))
    #trial_mat = np.append(trials,trial_type,axis=1)
    trial_mat = np.append(trials,num_bubbles,axis=1)
    trial_mat = np.append(trial_mat,disp_time,axis=1)
    trial_mat = np.append(trial_mat, control_list, axis=1)
    trial_mat = np.append(trial_mat,trial_num,axis=1)
    # create vector if control condition is applied in the trial or not
    #control_mat = np.random.randint(2,size=(1,total_num_trials))

    np.save(path_to_fixdur_code+'/data/'+str(subject)+'/rand_'+str(subject),trial_mat)

    return trial_mat



#get center bubble location relative to center of screen
def get_bubble_pos(bubble):
    x,y = int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])
    x = x + 320 + 77 - 960
    y = y + 60 + 77 - 540
    return x,y


''' copied from Simons tool file'''
def slideshow(surf, ims):
    ims = [visual.SimpleImageStim(surf,im.tostring()) for im in ims]
    #ims = [pygame.image.load(im) for im in ims]
    #arrows = pygame.image.load(path_to_fixdur_code+'images/arrowkeys_sm.png')
    #center = np.array(screen.get_size())/2
    i = 0
    
    while True:
        
        
        ims[i].draw()
        surf.flip()
        #screen.blit(ims[i], center-np.array(ims[i].get_size())/2)
        #screen.blit(arrows, np.array(screen.get_size()) - np.array(arrows.get_size()) - np.array((10,10)))
        #pygame.display.flip()
        
        key = event.waitKeys(keyList=['left', 'right'])
        #key = wait_for_key(keylist = [276, 275])
        #screen.fill((255,255,255))
        
        if key == ['right']:        
        #if key.key == 275:
            if (i == len(ims)-1):
                return
            else:
                i += 1
        elif (key == ['left'] and i>0):
        #elif (key.key == 276 and i>0):
            i -= 1

def wait_for_key(keylist = None):
    return(event.getKeys(keyList = keylist))
    #return(event.waitKeys(keyList = keylist))
 #   while 1:
 #       for event in psychopy.event.getKeys():
 #           if event.type == pygame.KEYDOWN:
 #               if keylist is not None:
 #                   if event.key in keylist:
 #                       return event
 #               else:
 #                   return event
 #       pygame.time.delay(50)


''' Choose new bubble location in whole image condition when timeout occured '''
def choose_location_timeout(sample_points,current_loc,prev_loc):
    # import package for distance computations
    from scipy import spatial
    
    # create copy of sample_points to not change the original
    points_copy = list(sample_points)
    
    # minimal distance between center of 2 bubbles = diameter of bubble
    MIN_DIST = 154
    
    # compute distance between sample points and previous location
    distances_prev = spatial.distance.cdist(prev_loc,points_copy,'euclidean')
    distances_prev_list = list(distances_prev[0])
    
    # remove all locations which would yield overlapping with previous bubble
    for i,dist in enumerate(distances_prev_list):
        if dist< MIN_DIST:
            points_copy.remove(sample_points[i])
            #distances_prev_list.remove(distances_prev[i])   
    
    # compute distance between remaining sample points and current location
    distances_curr = spatial.distance.cdist(current_loc,points_copy,'euclidean')
    
    # draw new location from possible locations according to probability 
    # distribution (higher likelihood for closer bubbles) 
    # Taking distances from current location (NOT from previous)
    weights = 1 - (distances_curr-np.min(distances_curr))/np.ptp(distances_curr)
    weights = weights[0]/sum(weights[0])
    custm = stats.rv_discrete(name='custm', values=(np.arange(len(points_copy)), weights))
    
    index = custm.rvs(size=1)
    next_loc = points_copy[index[0]]
        
    return next_loc


'''    
predict saccade end point
return bubble if in distance of diameter(MAT) of bubble center
'''    
def sacc_detection(el,used_locations,whole_image,surf,prev_loc,remaining_points):
    #buffer for x coordiante, y coordinate, velocity
    bufferx, buffery, bufferv = deque(maxlen=3), deque(maxlen=3), deque(maxlen=4)
    start = pylink.currentTime()
    saccade = 0

    while (pylink.currentTime() - start) < TRIAL_LENGTH:
        i = el.getNextData()
        # wenn es etwas anderes ist als RAW_DATA(=200), naechster schleifendurchlauf
        if i!=200: continue
        # actuelle position direkt vom eye-tracker
        x, y = el.getNewestSample().getLeftEye().getGaze()
        # Eyetracker Koordinaten (Screen-Koordinaten?) in Bildkoordinaten umrechnen
        x  = x - (surf.size[0]-1280)/2
        y  = y - (surf.size[1]-960)/2
        y  = 960-y
        
        # XXX
        #stim.pos = (x-surf.size[0]/2,surf.size[1]-y-surf.size[1]/2)
        #stim.draw()
        #surf.flip(clearBuffer=False)
        #XXX
        
        # don't add too high coordinate values (beccause of blinks) to buffer
        # add previous coordinates instead
        if abs(x)>10000:
            x = bufferx[-1]
        if abs(y)>10000:
            y = buffery[-1]
        

        bufferx.append(float(x))
        buffery.append(float(y))
        
        # Compute velocity in degrees per second
        bufferv.append(np.mean(((np.diff(np.array(bufferx))**2+np.diff(np.array(buffery))**2)**.5) * TRACKING_FREQ)/float(PPD))
        #print 'bubble then ET'
        #print prev_loc
        #print x,y
        #saccade_onset
        if bufferv[-1] < 30:
            saccade = 0
            #print used_locations
            #print MAT,x,y
            #check if sample already in next bubble
            if whole_image == False:
                for bubble in used_locations:
                    #print bubble
                    if ((sqrt(((bubble[0]-x)**2) + ((bubble[1]-y)**2))) < (MAT/2.)):                    
#                    if ((sqrt((((bubble[0]+(MAT/2.)+320)-x)**2) + (((bubble[1]+(MAT/2.)+60)-(1080-y))**2))) < (MAT/2.)):
                        el.trialmetadata('start_x', bufferx[-1])
                        el.trialmetadata('start_y', buffery[-1])
                        el.trialmetadata('start_velocity', bufferv[-1])
                        el.trialmetadata('end_x', bufferx[-1])
                        el.trialmetadata('end_y', buffery[-1])
                        el.trialmetadata('end_velocity', bufferv[-1])
                        el.trialmetadata('sacc_detection', 'start_in_bubble')
                        return bubble
                        
            else:
                # compute distance between centre of the previous bubble and the current fixation

                if ((bufferx[-1]<MAT/2) or (bufferx[-1]>(1280-MAT/2)) or (buffery[-1]<MAT/2) or (buffery[-1]>(960-MAT/2))):
                    continue
                dist = spatial.distance.pdist([prev_loc,(bufferx[-1],buffery[-1])], metric='euclidean')
                print(dist)
                if abs(dist)>10000: # sometimes ET gives strange big numbers (bene thinks this has to do with missing samples)
                    continue
                
                # make sure, that next fixation is at least 2/3 bubble-size away from the previous location
                if (dist > 2*MAT/3.):
                    print 'ET quit because distance'
                    return (bufferx[-1],buffery[-1])                  
                        
        if saccade == 0 and bufferv[-1]>70:
            start_x = float(bufferx[-1])
            start_y = float(buffery[-1])
            #start_time = pylink.currentTime()
            saccade = 1
            el.trialmetadata('start_x', start_x)
            el.trialmetadata('start_y', start_y)
            el.trialmetadata('start_velocity', bufferv[-1])
            #continue
        '''    
        #saccade end
        if start_time and np.all(np.diff(bufferv)<0):
            
            #if abs((start_x - bufferx[-1])) < 0.00000001:
            #    alpha = 3.1415926535897931 / 2 # pi/2 = 90deg
            #else:
            alpha = atan2((buffery[-1]-start_y),(bufferx[-1]-start_x))
            
            predLength = exp((log(bufferv[0]) - 4.6)/.55)*PPD
            predX = start_x + cos(alpha) * predLength
            predY = start_y + sin(alpha) * predLength
            el.trialmetadata('predX', predX)
            el.trialmetadata('predY', predY)
            el.trialmetadata('end_velocity', bufferv)
            start_time = []
            for bubble in used_bubble:
                if ((sqrt((((bubble[0]+(MAT/2)+320)-predX)**2) + (((bubble[1]+(MAT/2)+60)-predY)**2))) < MAT):
                    print "predicted bubble found"
                    return bubble 
        '''
        if whole_image == False:
            
            if bufferv[-1] < 50 and saccade:
                for bubble in used_locations:
                    if (sqrt((((bubble[0])-x)**2) + (((bubble[1]-y)**2))) < 2*MAT/3):
                        el.trialmetadata('end_x', bufferx[-1])
                        el.trialmetadata('end_y', buffery[-1])
                        el.trialmetadata('end_velocity', bufferv[-1])
                        el.trialmetadata('sacc_detection', 'pred_in_bubble')
                        return bubble
        else:
            if bufferv[-1] < 40 and saccade:
                if ((bufferx[-1]<MAT/2) or (bufferx[-1]>(1280-MAT/2)) or (buffery[-1]<MAT/2) or (buffery[-1]>(960-MAT/2))):
                    continue
                
                
                dist = spatial.distance.pdist([prev_loc,(bufferx[-1],buffery[-1])], metric='euclidean')
                if abs(dist)>10000: # sometimes ET gives strange big numbers (bene thinks this has to do with missing samples)
                    continue
                #print prev_loc
                #print x,y
                #print(dist)
                # make sure, that next fixation is at least one bubble-size away from the previous location
                if (dist > 2*MAT/3.):
                    print 'ET quit because smaller 40'
                    el.trialmetadata('end_x', bufferx[-1])
                    el.trialmetadata('end_y', buffery[-1])
                    el.trialmetadata('end_velocity', bufferv[-1])
                    el.trialmetadata('sacc_detection', 'pred_in_bubble')
                    return (bufferx[-1],buffery[-1])
                            
        #check if sample near bubble (in distance of 2 * radius MAT/2)
    #print "random bubble returned" 
    el.trialmetadata('sacc_detection', 'random')
    if whole_image == False:
        return random.choice(used_locations) #if no prediction on bubble during trial_length
    else:
        current_loc = (bufferx[-1],buffery[-1])
        next_loc = choose_location_timeout(remaining_points,current_loc,prev_loc)
        return next_loc
    
    
path_to_fixdur_files, path_to_fixdur_code = paths()

def debug_time(dispstr,start):
    pass
    #print "%s : %.2f"%(dispstr,1000*(core.getTime()-start))
    #print "%s : %.2f"%(dispstr,1000*(core.getTime()-start))
