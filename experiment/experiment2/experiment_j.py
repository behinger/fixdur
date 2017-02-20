# import modules
import sys, os, random, math, string, glob, pdb, re
from psychopy import visual, core, event, monitors,logging
import numpy as np
import cPickle as pickle

import trial, tools
import tools_extended as tools_ex
from PIL import Image
#from scipy.random import exponential

#from pylink import openGraphicsEx
#from eyelink_psychopy import EyeLinkCoreGraphicsOpenGL



#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()


#NUM_OF_TRIALS =128
NUM_OF_TRIALS = 5
TRIAL_TIME = 6000   #how long sould the bubbles in theory be displayed per trial for randomization

START_TRIAL = 1    #which trial to begin with   
fullscreen = True
EYETRACKING = False


if EYETRACKING == False:
    tracker = None;
else:
    import pylink
    import fixdur_tracker

#subject number to determine which multiple_bubble_images are shown, first subject 0
#subject_number = raw_input("Please enter the subject NUMBER(31-45): ")
subject_number = raw_input("Please enter the subject NUMBER: ")
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
# copy of all images that are used (which remains unchanged)
all_images_copy = list(all_images)
        
# open_file for meta data
if START_TRIAL == 0:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject),'w')
else:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject)+str(START_TRIAL),'w')
# set up the window
rectXY = (1920,1080);

surf = visual.Window(size=rectXY,fullscr=fullscreen,winType = 'pyglet', screen=0, units='pix',waitBlanking=True)
surf.setMouseVisible(False)

# load memory image
memory_image = visual.SimpleImageStim(surf, image=path_to_fixdur_code+'images/memory.png')

# create grey mask image
grey_im = Image.new('L',(2048,2048),128)
greyStim = visual.ImageStim(surf,grey_im)

# preload all images and create a stimulus list out of them
stimList_preload = {}
for new_image in all_images: 
    # load image
    image = Image.open(path_to_fixdur_files+'stimuli/urban/'+new_image)
    
    # convert image to grayscale
    image = image.convert('L')
    
    # create a stimulus and save it in the stimulus list
    stim = visual.ImageStim(surf, image=image, units='pix')
    stimList_preload[new_image] = stim

# set up eyetracker
rand_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
print rand_filename
if EYETRACKING:
    tracker = fixdur_tracker.Tracker(surf,rand_filename+'.EDF')


#start slide show
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/intro*.png')))
if EYETRACKING:
    #tools_ex.tracker_setup(surf,tk)
    tracker.setup()

# show fixation cross
fix_cross = visual.SimpleImageStim(surf,image=path_to_fixdur_code+'images/fixationcross.png')
#fix_cross.draw(surf)
surf.flip()

# create gaussian mask
gausStim = tools_ex.create_mask_fast([(0,0)],surf)

#training trials
if START_TRIAL == 0:
    tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/training_block1.png')))
    trial.training(surf,tracker,memory_image,fix_cross,stimList_preload,gausStim,EYETRACKING,control=1)
 
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/pre_start.png')))

# show fixation cross
fix_cross.draw(surf)
surf.flip()


trial_num = 1
trial_list = []



# create mask stimulus for single bubbles    
#single_mask_stim = tools_ex.create_mask([surf.size/2],mask_size=surf.size*2)
#maskimage = Image.new('L',surf.size*2,128)
#gausStim = visual.ImageStim(surf,maskimage,mask=-single_mask_stim)
'''p_noise = re.compile('noise') #define pattern for pattern matching
for new_image in all_images: 
    if p_noise.match(new_image) != None:
        image = Image.open(path_to_fixdur_files+'stimuli/noise/post_shine/'+new_image)
    else:
        image = Image.open(path_to_fixdur_files+'stimuli/urban/'+new_image)
        # convert image to grayscale
        image = image.convert('L')
    stim = visual.ImageStim(surf, image=image, units='pix')
    stimList_preload[new_image] = stim '''

#surf.setRecordFrameIntervals(True)
#surf._refreshTreshold=1/120.0+0.002
#logging.console.setLevel(logging.WARNING)

# run the game loop
#for img_num in range(NUM_OF_TRIALS-START_TRIAL):
for img_num in range(38,48):
    #print chosen_image
    try:
    
        #remove all trials that should be skipped
        if START_TRIAL !=0 and img_num == 0:
            for tr in range(0,START_TRIAL):
                all_images.pop(0)
    
        # start with first image
        bubble_image = all_images[0]    # copy in which already used locations can be deleted
        #    remaining_points = list(sample_points)
        
        #remove chosen image from all images
        all_images.pop(0)
        
        #get the trial corresponding to the image
        current_trial = trial_mat[np.where(trial_mat[:,4] == str(float(img_num+1)))]
           
        # breaks (wait for next trial)
        # 5 breaks in 96 trials; every 16 trials (32 is used for instructions, see below)
        breaks = [16,48,64,80]
        breaks = [ x + START_TRIAL +1 for x in breaks] # +1 because we start counting trial_num at 1
        #print trial_num
        if trial_num in breaks:
            text = visual.TextStim(surf, text="It's time for a break!") #u in front of the text??
            text.draw(surf)
            
        # Break with instructions in between the first and the second block
        elif trial_num == 33:
            
            # instructions for second block
            tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/finish_block1.png')))
            tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/memory1.png')))
            tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/training_block2.png')))
            
            # training trials for second block            
            trial.training(surf,tracker,memory_image,fix_cross,stimList_preload,gausStim,EYETRACKING,control=0)
            tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/pre_start2.png')))
            
            # show circle
            circ = visual.Circle(surf, units='pix', radius=10)
            circ.draw(surf)
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
            tracker.drift()
            #tracker.doDriftCorrect(surf.size[0]/2, surf.size[1]/2, 1, 1)
            
        #keep displaying fixation cross so it is still present after new calibration
        fix_cross.draw(surf)
        surf.flip()
            
        #start trial (eye-tracker)
        if EYETRACKING == True:
            tracker.start_trial()

        #normal_dist with mean 300 and spread 700
        delay_time = np.random.uniform(300,700)
        core.wait(int(delay_time/1000))
        
        # New Part
        

        
        # start trial
        if EYETRACKING == True:            
           tracker.trial(trial_num)
           tracker.trialmetadata('BUBBLE_IMAGE',bubble_image)
        
        subtrial_num = 1
        subtrial_list = []        
        white_image = Image.new('L',image.size,150)
        stimWhite = visual.ImageStim(surf, image=white_image, units='pix')
        stim = stimList_preload[bubble_image]
        
        # Sample bubble locations for current image from Poisson distribution
        width, height = stim.size
        sample_points = tools_ex.poisson_sampling(width,height)        
        
        memory = True     
        whole_image = False
        start = core.getTime()
        # copy in which already used locations can be deleted
        remaining_points = list(sample_points)
        
        for subtrial in current_trial:
            #subtrial[1] = 0

            #print 'subtrial: '+str(subtrial_num)
            # print subtrial
            # reset list for used locations            
            used_locations = []
        
            control = int(float(subtrial[3]))
            
            #choose starting bubble for first trial randomly
            if subtrial_num == 1:
                chosen_location = [random.choice(sample_points)]
                first_bubble = chosen_location[0]
                
                if control == 1:
                    memory = False

            # make a list of used locations                
            #used_locations.append(chosen_location[0])
            
            #print chosen_location[0]
            # delete previous location for next subtrial
            if chosen_location[0] in remaining_points:
                remaining_points.remove(chosen_location[0])
            
            # create mask image for first bubble
            #print(chosen_location)
            #tools.debug_time("before mask create",start)
            #start = core.getTime()
            
            ### mask_im = tools_ex.create_mask(chosen_location) ???
            #tools.debug_time("mask created",start)
           # start = core.getTime()
            #stim.mask = mask_im
            #tools.debug_time("stim.mask =mask_im updated",start)
            
            
            #start = core.getTime()
            stim.mask = None
            tools.debug_time("1.stim.mask=None",start)
            stim.draw()
            tools.debug_time("2.stim.draw()",start)
            tools_ex.create_mask_fast(chosen_location,surf,gausStim)
            tools.debug_time("3.tools_ex.create_mask_fast",start)
            
            
            # if control condition is applied
            if control == 1 and subtrial_num != 1:
                # flip to foveated "old" bubble
                surf.flip()
                
                foveated_prev_start = core.getTime()
                if EYETRACKING == True:                
                    tracker.trialmetadata("foveated_prev_onset", foveated_prev_start)
                
                tools.debug_time("4.[white] foveated displayed",start)
                start = core.getTime()
                
                bubble_display_start = core.getTime()
               # stimWhite.mask = mask_im
                #tools.debug_time("stimWhite.mask = mask_im",start)
                #start = core.getTime()
            
                #display time for white bubble (gaussian with mean 400 ms and sd 50 ms)
                white_disp = np.random.normal(400,50)
                #white_disp = 300 + np.random.exponential(200,1)
                
                # find a different image
                new_image = random.choice(all_images_copy)
                while new_image == bubble_image:
                    new_image = random.choice(all_images_copy)

                #tools.debug_time("new image selected",start)                
                #start = core.getTime()                
                
                stimWhite.draw()
                tools_ex.create_mask_fast(chosen_location,surf,gausStim)
                
                ###################
                ### Wait 200ms with current foveated
                ###################                              
                curr_display_time = 0
                while curr_display_time < 200/1000.:
                    core.wait(0.001)                    
                    curr_display_time = core.getTime() - bubble_display_start
                start = start+200/1000.
                

                surf.flip() #flip to white stimulus
                white_display_start = core.getTime()
                if EYETRACKING == True:                
                    tracker.trialmetadata("white_onset", white_display_start)
                    
                #display_start = core.getTime()

                tools.debug_time("[white] white displayed",start)
                start = core.getTime()
                
                stim = stimList_preload[new_image]
                stim.mask = None
                stim.draw()
                tools_ex.create_mask_fast(chosen_location,surf,gausStim)
                
                curr_display_time = 0
                while curr_display_time < white_disp/1000:
                    core.wait(0.001)                    
                    curr_display_time = core.getTime() - white_display_start
                start = start + white_disp/1000.
                
                #tools.debug_time("new image set",start)
                
                # display white bubble until display time is over
                #start = core.getTime()

            else:
                #if the control condition is not applied set both triggers to "None" because they are not applicable
                foveated_prev_start = 'None'
                white_display_start = 'None'
                
            #################################
            ### Show A Single Foveated Bubble
            ###############################
            tools.debug_time("before flip",start)
            #print(stim.pos)
            surf.flip()
            tools.debug_time("after flip",start)
            bubble_display_start = core.getTime()
            if EYETRACKING == True:                
                tracker.trialmetadata("forced_fix_onset", bubble_display_start)
            tools.debug_time("stimulus drawn, wait forced fix time (white-timing corrected)",start)
            start = core.getTime()

            
            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial_num == 1:
                if EYETRACKING:
                    tools.sacc_detection(tracker,chosen_location,False,surf,chosen_location[0],remaining_points)            
            
            # get number of bubbles for current trial
            num_of_bubbles = int(float(subtrial[1]))
            #num_of_bubbles = 1            
            
            if num_of_bubbles == 0:
                mask_im = tools_ex.whole_image(chosen_location)
                whole_image = True
                #stim.mask = mask_im
            
            # choose bubble locations according to num of bubbles
            else:
                bubble_locations = tools_ex.choose_locations(whole_image,num_of_bubbles, sample_points, remaining_points, chosen_location)          
                mask_im = tools_ex.create_mask(bubble_locations)
                #mask_im = tools_ex.create_mask(bubble_locations,(2048,2048),MULTIPLE=True)
                [used_locations.append(location) for location in bubble_locations]
                whole_image = False
            tools.debug_time("Before Mask Adding",start)    
            #greyStim.mask = -mask_im
            stim.mask = mask_im
            
            print('NoB:%i'%(num_of_bubbles))
            print('FullImage:%i'%(whole_image))
            #tools.debug_time("choose new bubble locations ",start)
            #start = core.getTime()
            # prepare stimulus for alternative bubble(s)
            #stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
            
            
            #tools.debug_time("stim.mask",start)
            #start = core.getTime()
            
            disp_time = float(subtrial[2])
            #keep displaying choosen bubble until disp_time is over
            
            
            tools.debug_time("Before Stim Draw",start)

            # show alternative bubble(s)
            stim.draw()
            #greyStim.draw()
            ###################
            ## Wait FORCED FIXATION TIME
            ###################
            bubble_display_time = 0
            while bubble_display_time < disp_time/1000.:
                core.wait(0.001)                    
                bubble_display_time = core.getTime() - bubble_display_start
                
            start = start + disp_time/1000.
            
            ###################
            ## Show Alternative Bubbles
            ###################
            #print(stim.pos)
            surf.flip()
            tools.debug_time("choose new bubble locations (without FF)",start)

            start = core.getTime()

            stimulus_onset = core.getTime()
            if EYETRACKING == True:
                tracker.trialmetadata("stimulus_onset", stimulus_onset)

            if EYETRACKING:
                chosen_location = [tools.sacc_detection(tracker,used_locations,whole_image,surf, chosen_location[0],remaining_points)]
                #print('saccade detected')
            else:
                if num_of_bubbles == 0:
                    copy_points = list(sample_points)
                    copy_points.remove(chosen_location[0])
                    core.wait(0.1) ### remove
                    chosen_location = [random.choice(copy_points)]
                else:
                    core.wait(0.1) ### remove
                    chosen_location = [random.choice(bubble_locations)]
                            
            tools.debug_time("et saccade detected",start)
            start = core.getTime()    
            
            
            saccade_offset = core.getTime()
            if EYETRACKING == True:
                tracker.trialmetadata("saccade_offset", saccade_offset)
                
            #for location in used_locations:
            #    if location in sample_points:                
            #        sample_points.remove(location)
                
            #metainfos for tracker
            if EYETRACKING == True:
                tracker.trialmetadata("DISPLAYED_BUBBLES", used_locations)
                tracker.trialmetadata("CHOSEN_BUBBLE", chosen_location)
                tracker.trialmetadata('BUBBLE_DISPLAY_TIME', disp_time)
        
            key = tools.wait_for_key()
            if 'escape' in key:
                surf.close()
                sys.exit()
        
            #metainfos for dictionary
            #subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_locations, 'first_bubble':first_bubble, 'chosen_bubble': chosen_location, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}
            subtrial_dict = {'trial': trial_num, 'img': bubble_image,'num_bubbles': num_of_bubbles,'whole_image_condition': whole_image, 'control_condition': control, 'disp_bubbles': used_locations, 'first_bubble':first_bubble, 'chosen_bubble': chosen_location, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start,'white_onset': white_display_start, 'foveated_prev_onset': foveated_prev_start}                
            subtrial_list.append(subtrial_dict)  
            
            subtrial_num = subtrial_num + 1
        
      
            tools.debug_time("end of trial - time after wait for fix",start)
                
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        if memory:
            memory_res = tools_ex.memory_task(stim,memory_image,surf,stimList_preload,bubble_image)
        else:
            memory_res = ['no_memory_task','no_memory_task','no_memory_task']
        
        #add trial meta data    
        trial_list.append(subtrial_list)
        #memory_res has order correct, left, right -> wrong in dict, but corrected for in analysis
        trial_list.append({'subject_number':subject_number,'left_bubble':memory_res[1], 'right_bubble':memory_res[2], 'correct':memory_res[0]})
        trial_num = trial_num + 1   
        
        if EYETRACKING == True:       
            tracker.end_trial() 
        
    except Exception as e:
        import sys
        exc_type, exc_obj, exc_tb = sys.exc_info()

        print e.message,e.args,exc_tb.tb_lineno
        try:
            error_file = open(path_to_fixdur_code+'data/'+str(subject)+'/error_'+str(trial_num)+'_'+str(subtrial),'w')
            error_file.write('ERROR')
            error_file.close()
        except:
            pass
        pickle.dump(trial_list,subject_file)
        subject_file.close()
        if EYETRACKING == True:
            tracker.finish()
        os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')
        surf.close()
            #pygame.quit()
        import traceback
        traceback.print_exc()


#final screen
ending = visual.SimpleImageStim(surf,path_to_fixdur_code+'images/instructions/ending.png')
ending.draw()
surf.flip()
core.wait(6)
surf.close()

   
#write metadata into file
pickle.dump(trial_list,subject_file)
subject_file.close()

if EYETRACKING == True:
    tracker.finish()
os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')

#if os.path.exists('/home_local/tracking/experiments/fixdur/'):
#    os.system('cp -r /home_local/tracking/experiments/fixdur/expcode/data/'+str(subject)+'/ /home_local/tracking/experiments/fixdur/data/'+str(subject)+'/')
#sys.exit()
