# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 18:09:49 2015

@author: tracking
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:36:35 2015

@author: lkaufhol
"""

import pygame, sys, os, random, math, string, glob, pdb
import pylink
from psychopy import visual, core, event, monitors,logging
import numpy as np
import cPickle as pickle
import fixdur_tracker_psychopy as tracker
import trial_psychopy as trial
import tools_psychopy as tools
from collections import deque
from pygame.locals import *
# Stuff from Niklas(Aspen)
from pylink import openGraphicsEx
from eyelink_psychopy import EyeLinkCoreGraphicsOpenGL


#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()

NUM_OF_TRIALS =128
#NUM_OF_TRIALS =30 
TRIAL_TIME = 6000   #how long sould the bubbles in theory be displayed per trial for randomization
START_TRIAL = 126
     #which trial to begin with

#subject number to determine which multiple_bubble_images are shown, first subject 0
subject_number = raw_input("Please enter the subject NUMBER(0-20): ")
#subject_number = random.randint(0,9)
#subject = raw_input("Please enter a subject ID: ")
subject = subject_number
# load randomization for subject
cont = 'n'
while cont != 'y':
    if (os.path.exists(path_to_fixdur_code+'data/'+str(subject)+'/rand_'+str(subject)+'.npy')):
        a = raw_input('Randomization for subject '+str(subject)+' does already exist. Do you want to continue? (y/n)')
        if a == 'y':        
            trial_mat = np.load(path_to_fixdur_code+'data/'+str(subject)+'/rand_'+str(subject)+'.npy')
            cont = 'y'
        else:
            subject = raw_input("Please enter a subject ID: ")
    else:
        if not os.path.exists(path_to_fixdur_code+'data/'+str(subject)+'/'):
            os.mkdir(path_to_fixdur_code+'data/'+str(subject)+'/')
        trial_mat = tools.randomization(subject,TRIAL_TIME)
        print 'No randomization file found, created new one'
        cont = 'y'
    
# load all unique image names while keeping order of rand-file
# indexes = np.unique(trial_mat[:,0], return_index=True)[1]
# all_images = [trial_mat[:,0][index] for index in sorted(indexes)]
all_images = []
for image in trial_mat[:,0]:
    if not image in all_images:
        all_images.append(image)
        
# open_file for meta data
if START_TRIAL == 0:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject),'w')
else:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject)+str(START_TRIAL),'w')
    
#monitor information

# set up the window
rectXY = (1920,1080);
surf = visual.Window(size=rectXY,fullscr=True,winType = 'pygame')
#surf.setMouseVisible(False)
#surf.waitBlanking = False
#load images
memory_image = visual.SimpleImageStim(surf, image=path_to_fixdur_code+'images/memory.png')#,pos=(rectXY[0]/2,rectXY[1]/2))
fix_cross = visual.SimpleImageStim(surf,image=path_to_fixdur_code+'images/fixationcross.png')

# set up eyetracker
#pylink.openGraphics()
openGraphicsEx(EyeLinkCoreGraphicsOpenGL(surf))
rand_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
print rand_filename
#el = tracker.Tracker(surf,rand_filename+'.EDF')
#track = PsychoTracker(surf, rand_filename)
#track.set_calibration(13)
#el.setup()
#[] = 2
#start slide show
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/intro*.png')))
##el.setup()

# show fixation cross
fix_cross.draw(surf)
surf.flip()

#training trials
if START_TRIAL == 0:
	trial.training(surf,el,memory_image.copy(),fix_cross.copy())
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/pre_start.png')))

# show fixation cross
fix_cross.draw(surf)
surf.flip()

trial_num = 1
trial_list = []


####
#surf.setRecordFrameIntervals(True)
#surf._refreshTreshold=1/120.0+0.002
#logging.console.setLevel(logging.WARNING)

# run the game loop
for chosen_image in range(NUM_OF_TRIALS-START_TRIAL):
    
    #remove all trials that should be skipped
    if START_TRIAL !=0 and chosen_image == 0:
        for tr in range(0,START_TRIAL):
            all_images.pop(0)

    # start with first image
    bubble_image = all_images[0]
    #remove chosen image from all images
    all_images.pop(0)
    #get the trial corresponding to the image
    current_trial = trial_mat[np.where(trial_mat[:,0] == bubble_image)]
       
    #wait for next trial
    breaks = [28,48,68,88,108]
    breaks = [ x + START_TRIAL for x in breaks]
    if trial_num in breaks:
        text = visual.TextStim(surf, text=u"It's time for a break!")
        text.draw(surf)
    else:
        circ = visual.Circle(surf, radius=0.01)#, color = (128, 255, 128))
        circ.draw(surf)
    #pygame.display.update()
    surf.flip()
    
    #####
    #key = event.getKeys()
    #if 'escape' in key:
    #    surf.close()
    #    sys.exit()
    
    #drift correction
    fix_cross.draw(surf)
    surf.flip()
    #el.drift()####
    #keep displying fixation cross so it"s still present after ne calibration
    fix_cross.draw(surf)
    surf.flip()
    #start trial
#    el.start_trial()
    #normal_dist with mean 500 and spread 100 (ms)
    delay_time = np.random.uniform(300,700)
    #wait for n seconds
    #core.wait(int(delay_time/1000))####
    
    ''' if we have a trial where all bubbles are shown at once'''
    if current_trial[0][1] == 'all': 

        #load bubbles for memory task
        remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            x,y = tools.get_bubble_pos(bubble)
            #loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble).convert_alpha())
            loaded_bubbles.append(visual.SimpleImageStim(surf, image = path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble, pos = (x,y)))            
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
        remaining_bubbles = list(all_bubbles)
        
        # start trial
#        el.trial(trial_num)
        
        #load and show stimulus
        img_num = subject_number
        stim = visual.SimpleImageStim(surf, image=path_to_fixdur_files+'stimuli/multi_bubble_images/'+bubble_image+'/'+bubble_image+'_'+str(img_num)+'.png')
        stim.draw(surf)
        surf.flip()
        #core.wait(6)####
        
        #metainfos for tracker
#        el.trialmetadata('BUBBLE_IMAGE',bubble_image)
#        el.trialmetadata("forced_fix_onset", -1)
#        el.trialmetadata("stimulus_onset", -1)
#        el.trialmetadata("saccade_offset", -1)
#        el.trialmetadata("DISPLAYED_BUBBLES", -1)
#        el.trialmetadata("CHOSEN_BUBBLE", -1)
#        el.trialmetadata('BUBBLE_DISPLAY_TIME', 6000)
#             
        #fill meta_data
        subtrial_list = [{'trial': trial_num, 'img': bubble_image, 'img_num': img_num}]
    
    ''' if we have a regular trial where bubbles are shown sequentially'''
    if current_trial[0][1] == 'seq':

        # load all bubbles for chosen image
        remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            x,y = tools.get_bubble_pos(bubble)
            #loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble).convert_alpha())
            loaded_bubbles.append(visual.SimpleImageStim(surf, image = path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble, pos = (x,y)))            
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
        remaining_bubbles = list(all_bubbles)
        # load distance mat for chosen image
        dist_mat = np.load(path_to_fixdur_code+'distances/'+bubble_image+'.npy')
        chosen_bubble = 'No bubble'
        used_bubbles = []
    
        # start trial
        #        el.trial(trial_num)
        #        el.trialmetadata('BUBBLE_IMAGE',bubble_image)
                
        subtrial_num = 1
        subtrial_list = []   
        start = pygame.time.get_ticks()

        for subtrial in current_trial:
                        
            #choose starting bubble for first trial randomly
            if subtrial_num == 1:
                chosen_bubble = [random.choice(remaining_bubbles)]
                
                remaining_bubbles.remove(chosen_bubble[0])
                first_bubble = chosen_bubble[0]
                #rectMultiple = [pygame.Rect((rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1])+fix_cross.get_size()),pygame.Rect(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60,154,154)] # in the beginning we need to actually show a bubble, not hide them
            
            #start displaying chosen bubble  
            chosen_bubble_image = loaded_bubbles[all_bubbles.index(chosen_bubble[0])]   
            ##tools.debug_time("Bubble Loaded",start)

            #image.blit(chosen_bubble_image,(chosen_bubble[0][0],chosen_bubble[0][1]))
            ##tools.debug_time("Bubble Blitted",start)
            #surf.fill((128,128,128))
            #surf.blit(chosen_bubble_image,(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60))
            chosen_bubble_image.draw(surf)
            

            #surf.blit(image,(320,60))
            ##tools.debug_time("Forced Stim Blitted",start)
            
            start = pygame.time.get_ticks()
            #pygame.display.update(rectMultiple)
            surf.flip()
            bubble_display_start = pygame.time.get_ticks()
            tools.debug_time("Forced_stim_onset",start)
            #            el.trialmetadata("forced_fix_onset", bubble_display_start)


            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial_num == 1:
                pass
                # tools.sacc_detection(el,chosen_bubble)

            
            #choice
            #how many bubbles should be displayed
            num_of_bubbles = int(float(subtrial[2]))  
            #num_of_bubbles = 5
            ##tools.debug_time("pre_stim_gen",start)
            start = pygame.time.get_ticks()

            #load surface for choosing next fixation location
            used_bubble, more_bubbles = trial.get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat)                
            tools.debug_time("post_stim_gen",start)
        
            #keep displaying choosen bubble until disp_time is over
            disp_time = float(subtrial[3])
            disp_time = 50####
            
            bubble_display_time = 0
            while bubble_display_time < disp_time:
                pygame.time.delay(1)
                bubble_display_time = pygame.time.get_ticks() - bubble_display_start
                
            
            # draw choice window onto the screen until saccade is over


            

            start = pygame.time.get_ticks()
            surf.flip() # blit the currently fixated bubbles and all to be displayed bubbles.
            tools.debug_time("Time for second update",start)
            ##tools.debug_time("post_update",start)
            stimulus_onset = pygame.time.get_ticks()
            #            el.trialmetadata("stimulus_onset", stimulus_onset)
            #fix_x,fix_y = tools.wait_for_saccade(el)
            
            chosen_bubble= used_bubble[0]#= tools.sacc_detection(el,used_bubble)
                        
            ##start = pygame.time.get_ticks()
            
            saccade_offset = pygame.time.get_ticks()
            #            el.trialmetadata("saccade_offset", saccade_offset)
            
            
        
            #chosen_bubble = tools.get_fixated_bubble(used_bubble,fix_x,fix_y)            
            chosen_bubble = [chosen_bubble]
            
            # update used bubbles for whole trial   
            used_bubbles.append(chosen_bubble[0])  
            
            # reset bubbles
            remaining_bubbles = list(all_bubbles)
            # remove bubbles alreadz shown in trial
            for bubble in used_bubbles:
                remaining_bubbles.remove(bubble)
            remaining_bubbles.remove(first_bubble)
    
            #metainfos for tracker
            #            el.trialmetadata("DISPLAYED_BUBBLES", used_bubble)
            #            el.trialmetadata("CHOSEN_BUBBLE", chosen_bubble)
            #            el.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
                
            key = event.getKeys()
            if 'escape' in key:
                surf.close()
                sys.exit()
    
            #metainfos for dictionary        
            subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_bubble, 'first_bubble':first_bubble, 'chosen_bubble': chosen_bubble, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}                
            subtrial_list.append(subtrial_dict)  
            
            subtrial_num = subtrial_num + 1
            #tools.debug_time("end of trial - time after wait for fix",start)
            
    #memory task
    #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
    #memory_res = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)    
    memory_res = [-1,-1,-1];####
    #add trial meta data    
    trial_list.append(subtrial_list)
    #memory_res has order correct, left, right -> wrong in dict, but corrected for in analysis
    trial_list.append({'subject_number':subject_number, 'trial_type':current_trial[0][1], 'left_bubble':memory_res[0], 'right_bubble':memory_res[1], 'correct':memory_res[2]})
    trial_num = trial_num + 1      
#    el.end_trial() 

#final screen
ending = visual.SimpleImageStim(surf, path_to_fixdur_code+'images/instructions/ending.png')
ending.draw()
surf.flip()
core.wait(6)
surf.close()
   
#write metadata into file
pickle.dump(trial_list,subject_file)
subject_file.close()

#import pylab
#pylab.plot(surf.frameIntervals)
#pylab.show()

el.finish()
os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')

if os.path.exists('/home_local/tracking/experiments/fixdur/'):
	os.system('cp -r /home_local/tracking/experiments/fixdur/expcode/data/'+str(subject)+'/ /home_local/tracking/experiments/fixdur/data/'+str(subject)+'/')
#sys.exit()
