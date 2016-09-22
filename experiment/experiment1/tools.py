import numpy as np
import pygame, random, scipy, os
from psychopy import visual, core, event 
from math import atan2, degrees,sqrt,atan,sin,cos,exp,log
from scipy import stats
from pygame.locals import *
from collections import deque

try:
    import fixdur_tracker as tracker
    import pylink
except ImportError:
    print 'pylink and fixdur_tracker cannot be imported'

#import collections
#from numpy.compat import long

TRIAL_LENGTH = 2000    #how long do we want to wait for a saccade:

TRACKING_FREQ = 500
PPD = 50 
#PPD = 76
MAT = 154




def paths():
    '''return paths'''
    if os.path.exists('/home_local/tracking/experiments/fixdur/'):
        path_to_fixdur_files = '/home_local/tracking/experiments/fixdur/'
        path_to_fixdur_code = '/home_local/tracking/experiments/fixdur/expcode/'
    elif os.path.exists('/net/store/nbp/projects/fixdur/'):
        path_to_fixdur_files = '/net/store/nbp/projects/fixdur/'
        path_to_fixdur_code = '/home/student/l/lkaufhol/fixdur/expcode/'
    elif os.path.exists('/home/lkaufhol/Dokumente/studium/master/master_thesis/fixdur/'):
        path_to_fixdur_files = '/home/lkaufhol/Dokumente/studium/master/master_thesis/fixdur/'
        path_to_fixdur_code = '/home/lkaufhol/Dokumente/studium/master/master_thesis/fixdur/expcode/'
    
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
    # ratio of number of bubbles: 1=50, 2=25, 3 =12.5, 4=6.25, 5=3.125 -> normalization factor to get to 100%: x=100/sum(ratios)
    x=100/96.875
    # custom distribution for ratios:
    xk = np.arange(5)+1
    pk = (0.5*x,0.25*x,0.125*x,0.0625*x,0.03125*x)
    custm = stats.rv_discrete(name='custm', values=(xk, pk))
    # num_of_bubbles_ratio = [[i] for i in [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,3,3,3,3,4,4,5]]
    
    images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/')
    np.random.shuffle(images)
    
    types = []
    for a in range(int(len(images)/4)):
        types.append('all')
    for a in range(int((len(images)/4)*3)):
        types.append('seq')
    random.shuffle(types)

    # dimensions of output array: 
    trials = []         # image number
    trial_type = []     # all_bubbles or sequential
    num_bubbles = []    # number of bubbles
    disp_time = []      # time of bubble display
    #bubble_sums = []
    #fix_nums = []
    a = 0;
    for image in images:
        # reset counter
        time = 0
        #bubble_sum = 0
        #fix_num = 0
        while time<trial_time:
            # image
            trials = np.append(trials,image)
            # if new trial beginns
            try:
                if (time == 0):
                    trial_type = np.append(trial_type,types[0])
                    types.remove(types[0])
                    a = a+1
                    # if we are still in the same trial    
                else:
                    trial_type = np.append(trial_type,trial_type[-1])
            except:
                IndexError 
            # num of bubbles            '''
            num_bubble = custm.rvs(size=1)
            num_bubbles = np.append(num_bubbles,num_bubble[0])
            #bubble_sum = bubble_sum + num_bubble[0]
            # display time of bubble
            disp = scipy.random.exponential(295,1)
            disp_time = np.append(disp_time,int(disp))
            # increase counter
            if int(disp) == 0:
                disp = 1
            time = time + int(disp)
            #fix_num = fix_num + 1
        #bubble_sums.append(bubble_sum)
        #fix_nums.append(fix_num)

    trials = np.reshape(trials,(len(trials),1))
    trial_type = np.reshape(trial_type,(len(trial_type),1))
    num_bubbles = np.reshape(num_bubbles,(len(num_bubbles),1))
    disp_time = np.reshape(disp_time,(len(disp_time),1))

    trial_mat = np.append(trials,trial_type,axis=1)
    trial_mat = np.append(trial_mat,num_bubbles,axis=1)
    trial_mat = np.append(trial_mat,disp_time,axis=1)

    np.save(path_to_fixdur_code+'/data/'+str(subject)+'/rand_'+str(subject),trial_mat)

    return trial_mat


''' copied from Simons tool file'''
def slideshow(screen, ims):
    ims = [pygame.image.load(im) for im in ims]
    #arrows = pygame.image.load(path_to_fixdur_code+'images/arrowkeys_sm.png')
    center = np.array(screen.get_size())/2
    i = 0
    
    while True:
        
        screen.blit(ims[i], center-np.array(ims[i].get_size())/2)
        #screen.blit(arrows, np.array(screen.get_size()) - np.array(arrows.get_size()) - np.array((10,10)))
        pygame.display.flip()
        key = wait_for_key(keylist = [276, 275])
        screen.fill((255,255,255))
        
        if key.key == 275:
            if (i == len(ims)-1):
                return
            else:
                i += 1
        elif (key.key == 276 and i>0):
            i -= 1

def wait_for_key(keylist = None):
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if keylist is not None:
                    if event.key in keylist:
                        return event
                else:
                    return event
        pygame.time.delay(50)

'''display memory task, return displayed bubbles and decision'''        
def memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image,surf):
    correct = 'No valid answer yet'
    #bubble from shown image for task
    same_pic_rand_bubble_loc = random.choice(all_bubbles)
    #load bubble
    same_pic_rand_bubble = loaded_bubbles[all_bubbles.index(same_pic_rand_bubble_loc)]
    #save image and bubble position
    same_pic_rand_bubble_loc = [bubble_image,same_pic_rand_bubble_loc]
    #bubble from other image
    bubble_mat = np.load(path_to_fixdur_code+'all_bubble_mat.npy')
    other_pic_rand_bubble_loc = random.choice(bubble_mat)
    #make sure it"s from another image
    while other_pic_rand_bubble_loc[0] == bubble_image:
        other_pic_rand_bubble_loc = random.choice(bubble_mat)
    #load bubble 
    other_pic_rand_bubble = pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+other_pic_rand_bubble_loc[0]+'/'+other_pic_rand_bubble_loc[1]).convert_alpha()   
    #save image and bubble position
    other_pic_rand_bubble_loc = [other_pic_rand_bubble_loc[0],[int(other_pic_rand_bubble_loc[1].split('_',1)[1].split('_')[0]),int(other_pic_rand_bubble_loc[1].split('_',1)[1].split('_')[1].split('.')[0])] ]    
    locations = [(386,400),(740,400)]
    same = random.choice(locations)   
    locations.remove(same)
    memory_image.blit(same_pic_rand_bubble,same)
    memory_image.blit(other_pic_rand_bubble,locations[0])
    surf.blit(memory_image,(320,60))
    pygame.display.update()
    key = wait_for_key(keylist = [K_LEFT,K_RIGHT])
    #if left bubble is correct and left bubble was choosen
    if (((same == (386,400)) and (pygame.key.name(key.key) == 'left')) or \
    #if right bubble is correct and right bubble was choosen    
    ((same == (740,400)) and (pygame.key.name(key.key) == 'right'))):
        correct = True
    else:
        correct = False
    if same == (386,400):
        left_bubble = same_pic_rand_bubble_loc
        right_bubble = other_pic_rand_bubble_loc
    if same == (740,400):
        left_bubble = other_pic_rand_bubble_loc
        right_bubble = same_pic_rand_bubble_loc
        
    return [correct,left_bubble,right_bubble]
    
    

def wait_for_saccade(el):
    start = pylink.currentTime()
    bufferx, buffery = deque(maxlen=3), deque(maxlen=3)
    saccade = False
    lastFixTime = -50
    lastSaccadeOnset = -20
    fixbufferx = []
    fixbuffery = []
    while (pylink.currentTime() - start) < TRIAL_LENGTH:
        # Anfragen, welcher Typ von daten gerade in der pipe wartet.
        i = el.getNextData()
        # wenn es etwas anderes ist als RAW_DATA(=200), naechster schleifendurchlauf
        if i!=200: continue
        lastSampleTime = pylink.currentTime()
		# actuelle position direkt vom eye-tracker
        x, y = el.getNewestSample().getLeftEye().getGaze()
        if pylink.currentTime()-lastSampleTime > 15:	#falls zu lange keine neuen sample-points, beginn von vorne mit neuen decks
            bufferx, buffery = deque(maxlen=3), deque(maxlen=3)
            bufferx.append(x)
            buffery.append(y)
            continue
        
        bufferx.append(x)
        buffery.append(y)
        if len(fixbufferx)<1:
            fixbufferx.append(x)
            fixbuffery.append(y)
            el.trialmetadata("FIXATION", 0.0) # Take first sample as first fix.
            el.trialmetadata("FIXCOOX", x) # markiere fixation als tag in eye-tracking data
            el.trialmetadata("FIXCOOY", y)
            
        # Compute velocity in degrees per second
        v = np.mean(((np.diff(np.array(bufferx))**2+np.diff(np.array(buffery))**2)**.5) * TRACKING_FREQ)/float(PPD)
        
        ## Saccade onset
        if v > 70 and not saccade and (pylink.currentTime() - lastFixTime) > 50:
            lastSaccadeOnset = pylink.currentTime()
            saccade = True
            el.trialmetadata("SACCADE", v)
        
        ## Saccade offset        
        if v < 30 and saccade and (pylink.currentTime() - lastSaccadeOnset) > 20:
            saccade = False
            lastFixTime = pylink.currentTime()
            
            el.trialmetadata("FIXATION", v)
            # Calculate the angle of the current saccade
            el.trialmetadata("FIXCOOX", x)
            el.trialmetadata("FIXCOOY", y)
            
            fixbufferx.append(x)
            fixbuffery.append(y)
            
            return fixbufferx,fixbuffery
    return [-1,-1],[-1,-1]

'''return displayed bubble closest to fixation'''
def get_fixated_bubble(used_bubble,fix_x,fix_y):
    distances = []
    for bubble in used_bubble:
        #add 77 to get center of bubble, add 320/60 for higher monitor resolution
        distances.append(sqrt((((bubble[0]+(MAT/2)+320)-fix_x[1])**2) + (((bubble[1]+(MAT/2)+60)-fix_y[1])**2)))
    index_chosen = distances.index(min(distances))
    return used_bubble[index_chosen]  #

'''return bubble when fixation on bubble and velocity of saccade<30'''    
def wait_for_fix(el,used_bubble):
    #print "-----"
    bufferx, buffery = deque(maxlen=3), deque(maxlen=3)
    start = pylink.currentTime()
    while (pylink.currentTime() - start) < TRIAL_LENGTH:
        i = el.getNextData()
        # wenn es etwas anderes ist als RAW_DATA(=200), naechster schleifendurchlauf
        if i!=200: continue
        lastSampleTime = pylink.currentTime()
        # actuelle position direkt vom eye-tracker
        x, y = el.getNewestSample().getLeftEye().getGaze()
        bufferx.append(x)
        buffery.append(y)
        
        # Compute velocity in degrees per second
        v = np.mean(((np.diff(np.array(bufferx))**2+np.diff(np.array(buffery))**2)**.5) * TRACKING_FREQ)/float(PPD)
        
        if v<30:
            for bubble in used_bubble:
                #add 77 to get center of bubble, add 320/60 for higher monitor resolution
                #    if ((sqrt((((bubble[0]+(MAT/2)+320)-x)**2) + (((bubble[1]+(MAT/2)+60)-y)**2))) < 77):
                #        print "Bubble Detected, current speed: %f - %f"%(v,lastSampleTime)
                if ((sqrt((((bubble[0]+(MAT/2)+320)-x)**2) + (((bubble[1]+(MAT/2)+60)-y)**2))) < 77):
                    return bubble
    return random.choice(used_bubble) #if no fixation on bubble during trial_length

'''    
predict saccade end point
return bubble if in distance of diameter(MAT) of bubble center
'''    
def sacc_detection(el,used_bubble):
    
    #buffer for x coordiante, y coordinate, velocity
    bufferx, buffery, bufferv = deque(maxlen=3), deque(maxlen=3), deque(maxlen=4)
    start = pylink.currentTime()
    saccade = 0
    #start_time = []
    while (pylink.currentTime() - start) < TRIAL_LENGTH:
        i = el.getNextData()
        # wenn es etwas anderes ist als RAW_DATA(=200), naechster schleifendurchlauf
        if i!=200: continue
        # actuelle position direkt vom eye-tracker
        x, y = el.getNewestSample().getLeftEye().getGaze()
        bufferx.append(float(x))
        buffery.append(float(y))
        
        # Compute velocity in degrees per second
        bufferv.append(np.mean(((np.diff(np.array(bufferx))**2+np.diff(np.array(buffery))**2)**.5) * TRACKING_FREQ)/float(PPD))

        #saccade_onset
        if bufferv[-1] < 30:
            saccade = 0
            #check if sample already in next bubble
            for bubble in used_bubble:
                if ((sqrt((((bubble[0]+(MAT/2)+320)-x)**2) + (((bubble[1]+(MAT/2)+60)-y)**2))) < MAT/2):
                    el.trialmetadata('start_x', bufferx[-1])
                    el.trialmetadata('start_y', buffery[-1])
                    el.trialmetadata('start_velocity', bufferv[-1])
                    el.trialmetadata('end_x', bufferx[-1])
                    el.trialmetadata('end_y', buffery[-1])
                    el.trialmetadata('end_velocity', bufferv[-1])
                    el.trialmetadata('sacc_detection', 'start_in_bubble')
                    return bubble   
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
        if bufferv[-1] < 50 and saccade:
            for bubble in used_bubble:
                if ((sqrt((((bubble[0]+(MAT/2)+320)-x)**2) + (((bubble[1]+(MAT/2)+60)-y)**2))) < 2*MAT/3):
                    el.trialmetadata('end_x', bufferx[-1])
                    el.trialmetadata('end_y', buffery[-1])
                    el.trialmetadata('end_velocity', bufferv[-1])
                    el.trialmetadata('sacc_detection', 'pred_in_bubble')
                    return bubble    
                            
        #check if sample near bubble (in distance of 2 * radius MAT/2)
    #print "random bubble returned" 
    el.trialmetadata('sacc_detection', 'random')
    return random.choice(used_bubble) #if no prediction on bubble during trial_length
    
    
path_to_fixdur_files, path_to_fixdur_code = paths()

def debug_time(dispstr,start):
    print "%s : %.2f"%(dispstr,pygame.time.get_ticks()-start)
