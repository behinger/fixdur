# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 13:00:06 2014
@author: lkaufhol
"""

import numpy as np
import random
import tools_extended as tools_ex
import sys, scipy, os, tools
from scipy import stats
from psychopy import visual, core, event
from PIL import Image

EYETRACKING = False

try:
    if EYETRACKING:    
        import fixdur_tracker
        import pylink
except ImportError:
    print 'pylink and fixdur_tracker cannot be imported'



# get size of bubble in px from generate_stimuli.py
MAT = 154
# minimal distance between center of 2 bubbles = diameter of bubble, min_distance = MAT

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()


''' display training trials'''    
def training(surf,tracker,memory_image,fix_cross,stimuli,gausStim,EYETRACKING,control):
    
    #training parameter
    #training_bubble_num = [0,2,4,8,16] # number of bubbles for training
    num_trials = 2 # number of trials for training
    num_subtrials = 20 # number of subtrials per trial
    image_size = (1280,960)
    
    # choose randomly as many images as number of training trials
    training_stimuli_keys = np.random.choice(stimuli.keys(),num_trials,replace=False)   
    #bubble_image = training_images[0]
    trial_num = 1000
    
    # create white stimulus
    white_image = Image.new('L',image_size,150)
    stimWhite = visual.ImageStim(surf, image=white_image, units='pix')
    
    # create control_list such that in half of the cases control condition is applied
    #control_list = np.ones(num_trials)
    #control_list[len(control_list)/2:] = 0
    
    # random order of trials with and without control condition
    #np.random.shuffle(control_list)
        
    
    for num,current_key in enumerate(training_stimuli_keys):
        
        # save in a variable if control condition is applied in this trial or not        
        #control = control_list[num]        
        
        # save the name of the current image in a variable
        bubble_image = current_key
        
        # find stimulus to current key (image)
        current_stim = stimuli[current_key]
        
        # Sample bubble locations for current image from Poisson distribution
        width, height = current_stim.size
        sample_points = tools_ex.poisson_sampling(width,height)
        
        # draw and show white circle
        circ = visual.Circle(surf, units='pix', radius=10)
        circ.draw(surf)
        surf.flip()

        # exit function via escape
        key = event.waitKeys()
        if ('escape' in key):
            surf.close()
            sys.exit()
         
        # show fixation cross and apply drift correction
        fix_cross.draw(surf)
        surf.flip()
        if EYETRACKING == True:        
            tracker.drift() 
            
        #keep displaying fixation cross after new calibration
        fix_cross.draw(surf)
        surf.flip()
        
        #start trial (eye-tracker)
        if EYETRACKING == True:
            tracker.start_trial()
        
        #normal_dist with mean 300 and spread 700
        delay_time = np.random.uniform(300,700)
        # wait delay time
        core.wait(int(delay_time/1000))
        
        # record meta-data for tracker
        if EYETRACKING == True:
            tracker.trial(trial_num)
            tracker.trialmetadata('BUBBLE_IMAGE',bubble_image)
        
        # default: enable memory task
        memory = True 
        whole_image = False
        
        # copy in which already used locations can be deleted
        remaining_points = list(sample_points)
        for subtrial in range(num_subtrials):
            
            # for first subtrial choose location randomly from sample_points
            if subtrial == 0:
                chosen_location = [random.choice(sample_points)]
                
                if control == 1:
                    memory = False
            
        
            
            # delete previous location for next subtrial
            if chosen_location[0] in remaining_points:
                remaining_points.remove(chosen_location[0])
            
            # draw stimulus without mask
            current_stim.mask = None
            current_stim.draw()
            
            # move mask to chosen_location
            tools_ex.create_mask_fast(chosen_location,surf,gausStim)
            
            
            # if control condition is applied
            if control == 1 and subtrial != 0:
                
                surf.flip()             
                bubble_display_start = core.getTime()
            
                #display time for white bubble (gaussian with mean 400 ms and sd 50 ms)
                white_disp = np.random.normal(400,50)
                
                # find a different image
                new_image = random.choice(stimuli.keys())
                while new_image == bubble_image:
                    new_image = random.choice(stimuli.keys())
               
                # draw white stimulus with mask at chosen_location
                stimWhite.draw()
                tools_ex.create_mask_fast(chosen_location,surf,gausStim)
                
                ###################
                ### Wait 200ms with current foveated
                ###################                              
                curr_display_time = 0
                while curr_display_time < 200/1000.:
                    core.wait(0.001)                    
                    curr_display_time = core.getTime() - bubble_display_start
                
                #flip to white stimulus
                surf.flip()
                display_start = core.getTime()
                
                # draw new image with mask at chosen location
                current_stim = stimuli[new_image]
                current_stim.mask = None
                current_stim.draw()
                tools_ex.create_mask_fast(chosen_location,surf,gausStim)
                
                # display white bubble for white_disp time
                curr_display_time = 0
                while curr_display_time < white_disp/1000:
                    core.wait(0.001)                    
                    curr_display_time = core.getTime() - display_start
                    
            #################################
            ### Show A Single Foveated Bubble
            ################################
            surf.flip()
            bubble_display_start = core.getTime()
            #if EYETRACKING == True:                
            #    tracker.trialmetadata("forced_fix_onset", bubble_display_start)
        
            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial == 0:
                if EYETRACKING:
                    tools.sacc_detection(tracker,chosen_location,False,surf,chosen_location[0],remaining_points)            
            
            # get number of bubbles for current subtrial
            if control == 1:
                num_of_bubbles = random.choice([1,2,3,4,5])
            else:
                num_of_bubbles = random.choice([0,1,2,4,8,16])
            
            # if num_of_bubbles == 0 apply whole image condition
            if num_of_bubbles == 0:
                mask_im = tools_ex.whole_image(chosen_location)
                used_locations = []
                whole_image = True
            
            # choose bubble locations according to num of bubbles
            else:
                bubble_locations = tools_ex.choose_locations(whole_image,num_of_bubbles, sample_points, remaining_points, chosen_location)          
                mask_im = tools_ex.create_mask(bubble_locations)
                used_locations = []
                [used_locations.append(location) for location in bubble_locations]
                whole_image = False
            #tools.debug_time("choose new bubble locations ",start)
            #start = core.getTime()
            # prepare stimulus for alternative bubble(s)
            #stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
            current_stim.mask = mask_im
            #tools.debug_time("stim.mask",start)
            #start = core.getTime()
            
            #draw sample for forced fixation time
            disp_time = scipy.random.exponential(295,1)
           
            # draw alternative bubble(s)
            current_stim.draw()
            
            ###################
            ## Wait FORCED FIXATION TIME
            ###################
            
            #keep displaying choosen bubble until disp_time is over
            bubble_display_time = 0
            while bubble_display_time < disp_time/1000.:
                core.wait(0.001)                    
                bubble_display_time = core.getTime() - bubble_display_start
                
            
            ###################
            ## Show Alternative Bubbles
            ###################
            surf.flip()
            
            #stimulus_onset = core.getTime()
            #if EYETRACKING == True:
            #    tracker.trialmetadata("stimulus_onset", stimulus_onset)

            if EYETRACKING:
                chosen_location = [tools.sacc_detection(tracker,used_locations,whole_image,surf, chosen_location[0],remaining_points)]
            else:
                if num_of_bubbles == 0:
                    copy_points = list(sample_points)
                    copy_points.remove(chosen_location[0])
                    chosen_location = [random.choice(copy_points)]
                else:
                    chosen_location = [random.choice(bubble_locations)]
            
            #saccade_offset = core.getTime()
            #if EYETRACKING == True:
            #    tracker.trialmetadata("saccade_offset", saccade_offset)
                
            #metainfos for tracker
            if EYETRACKING == True:
                tracker.trialmetadata("DISPLAYED_BUBBLES", used_locations)
                tracker.trialmetadata("CHOSEN_BUBBLE", chosen_location)
                tracker.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
        
            key = tools.wait_for_key()
            if 'escape' in key:
                surf.close()
                sys.exit()
        
        # show memory task if control is false        
        if memory:
            memory_res = tools_ex.memory_task(current_stim,memory_image,surf,stimuli,bubble_image)
            
        # increase trial_num
        trial_num = trial_num + 1
        
        if EYETRACKING == True:       
            tracker.end_trial() 
            
        


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

