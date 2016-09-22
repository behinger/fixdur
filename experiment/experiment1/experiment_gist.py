import pygame, sys, os, random, math, string, glob, pdb
import pylink
import numpy as np
import cPickle as pickle
import fixdur_tracker as tracker
import trial_gist as trial
import tools_gist as tools
from collections import deque
from os.path import normpath as pN
import codecs
from pygame.locals import *

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()

NUM_OF_TRIALS =128
#NUM_OF_TRIALS =5 
TRIAL_TIME = 6000   #how long sould the bubbles in theory be displayed per trial for randomization
START_TRIAL = 0     #which trial to begin with   
fullscreen = True   


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
#print trial_mat[1:100,4]
#raise(Exception)
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

# set up the window
pygame.init()

rectXY = (1920,1080);

flags = pygame.FULLSCREEN |  pygame.RLEACCEL | pygame.HWSURFACE
surf = pygame.display.set_mode(rectXY, flags, 32)
if fullscreen == False:
    surf = pygame.display.set_mode(rectXY, 0, 32)
pygame.mouse.set_visible(False)

memory_image = pygame.image.load(path_to_fixdur_code+'images/memory.png').convert_alpha()

# set up eyetracker
pylink.openGraphics()
rand_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
print rand_filename
el = tracker.Tracker(surf,rand_filename+'.EDF')

#start slide show
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/intro*.png')))
el.setup()

# show fixation cross
fix_cross = pygame.image.load(path_to_fixdur_code+'images/fixationcross.png').convert()
surf.fill((128,128,128))
#surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
pygame.display.update()

#training trials
if START_TRIAL == 0:
   trial.training(surf,el,memory_image.copy(),fix_cross.copy())
surf.fill((128,128,128))
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/pre_start.png')))

# show fixation cross
surf.fill((128,128,128))
surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
pygame.display.update()

trial_num = 1
trial_list = []

# run the game loop
for chosen_image in range(NUM_OF_TRIALS-START_TRIAL):
    
    try:
    
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
        surf.fill((128,128,128))
        breaks = [28,48,68,88,108]
        breaks = [ x + START_TRIAL for x in breaks]
        if trial_num in breaks:
            myfont = pygame.font.Font(None,52)
            text = myfont.render("It's time for a break!", 1, (10,10,10))
            textpos = text.get_rect()
            textpos.centerx = surf.get_rect().centerx
            textpos.centery = surf.get_rect().centery
            surf.blit(text,textpos)
        else:
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
        #keep displying fixation cross so it"s still present after ne calibration
        surf.fill((128,128,128))
        surf.blit(fix_cross,(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1]))
        pygame.display.update()
        #start trial
        el.start_trial()
        #el.drift(rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1])
        #normal_dist with mean 500 and spread 100
        delay_time = np.random.uniform(300,700)
        pygame.time.delay(int(delay_time))
        
        ''' if we have a trial where all bubbles are shown at once'''
        if current_trial[0][1] == 'all': 
    
            #load bubbles for memory task
            remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
            all_bubbles = []
            loaded_bubbles = []
            for bubble in remaining_bubbles:
                loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble).convert_alpha())
                all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
            remaining_bubbles = list(all_bubbles)
            
            # start trial
            el.trial(trial_num)
            
            #load and show stimulus
            img_num = subject_number
            stim = pygame.image.load(path_to_fixdur_files+'stimuli/multi_bubble_images/'+bubble_image+'/'+bubble_image+'_'+str(img_num)+'.png').convert()
            
            tools.full_image_load(surf,current_trial,path_to_fixdur_files,bubble_image)
            
            surf.blit(stim,(0,0))
            pygame.display.update()
            
            pygame.time.delay(6000)
            
            #metainfos for tracker
            el.trialmetadata('BUBBLE_IMAGE',bubble_image)
            el.trialmetadata("forced_fix_onset", -1)
            el.trialmetadata("stimulus_onset", -1)
            el.trialmetadata("saccade_offset", -1)
            el.trialmetadata("DISPLAYED_BUBBLES", -1)
            el.trialmetadata("CHOSEN_BUBBLE", -1)
            el.trialmetadata('BUBBLE_DISPLAY_TIME', 6000)
            el.trialmetadata('GIST',current_trial[0][4])    
            #fill meta_data
            subtrial_list = [{'trial': trial_num, 'img': bubble_image, 'img_num': img_num}]
        
        ''' if we have a regular trial where bubbles are shown sequentially'''
        if current_trial[0][1] == 'seq':
    
            # load all bubbles for chosen image
            remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
            all_bubbles = []
            loaded_bubbles = []
            for bubble in remaining_bubbles:
                loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble).convert_alpha())
                all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
            remaining_bubbles = list(all_bubbles)
            # load distance mat for chosen image
            dist_mat = np.load(path_to_fixdur_code+'distances/'+bubble_image+'.npy')
            chosen_bubble = 'No bubble'
            used_bubbles = []
        
            # start trial
            el.trial(trial_num)
            el.trialmetadata('BUBBLE_IMAGE',bubble_image)
            el.trialmetadata('GIST',current_trial[0][4])
            subtrial_num = 1
            subtrial_list = []   
            
            ##start = pygame.time.get_ticks()
            tools.full_image_load(surf,current_trial,path_to_fixdur_files,bubble_image)
            
            surf.fill((128,128,128))
            pygame.display.update()
            
            for subtrial in current_trial:
                            
                #choose starting bubble for first trial randomly
                if subtrial_num == 1:
                    
                    chosen_bubble = [random.choice(remaining_bubbles)]
                    
                    remaining_bubbles.remove(chosen_bubble[0])
                    first_bubble = chosen_bubble[0]
                    rectMultiple = [pygame.Rect((rectXY[0]/2-(np.array(fix_cross.get_size())/2)[0],rectXY[1]/2-(np.array(fix_cross.get_size())/2)[1])+fix_cross.get_size()),pygame.Rect(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60,154,154)] # in the beginning we need to actually show a bubble, not hide them
                    rectMultipleLasttrial = rectMultiple
                
                #start displaying chosen bubble  
                chosen_bubble_image = loaded_bubbles[all_bubbles.index(chosen_bubble[0])]   
                ##tools.debug_time("Bubble Loaded",start)
    
                #image.blit(chosen_bubble_image,(chosen_bubble[0][0],chosen_bubble[0][1]))
                ##tools.debug_time("Bubble Blitted",start)
                surf.fill((128,128,128))
                surf.blit(chosen_bubble_image,(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60))
    
                #surf.blit(image,(320,60))
                ##tools.debug_time("Forced Stim Blitted",start)
                
                ##start = pygame.time.get_ticks()
                pygame.display.update(rectMultiple+rectMultipleLasttrial)
                bubble_display_start = pygame.time.get_ticks()
                ##tools.debug_time("Forced_stim_onset",start)
                el.trialmetadata("forced_fix_onset", bubble_display_start)
                rectMultipleLasttrial = rectMultiple
    
    
                # wait until first bubble is fixated before starting forced_fix_time
                if subtrial_num == 1:
                     tools.sacc_detection(el,chosen_bubble)
    
                
                #choice
                #how many bubbles should be displayed
                num_of_bubbles = int(float(subtrial[2]))  
                #num_of_bubbles = 5
                #tools.debug_time("pre_stim_gen",start)
                #load surface for choosing next fixation location
                used_bubble, more_bubbles = trial.get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat)                
                #tools.debug_time("post_stim_gen",start)
            
                #keep displaying choosen bubble until disp_time is over
                disp_time = float(subtrial[3])
                #disp_time = 50
                
                bubble_display_time = 0
                while bubble_display_time < disp_time:
                    pygame.time.delay(1)
                    bubble_display_time = pygame.time.get_ticks() - bubble_display_start
                    
                #start = pygame.time.get_ticks()
                
                # draw choice window onto the screen until saccade is over
    
                rects1 = [pygame.Rect(chosen_bubble[0][0]+320,chosen_bubble[0][1]+60,154,154)]
                rectMultiple = []
                for l in range(len(used_bubble)):
                    rectMultiple.append(pygame.Rect(used_bubble[l][0]+320,used_bubble[l][1]+60,154,154))
                
                ##start = pygame.time.get_
                pygame.display.update(rects1+rectMultiple) # blit the currently fixated bubbles and all to be displayed bubbles.
                ##tools.debug_time("Time for second update",start)
                ##tools.debug_time("post_update",start)
                stimulus_onset = pygame.time.get_ticks()
                el.trialmetadata("stimulus_onset", stimulus_onset)
                #fix_x,fix_y = tools.wait_for_saccade(el)
                
                chosen_bubble = tools.sacc_detection(el,used_bubble)
                            
                #start = pygame.time.get_ticks()
                
                saccade_offset = pygame.time.get_ticks()
                el.trialmetadata("saccade_offset", saccade_offset)
                
                #update only the bubbles that were not chosen
                #rectMultiple = []
                #for l in range(len(used_bubble)):
                #    if used_bubble[l][0] != chosen_bubble[0]:
                #        rectMultiple.append(pygame.Rect(used_bubble[l][0]+320,used_bubble[l][1]+60,154,154))
            
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
                el.trialmetadata("DISPLAYED_BUBBLES", used_bubble)
                el.trialmetadata("CHOSEN_BUBBLE", chosen_bubble)
                el.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
        
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            pygame.event.post(pygame.event.Event(QUIT))
        
                #metainfos for dictionary        
                subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_bubble, 'first_bubble':first_bubble, 'chosen_bubble': chosen_bubble, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}                
                subtrial_list.append(subtrial_dict)  
                
                subtrial_num = subtrial_num + 1
                ##tools.debug_time("end of trial - time after wait for fix",start)
                
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        memory_res = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)    
        
        #add trial meta data    
        trial_list.append(subtrial_list)
        #memory_res has order correct, left, right -> wrong in dict, but corrected for in analysis
        trial_list.append({'subject_number':subject_number, 'trial_type':current_trial[0][1], 'left_bubble':memory_res[0], 'right_bubble':memory_res[1], 'correct':memory_res[2],'gist':current_trial[0][4]})
        trial_num = trial_num + 1      
        el.end_trial() 
        
    except Exception as e:
        print type(e)
        print e
        try:
            error_file = open(path_to_fixdur_code+'data/'+str(subject)+'/error_'+str(trial_num)+'_'+str(subtrial),'w')
            error_file.write('ERROR')
            error_file.close()
        except:
            pickle.dump(trial_list,subject_file)
            subject_file.close()
            el.finish()
            os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')
            pygame.quit()
        

#final screen
ending = pygame.image.load(path_to_fixdur_code+'images/instructions/ending.png')
surf.fill((128,128,128))
surf.blit(ending,(0,0))
pygame.display.update()
   
#write metadata into file
pickle.dump(trial_list,subject_file)
subject_file.close()


el.finish()
os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')

pygame.quit()
if os.path.exists('/home_local/tracking/experiments/fixdur_gist/'):
    os.system('cp -r /home_local/tracking/experiments/fixdur_gist/expcode/data/'+str(subject)+'/ /home_local/tracking/experiments/fixdur_gist/data_gist/'+str(subject)+'/')
#sys.exit()
