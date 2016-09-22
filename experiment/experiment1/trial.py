# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 13:00:06 2014

@author: lkaufhol
"""

import numpy as np
import random
import pygame, sys, scipy, os, tools
from scipy import stats

try:
    import fixdur_tracker as tracker
    import pylink
except ImportError:
    print 'pylink and fixdur_tracker cannot be imported'

# get size of bubble in px from generate_stimuli.py
MAT = 154
# minimal distance between center of 2 bubbles = diameter of bubble, min_distance = MAT

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()


'''rate next poosible bubbles for display, based on current bubble, higher likeliehood for closer bubbles
return next bubble position'''
def choose_next_bubble(all_bubbles,chosen_bubble,remaining_bubbles,dist_mat):
    dist_to_current = np.empty(shape=(len(remaining_bubbles)))
    #print remaining_bubbles
    for bubble_pos in remaining_bubbles:
        dist_to_current[remaining_bubbles.index(bubble_pos)] = (dist_mat[all_bubbles.index((chosen_bubble)[0]),all_bubbles.index(bubble_pos)])
    weights = 1 - (dist_to_current-np.min(dist_to_current))/np.ptp(dist_to_current)
    weights = weights/sum(weights)
    custm = stats.rv_discrete(name='custm', values=(np.arange(len(remaining_bubbles)), weights))
    next_bubble_index = custm.rvs(size=1)
    next_bubble_pos = remaining_bubbles[next_bubble_index[0]]

    return next_bubble_pos   
       


'''generate individual stimuli for the trial'''
def get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat):
    #empty background
    #image = grayimage
    surf.fill((128,128,128))
    
    #remove previously fixated bubble from list    
    try:
        remaining_bubbles.remove(chosen_bubble[0])        
    except:
        pass
    #delete all bubbles that have overlap with chosen bubble from prev subtrial
    remove_from_remaining = [np.where(dist_mat[all_bubbles.index(chosen_bubble[0]),:] < MAT)]
    for item in remove_from_remaining[0][0]:
        if all_bubbles[item] in remaining_bubbles:
            remaining_bubbles.remove(all_bubbles[item])    
 
    #list to store bubbles used for current image
    used_bubbles = []
    if chosen_bubble == 'No bubble':
        #start with random single bubble images
        current_bubble_pos = random.choice(remaining_bubbles)
    else:
        # select bubble that is more likely closer to the previously fixated bubble
        current_bubble_pos = choose_next_bubble(all_bubbles,chosen_bubble,remaining_bubbles,dist_mat)
        #current_bubble_pos = random.choice(remaining_bubbles)
   
        
    used_bubbles.append(current_bubble_pos)
    #load current bubble
    current_bubble = loaded_bubbles[all_bubbles.index(current_bubble_pos)]
    # paste current bubble on background
    surf.blit(current_bubble,(current_bubble_pos[0]+320,current_bubble_pos[1]+60))
    more_bubbles = True
    if num_of_bubbles > 1:
        #delete all bubbles that have overlap with current bubble
        remove_from_remaining = [np.where(dist_mat[all_bubbles.index(current_bubble_pos),:] < MAT)]
        for item in remove_from_remaining[0][0]:
            if all_bubbles[item] in remaining_bubbles:
                remaining_bubbles.remove(all_bubbles[item])
        for a in range(num_of_bubbles-1):       
            # choose next bubble to add
            if not remaining_bubbles:
                    more_bubbles = False
                    print 'Warning: Ran out of bubbles!'
                    break
            else:
                if chosen_bubble == 'No bubble':
                    # select bubble that is more likely closer to the current_bubble
                    next_bubble_pos = choose_next_bubble(all_bubbles,[current_bubble_pos],remaining_bubbles,dist_mat)
                else:
                    # select bubble that is more likely closer to the previously fixated bubble
                    next_bubble_pos = choose_next_bubble(all_bubbles,chosen_bubble,remaining_bubbles,dist_mat)
                used_bubbles.append(next_bubble_pos)
                #delete all bubbles that have overlap with next bubble
                if num_of_bubbles > 2:
                    remove_from_remaining = [np.where(dist_mat[all_bubbles.index(next_bubble_pos),:] < MAT)]
                    for item in remove_from_remaining[0][0]:
                        if all_bubbles[item] in remaining_bubbles:
                            remaining_bubbles.remove(all_bubbles[item])
                # load an add next bubble images to image
                next_bubble = loaded_bubbles[all_bubbles.index(next_bubble_pos)]
                surf.blit(next_bubble,(next_bubble_pos[0]+320,next_bubble_pos[1]+60))

    return used_bubbles, more_bubbles    


''' display training trials'''    
def training(surf,el,memory_image,fix_cross):
    #training parameter
    rectXY = surf.get_rect()
    rectXY = (rectXY[2],rectXY[3])
    training_bubble_num = [1,2,3,4,5]

    training_images = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/')   
    bubble_image = training_images[0]
    trial_num = 1000
    
    for bubble_image in training_images:   
        
        #start with sequential trial
        # load all bubbles for chosen image
        remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image+'/'+bubble).convert_alpha())
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
        remaining_bubbles = list(all_bubbles)
        # load distance mat for chosen image
        dist_mat = np.load(path_to_fixdur_code+'distances/'+bubble_image+'.npy')
        chosen_bubble = 'No bubble'
        used_bubbles = []
    
        #wait for next trial
        surf.fill((128,128,128))
        pygame.draw.circle(surf,(50,205,50),(int(rectXY[0]/2),int(rectXY[1]/2)),10,5)
        pygame.display.update() 
        key = tools.wait_for_key()
        if (key.key == 27):
            pygame.quit()
            sys.exit()
    
        #drift correction
        surf.fill((128,128,128))
        surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        pygame.display.update() 
        #el.drift((rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        el.drift()       
        #keep displying fixation cross so it"s still present after ne calibration
        surf.fill((128,128,128))
        surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        pygame.display.update()
        #start trial
        el.start_trial()
        delay_time = np.random.normal(500,100)
        pygame.time.delay(int(delay_time))
        
        el.trial(trial_num)
        el.trialmetadata('BUBBLE_IMAGE',bubble_image)
       
        for subtrial in range(20):
            
            #choose starting bubble for first trial randomly
            if subtrial == 0:
                chosen_bubble = [random.choice(remaining_bubbles)]
                remaining_bubbles.remove(chosen_bubble[0])       
                rectMultiple = [pygame.Rect((rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1])+fix_cross.get_size()),pygame.Rect(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60,154,154)] # in the beginning we need to actually show a bubble, not hide them     
            
            #start displaying chosen bubble
            surf.fill((128,128,128))
            chosen_bubble_image = loaded_bubbles[all_bubbles.index(chosen_bubble[0])]   
            surf.blit(chosen_bubble_image,(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60))
            pygame.display.update(rectMultiple)
            bubble_display_start = pygame.time.get_ticks()
            
            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial == 0:
                tools.sacc_detection(el,chosen_bubble)
            
            #choice
            #how many bubbles should be displayed
            num_of_bubbles = random.choice(training_bubble_num)
            #load surface for choosing next fixation location
            used_bubble, more_bubbles = get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat)        
            # update used bubbles for whole trial   
            for bubble in used_bubble:
                used_bubbles.append(bubble)  
            # reset bubbles
            remaining_bubbles = list(all_bubbles)
            for bubble in remaining_bubbles:
                if bubble in used_bubbles:
                    remaining_bubbles.remove(bubble)
        
            #keep displaying choosen bubble until disp_time is over
            disp_time = scipy.random.exponential(300,1)
            bubble_display_time = 0
            while bubble_display_time < disp_time:
                pygame.time.delay(1)
                bubble_display_time = pygame.time.get_ticks() - bubble_display_start
                
            rects1 = [pygame.Rect(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60,154,154)]
            rectMultiple = []
            for l in range(len(used_bubble)):
                rectMultiple.append(pygame.Rect(used_bubble[l][0]+320,used_bubble[l][1]+60,154,154))
                
                
            # draw choice window onto the screen until saccade is over
            pygame.display.update(rects1+rectMultiple) # blit the currently fixated bubbles and all to be displayed bubbles.
            #fix_x,fix_y = tools.wait_for_saccade(el)
            chosen_bubble = tools.sacc_detection(el,used_bubble)
            #chosen_bubble = tools.get_fixated_bubble(used_bubble,fix_x,fix_y)            
            chosen_bubble = [chosen_bubble]
            
            rectMultiple = []
            for l in range(len(used_bubble)):
                if used_bubble[l][0] != chosen_bubble[0]:
                    rectMultiple.append(pygame.Rect(used_bubble[l][0]+320,used_bubble[l][1]+60,154,154))
            #metainfos for tracker
            el.trialmetadata("DISPLAYED_BUBBLES", used_bubble)
            el.trialmetadata("CHOSEN_BUBBLE", chosen_bubble)
            el.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
                        
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        surf.fill((128,128,128))
        memory_res = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf) 
        
        #wait for next trial
        surf.fill((128,128,128))
        pygame.draw.circle(surf,(50,205,50),(int(rectXY[0]/2),int(rectXY[1]/2)),10,5)
        pygame.display.update() 
        key = tools.wait_for_key()
        if (key.key == 27):
            pygame.quit()
            sys.exit()
    
        #drift correction
        surf.fill((128,128,128))
        surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        pygame.display.update() 
        el.drift()
        el.start_trial()
        delay_time = np.random.normal(500,100)
        pygame.time.delay(int(delay_time))        
        
        # all bubble displayed trial
        #load bubbles for memory task
        remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image+'/'+bubble).convert_alpha())
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
        remaining_bubbles = list(all_bubbles)
        #load and show stimulus
        img_num = random.randrange(0,10)
        img_num = random.randrange(31,46)
        stim = pygame.image.load(path_to_fixdur_files+'stimuli/multi_bubble_images/'+bubble_image+'/'+bubble_image+'_'+str(img_num)+'.png').convert()
        surf.blit(stim,(0,0))     
        pygame.display.update()
        pygame.time.delay(6000)         
        
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        surf.fill((128,128,128))        
        memory_res = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf) 
        el.end_trial()    



def get_image_debug(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat):
    #empty background
    #image = grayimage
    #surf.fill((128,128,128))
    #list to store bubbles used for current image

    try:
        remaining_bubbles.remove(chosen_bubble[0])
    except:
        pass
    #delete all bubbles that have overlap with chosen bubble from prev subtrial
    remove_from_remaining = [np.where(dist_mat[all_bubbles.index(chosen_bubble[0]),:] < MAT)]
    #print "First pass, remove the overlapping from previous bubble, %i found"%len(remove_from_remaining)
    #print remove_from_remaining
    for item in remove_from_remaining[0][0]:
        if all_bubbles[item] in remaining_bubbles:
            remaining_bubbles.remove(all_bubbles[item])
            
    used_bubbles = []
    if chosen_bubble == 'No bubble':
        #start with random single bubble images
        current_bubble_pos = random.choice(remaining_bubbles)
    else:
        # select bubble that is more likely closer to the previously fixated bubble
        current_bubble_pos = choose_next_bubble(all_bubbles,chosen_bubble,remaining_bubbles,dist_mat)
        #current_bubble_pos = random.choice(remaining_bubbles)
    #remove previously fixated bubble from list

    used_bubbles.append(current_bubble_pos)
    #load current bubble
    #current_bubble = loaded_bubbles[all_bubbles.index(current_bubble_pos)]
    # paste current bubble on background
    #surf.blit(current_bubble,(current_bubble_pos[0]+320,current_bubble_pos[1]+60))
    more_bubbles = True
    if num_of_bubbles > 1:
        #delete all bubbles that have overlap with current bubble
        remove_from_remaining = [np.where(dist_mat[all_bubbles.index(current_bubble_pos),:] < MAT)]
        for item in remove_from_remaining[0][0]:
            if all_bubbles[item] in remaining_bubbles:
                remaining_bubbles.remove(all_bubbles[item])
        #print "Second remove the overlapping from first selected bubble, %i found"%len(remove_from_remaining)
        #print remove_from_remaining
        for a in range(num_of_bubbles-1):       
            # choose next bubble to add
            if not remaining_bubbles:
                    more_bubbles = False
                    print 'Warning: Ran out of bubbles!'
                    break
            else:
                if chosen_bubble == 'No bubble':
                    # select bubble that is more likely closer to the current_bubble
                    next_bubble_pos = choose_next_bubble(all_bubbles,[current_bubble_pos],remaining_bubbles,dist_mat)
                else:
                    # select bubble that is more likely closer to the previously fixated bubble
                    next_bubble_pos = choose_next_bubble(all_bubbles,chosen_bubble,remaining_bubbles,dist_mat)
                used_bubbles.append(next_bubble_pos)
                #delete all bubbles that have overlap with next bubble
                if num_of_bubbles > 2:
                    remove_from_remaining = [np.where(dist_mat[all_bubbles.index(next_bubble_pos),:] < MAT)]
                    for item in remove_from_remaining[0][0]:
                        if all_bubbles[item] in remaining_bubbles:
                            remaining_bubbles.remove(all_bubbles[item])
                    #print "Further on, remove the overlapping from next selected bubble, %i found"%len(remove_from_remaining)
                    #print remove_from_remaining
                # load an add next bubble images to image
                #next_bubble = loaded_bubbles[all_bubbles.index(next_bubble_pos)]
                #surf.blit(next_bubble,(next_bubble_pos[0]+320,next_bubble_pos[1]+60))

    return used_bubbles, more_bubbles    
