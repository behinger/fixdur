# import modules
import sys, os, random, math, string, glob, pdb, re
from psychopy import visual, core, event, monitors,logging
import numpy as np
import cPickle as pickle
import trial, tools
import tools_extended as tools_ex
from PIL import Image


#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()


NUM_OF_TRIALS =128
#NUM_OF_TRIALS =5 
TRIAL_TIME = 6000   #how long sould the bubbles in theory be displayed per trial for randomization
START_TRIAL = 1    #which trial to begin with   
#fullscreen = True   
fullscreen = False
EYETRACKING = False

if EYETRACKING == False:
    el = None;
else:
    import pylink
    import fixdur_tracker as tracker

#subject number to determine which multiple_bubble_images are shown, first subject 0
subject_number = raw_input("Please enter the subject NUMBER(31-45): ")
#subject_number = 30
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
  
# own list for images (keep order of rand-file)
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
rectXY = (1920,1080);
surf = visual.Window(size=rectXY,fullscr=False,winType = 'pyglet', screen=1, units='pix')
surf.setMouseVisible(False)

# load memory image
memory_image = visual.SimpleImageStim(surf, image=path_to_fixdur_code+'images/memory.png')

# set up eyetracker
rand_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
print rand_filename
if EYETRACKING:
    pylink.openGraphics()
    el = tracker.Tracker(surf,rand_filename+'.EDF')

#start slide show
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/intro*.png')))
if EYETRACKING:
    el.setup()

# show fixation cross
fix_cross = visual.SimpleImageStim(surf,image=path_to_fixdur_code+'images/fixationcross.png')
#fix_cross.draw(surf)
surf.flip()

#training trials
if START_TRIAL == 0:
	trial.training(surf,el,memory_image,fix_cross)
 
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/pre_start.png')))

# show fixation cross
fix_cross.draw(surf)
surf.flip()


trial_num = 0
trial_list = []

# notwendig?
#surf.setRecordFrameIntervals(True)
#surf._refreshTreshold=1/120.0+0.002
#logging.console.setLevel(logging.WARNING)

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
           
        # breaks (wait for next trial)
        breaks = [28,48,68,88,108]
        breaks = [ x + START_TRIAL for x in breaks]
        if trial_num in breaks:
            text = visual.TextStim(surf, text=u"It's time for a break!")
            text.draw(surf)
        else:
            circ = visual.Circle(surf, units='pix', radius=10)
            circ.draw(surf)
 
        surf.flip()
        key = event.waitKeys()
        #key = tools.wait_for_key()
        print 'key',key
        if ('escape' in key):
            surf.close()
            sys.exit()
        
        #drift correction
        fix_cross.draw(surf)
        surf.flip()  
        if EYETRACKING == True:
            el.drift()
            
        #keep displying fixation cross so it is still present after new calibration
        fix_cross.draw(surf)
        surf.flip()
            
        #start trial (eye-tracker)
        if EYETRACKING == True:
            el.start_trial()

        #normal_dist with mean 500 and spread 100
        delay_time = np.random.uniform(300,700)
        core.wait(int(delay_time/1000))
        
        # New Part
        
        # Find and load image (with regular expression)
        p_noise = re.compile('noise') #define pattern for pattern matching
        if p_noise.match(bubble_image) != None:
            image = Image.open(path_to_fixdur_files+'stimuli/noise/post_shine/'+bubble_image)
        else:
            image = Image.open(path_to_fixdur_files+'stimuli/urban/'+bubble_image)
            # convert image to grayscale
            image = image.convert('L')
        
        # Sample bubble locations for current image from Poisson distribution
        width, height = image.size
        sample_points = tools_ex.poisson_sampling(width,height)
        
        # start trial
        if EYETRACKING == True:            
           el.trial(trial_num)
           el.trialmetadata('BUBBLE_IMAGE',bubble_image)
        
        subtrial_num = 1        
        used_locations = []        
        
        for subtrial in current_trial:
            #choose starting bubble for first trial randomly
            if subtrial_num == 1:
                chosen_location = [random.choice(sample_points)]

            # make a list of used locations to delete them for the next subtrial                
            used_locations.append(chosen_location[0])
            
            # create mask image for first bubble
            mask_im = tools_ex.create_mask(chosen_location)
            
            # show (only) chosen bubble
            stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
            stim.draw()
            surf.flip()
            
            bubble_display_start = core.getTime()
            if EYETRACKING == True:                
                el.trialmetadata("forced_fix_onset", bubble_display_start)
            
            # wait until first bubble is fixated before starting forced_fix_time
            #if subtrial_num == 1:
            #    if EYETRACKING:
            #        tools.sacc_detection(el,chosen_location)            
            
            # get number of bubbles for current trial
            num_of_bubbles = int(float(subtrial[1]))
            
            if num_of_bubbles == 0:
                mask_im = tools_ex.whole_image(chosen_location)
            
            # choose bubble locations according to num of bubbles
            else:
                bubble_locations = tools_ex.choose_locations(num_of_bubbles, sample_points, chosen_location)          
                mask_im = tools_ex.create_mask(bubble_locations)
                used_locations.append(bubble_locations)
        
            # prepare stimulus for alternative bubble(s)
            stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
            
            disp_time = float(subtrial[2])
            #keep displaying choosen bubble until disp_time is over
            bubble_display_time = 0
            while bubble_display_time < disp_time/1000:
                core.wait(0.001)                    
                bubble_display_time = core.getTime() - bubble_display_start
                
            # show alternative bubble(s)
            stim.draw()
            surf.flip()
            
            stimulus_onset = core.getTime()
            if EYETRACKING == True:
                el.trialmetadata("stimulus_onset", stimulus_onset)

 #           if EYETRACKING:
 #               chosen_bubble = tools.sacc_detection(el,used_bubble)
 #           else:
            if num_of_bubbles == 0:
                copy_points = list(sample_points)
                copy_points.remove(chosen_location[0])
                chosen_location = [random.choice(copy_points)]
            else:
                chosen_location = [random.choice(bubble_locations)]
                            
                
            saccade_offset = core.getTime()
            if EYETRACKING == True:
                el.trialmetadata("saccade_offset", saccade_offset)
                
            for location in used_locations:
                if location in sample_points:                
                    sample_points.remove(location)
                
            #metainfos for tracker
            #if EYETRACKING == True:
            #    el.trialmetadata("DISPLAYED_BUBBLES", used_bubble)
            #    el.trialmetadata("CHOSEN_BUBBLE", chosen_bubble)
            #    el.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
        
            key = tools.wait_for_key()
            if 'escape' in key:
                surf.close()
                sys.exit()
        
            #metainfos for dictionary        
            #subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_bubble, 'first_bubble':first_bubble, 'chosen_bubble': chosen_bubble, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}                
            #subtrial_list.append(subtrial_dict)  
            
            subtrial_num = subtrial_num + 1
        
        ''' if we have a regular trial where bubbles are shown sequentially 
        # load all bubbles for chosen image
        remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            x,y = tools.get_bubble_pos(bubble)
            loaded_bubbles.append(visual.SimpleImageStim(surf, image = path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble, pos = (x,y)))
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
            
        remaining_bubbles = list(all_bubbles)
            
        # load distance mat for chosen image
        dist_mat = np.load(path_to_fixdur_code+'distances/'+bubble_image+'.npy')
        chosen_bubble = 'No bubble'
        used_bubbles = []
        
        # start trial
        if EYETRACKING == True:            
            el.trial(trial_num)
            el.trialmetadata('BUBBLE_IMAGE',bubble_image)
            
        subtrial_num = 1
        subtrial_list = []   
            
        # notwendig?
        #start = psychopy.core.getTime()
           
        for subtrial in current_trial:
                            
            #choose starting bubble for first trial randomly
            if subtrial_num == 1:
                chosen_bubble = [random.choice(remaining_bubbles)]

                    
                remaining_bubbles.remove(chosen_bubble[0])
                first_bubble = chosen_bubble[0]
                 
                
            #start displaying chosen bubble  
            chosen_bubble_image = loaded_bubbles[all_bubbles.index(chosen_bubble[0])]
                
            # notwendig?                
            #tools.debug_time("Bubble Loaded",start)
    
            chosen_bubble_image.draw(surf)
                
            # notwendig?
            #start = psychopy.core.getTime()
            surf.flip()
            bubble_display_start = core.getTime()

            # notwendig?
            #tools.debug_time("Forced_stim_onset",start)
            if EYETRACKING == True:                
                el.trialmetadata("forced_fix_onset", bubble_display_start)
    
            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial_num == 1:
                if EYETRACKING:
                    tools.sacc_detection(el,chosen_bubble)
    
            #how many bubbles should be displayed
            num_of_bubbles = int(float(subtrial[1]))  
                
            #notwendig?
            #start = psychopy.core.getTime()                
                
            #new part: whole image condition
            #if num_of_bubbles == 0:
            #    tools_ex.whole_image(surf,bubble_image,chosen_bubble)
                
            #load surface for choosing next fixation location
            used_bubble, more_bubbles = trial.get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,num_of_bubbles,dist_mat)             
            #tools.debug_time("post_stim_gen",start)
            
            #keep displaying choosen bubble until disp_time is over
            disp_time = float(subtrial[2])
            #disp_time = 50
                
            bubble_display_time = 0
            while bubble_display_time < disp_time/1000:
                core.wait(0.001)                    
                bubble_display_time = core.getTime() - bubble_display_start
                    
                
            # draw choice window onto the screen until saccade is over
    
            #notwendig?
            #start = psychopy.core.getTime()
    
                
            surf.flip()
                
            #tools.debug_time("Time for second update",start)
            ##tools.debug_time("post_update",start)
            stimulus_onset = core.getTime()
            if EYETRACKING == True:
                el.trialmetadata("stimulus_onset", stimulus_onset)
            #fix_x,fix_y = tools.wait_for_saccade(el)
            if EYETRACKING:
                chosen_bubble = tools.sacc_detection(el,used_bubble)
            else:
                chosen_bubble = random.choice(used_bubble)
                            
                
            saccade_offset = core.getTime()
            if EYETRACKING == True:
                el.trialmetadata("saccade_offset", saccade_offset)

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
            if EYETRACKING == True:
                el.trialmetadata("DISPLAYED_BUBBLES", used_bubble)
                el.trialmetadata("CHOSEN_BUBBLE", chosen_bubble)
                el.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
        
            key = tools.wait_for_key()
            if 'escape' in key:
                surf.close()
                sys.exit()
        
            #metainfos for dictionary        
            subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_bubble, 'first_bubble':first_bubble, 'chosen_bubble': chosen_bubble, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}                
            subtrial_list.append(subtrial_dict)  
                
            subtrial_num = subtrial_num + 1 '''
            ##tools.debug_time("end of trial - time after wait for fix",start)
                
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        memory_res = tools_ex.memory_task(image,memory_image,surf)    
        
        #add trial meta data    
        trial_list.append(subtrial_list)
        #memory_res has order correct, left, right -> wrong in dict, but corrected for in analysis
        trial_list.append({'subject_number':subject_number,'left_bubble':memory_res[0], 'right_bubble':memory_res[1], 'correct':memory_res[2]})
        trial_num = trial_num + 1   
        
        if EYETRACKING == True:       
            el.end_trial() 
        
    except Exception as e:
        print e.message,e.args
        try:
            error_file = open(path_to_fixdur_code+'data/'+str(subject)+'/error_'+str(trial_num)+'_'+str(subtrial),'w')
            error_file.write('ERROR')
            error_file.close()
        except:
            pickle.dump(trial_list,subject_file)
            subject_file.close()
            if EYETRACKING == True:
                el.finish()
            os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')
            surf.close()
            #pygame.quit()
        

#final screen
ending = visual.SimpleImageStim(surf,path_to_fixdur_code+'images/instructions/ending.png')
ending.draw()
surf.flip()
core.wait(6)
surf.close()
#surf.fill((128,128,128))
#surf.blit(ending,(0,0))
#pygame.display.update()
   
#write metadata into file
pickle.dump(trial_list,subject_file)
subject_file.close()

if EYETRACKING == True:
    el.finish()
os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')

#pygame.quit()
if os.path.exists('/home_local/tracking/experiments/fixdur/'):
    os.system('cp -r /home_local/tracking/experiments/fixdur/expcode/data/'+str(subject)+'/ /home_local/tracking/experiments/fixdur/data/'+str(subject)+'/')
#sys.exit()
