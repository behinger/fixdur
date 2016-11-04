# import modules
import sys, os, random, math, string, glob, pdb, re
from psychopy import visual, core, event, monitors,logging
import numpy as np
import cPickle as pickle
import trial, tools
import tools_extended as tools_ex
from PIL import Image
#from scipy.random import exponential
<<<<<<< HEAD
#from pylink import openGraphicsEx
#from eyelink_psychopy import EyeLinkCoreGraphicsOpenGL
=======
from pylink import openGraphicsEx
from eyelink_psychopy import EyeLinkCoreGraphicsOpenGL
>>>>>>> 1d20b94ff2f6639765f223a1ca073e6ea2cebcce


#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()


NUM_OF_TRIALS =128
#NUM_OF_TRIALS =5 
TRIAL_TIME = 6000   #how long sould the bubbles in theory be displayed per trial for randomization
START_TRIAL = 1    #which trial to begin with   
#fullscreen = True   
<<<<<<< HEAD
fullscreen = False
=======
fullscreen = True
>>>>>>> 1d20b94ff2f6639765f223a1ca073e6ea2cebcce
EYETRACKING = True

if EYETRACKING == False:
    tracker = None;
else:
    import pylink
    import fixdur_tracker

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
# copy of all images that are used (which remains unchanged)
all_images_copy = list(all_images)
        
# open_file for meta data
if START_TRIAL == 0:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject),'w')
else:
    subject_file = open(path_to_fixdur_code+'data/'+str(subject)+'/'+str(subject)+str(START_TRIAL),'w')

# set up the window
rectXY = (1920,1080);
surf = visual.Window(size=rectXY,fullscr=fullscreen,winType = 'pyglet', screen=0, units='pix')
surf.setMouseVisible(False)

# load memory image
memory_image = visual.SimpleImageStim(surf, image=path_to_fixdur_code+'images/memory.png')

# set up eyetracker
rand_filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
print rand_filename
if EYETRACKING:
<<<<<<< HEAD
    #tracker = tools_ex.tracker_init(surf)
    #openGraphicsEx(EyeLinkCoreGraphicsOpenGL(surf))
    #pylink.openGraphics()
    tracker = fixdur_tracker.Tracker(surf,rand_filename+'.EDF')
=======
    openGraphicsEx(EyeLinkCoreGraphicsOpenGL(surf))
    #pylink.openGraphics()
    el = tracker.Tracker(surf,rand_filename+'.EDF')
>>>>>>> 1d20b94ff2f6639765f223a1ca073e6ea2cebcce

#start slide show
tools.slideshow(surf, np.sort(glob.glob(path_to_fixdur_code+'images/instructions/intro*.png')))
if EYETRACKING:
    #tools_ex.tracker_setup(surf,tk)
    tracker.setup()

# show fixation cross
fix_cross = visual.SimpleImageStim(surf,image=path_to_fixdur_code+'images/fixationcross.png')
#fix_cross.draw(surf)
surf.flip()

#training trials
if START_TRIAL == 0:
	trial.training(surf,tracker,memory_image,fix_cross)
 
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
            tracker.drift()
            #tracker.doDriftCorrect(surf.size[0]/2, surf.size[1]/2, 1, 1)
            
        #keep displying fixation cross so it is still present after new calibration
        fix_cross.draw(surf)
        surf.flip()
            
        #start trial (eye-tracker)
        if EYETRACKING == True:
            tracker.start_trial()

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
        
        # copy in which already used locations can be deleted
        remaining_points = list(sample_points)
        
        # start trial
        if EYETRACKING == True:            
           tracker.trial(trial_num)
           tracker.trialmetadata('BUBBLE_IMAGE',bubble_image)
        
        subtrial_num = 1
        subtrial_list = []        
        memory = True        
        
        for subtrial in current_trial:
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
            used_locations.append(chosen_location[0])
            
            print chosen_location[0]
            # delete previous location for next subtrial
            if chosen_location[0] in remaining_points:
                remaining_points.remove(chosen_location[0])
            
            # create mask image for first bubble
            #print(chosen_location)
            mask_im = tools_ex.create_mask(chosen_location)
            
            # if control condition is applied
            if control == 1 and subtrial_num != 1:
                # create white bubble
                white_image = Image.new('L',image.size,150)
                stim = visual.ImageStim(surf, image=white_image, mask=mask_im, units='pix')
                
                #display time for white bubble
                white_disp = 300 + np.random.exponential(200,1)
                
                # find a different image
                new_image = random.choice(all_images_copy)
                while new_image == bubble_image:
                    new_image = random.choice(all_images_copy)
                
                # load the new image
                p_noise = re.compile('noise') #define pattern for pattern matching
                if p_noise.match(new_image) != None:
                    image = Image.open(path_to_fixdur_files+'stimuli/noise/post_shine/'+new_image)
                else:
                    image = Image.open(path_to_fixdur_files+'stimuli/urban/'+new_image)
                    # convert image to grayscale
                    image = image.convert('L')
                
                stim.draw()
                surf.flip()
                
                display_start = core.getTime()
                
                # display white bubble until display time is over
                curr_display_time = 0
                while curr_display_time < white_disp/1000:
                    core.wait(0.001)                    
                    curr_display_time = core.getTime() - display_start
                

            stim = visual.ImageStim(surf, image=image, mask=mask_im, units='pix')
            stim.draw()
            surf.flip()
                
            # show (only) chosen bubble
            #stim.draw()
            #surf.flip()
            
            bubble_display_start = core.getTime()
            if EYETRACKING == True:                
                tracker.trialmetadata("forced_fix_onset", bubble_display_start)
            
            # wait until first bubble is fixated before starting forced_fix_time
            if subtrial_num == 1:
                if EYETRACKING:
                    tools.sacc_detection(tracker,chosen_location)            
            
            # get number of bubbles for current trial
            num_of_bubbles = int(float(subtrial[1]))
            
            if num_of_bubbles == 0:
                mask_im = tools_ex.whole_image(chosen_location)
                whole_image = True
            
            # choose bubble locations according to num of bubbles
            else:
                bubble_locations = tools_ex.choose_locations(num_of_bubbles, sample_points, remaining_points, chosen_location)          
                mask_im = tools_ex.create_mask(bubble_locations)
                [used_locations.append(location) for location in bubble_locations]
                whole_image = False
        
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
                tracker.trialmetadata("stimulus_onset", stimulus_onset)

            if EYETRACKING:
                chosen_location = [tools.sacc_detection(tracker,used_locations,whole_image)]
            else:
                if num_of_bubbles == 0:
                    copy_points = list(sample_points)
                    copy_points.remove(chosen_location[0])
                    chosen_location = [random.choice(copy_points)]
                else:
                    chosen_location = [random.choice(bubble_locations)]
                            
                
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
            subtrial_dict = {'trial': trial_num, 'img': bubble_image, 'disp_bubbles': used_locations, 'first_bubble':first_bubble, 'chosen_bubble': chosen_location, 'planned_disp_time': disp_time, 'stim_onset': stimulus_onset, 'saccade_offset': saccade_offset, 'forced_fix_onset': bubble_display_start}                
            subtrial_list.append(subtrial_dict)  
            
            subtrial_num = subtrial_num + 1
        
      
            ##tools.debug_time("end of trial - time after wait for fix",start)
                
        #memory task
        #left_bubble, right bubble, correct = tools.memory_task(all_bubbles,loaded_bubbles,bubble_image,memory_image.copy(),surf)
        if memory:
            memory_res = tools_ex.memory_task(image,memory_image,surf)
        else:
            memory_res = ['no_memory_task','no_memory_task','no_memory_task']
        
        #add trial meta data    
        trial_list.append(subtrial_list)
        #memory_res has order correct, left, right -> wrong in dict, but corrected for in analysis
        trial_list.append({'subject_number':subject_number,'left_bubble':memory_res[0], 'right_bubble':memory_res[1], 'correct':memory_res[2]})
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
#surf.fill((128,128,128))
#surf.blit(ending,(0,0))
#pygame.display.update()
   
#write metadata into file
pickle.dump(trial_list,subject_file)
subject_file.close()

if EYETRACKING == True:
    tracker.finish()
os.system('mv '+rand_filename+'.EDF '+path_to_fixdur_code+'data/'+str(subject)+'/')

#pygame.quit()
if os.path.exists('/home_local/tracking/experiments/fixdur/'):
    os.system('cp -r /home_local/tracking/experiments/fixdur/expcode/data/'+str(subject)+'/ /home_local/tracking/experiments/fixdur/data/'+str(subject)+'/')
#sys.exit()
