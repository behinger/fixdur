# -*- coding: utf-8 -*-
"""
Created on Thu Nov 27 14:52:39 2014

@author: lkaufhol
"""

import pygame, sys, os, random, pdb
import cPickle as pickle
import numpy as np
import trial, tools

#paths
path_to_fixdur_files, path_to_fixdur_code = tools.paths()
#path_to_fixdur_files = '/net/store/nbp/projects/fixdur/stimuli_gist'

pygame.init()

# set up the window
rectXY = (1920,1080)
surf = pygame.display.set_mode(rectXY, 0, 32)
surf.fill((128,128,128))
grayimage = pygame.image.load(path_to_fixdur_code+'images/gray_background.tiff').convert_alpha()

all_images = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/')
training = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/')
for image in training:
    all_images.append(image)

#list to store images    
image_list = []

for bubble_image in all_images:
    
    #list to store bubble location for each image
    bubble_loc = []
    
    for a in range(1,21):
        
        # load all bubbles for chosen image
        if ((bubble_image == 'image_28.bmp') or (bubble_image == 'noise_train_shine.bmp')):     
            remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image)
        else:
            remaining_bubbles = os.listdir(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image)
        all_bubbles = []
        loaded_bubbles = []
        for bubble in remaining_bubbles:
            if ((bubble_image == 'image_28.bmp') or (bubble_image == 'noise_train_shine.bmp')):
                loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/training/single_bubbles/'+bubble_image+'/'+bubble).convert_alpha())
            else:    
                loaded_bubbles.append(pygame.image.load(path_to_fixdur_files+'stimuli/single_bubble_images/'+bubble_image+'/'+bubble).convert_alpha())
            all_bubbles.append([int(bubble.split('_',1)[1].split('_')[0]),int(bubble.split('_',1)[1].split('_')[1].split('.')[0])])
        remaining_bubbles = list(all_bubbles)
        # load distance mat for chosen image
        dist_mat = np.load(path_to_fixdur_code+'distances/'+bubble_image+'.npy')
        chosen_bubble = [random.choice(all_bubbles)]

        more_bubbles = False
        while not more_bubbles:
            try:
                used_bubble, more_bubbles = trial.get_image(surf,bubble_image,all_bubbles,loaded_bubbles,remaining_bubbles,chosen_bubble,21,dist_mat)
            except ValueError:                
                print 'ValueError empty bubble list'
            except KeyError:
                print 'KeyError empty bubble list'
            except IndexError:
                print 'IndexError empty bubble list'
            remaining_bubbles = list(all_bubbles)
        
        #store displayed bubble locations
        bubble_loc.append(used_bubble)

        #surf.blit(stim,(0,0))
        if not os.path.exists(path_to_fixdur_files+'stimuli/multi_bubble_images3/'+bubble_image+'/'):
            os.system('mkdir '+path_to_fixdur_files+'stimuli/multi_bubble_images3/'+bubble_image+'/')
        pygame.image.save(surf,path_to_fixdur_files+'stimuli/multi_bubble_images3/'+bubble_image+'/'+bubble_image+'_'+str(a)+'.png')
    
    image_list.append(bubble_loc)


mult_bubble_file = open(path_to_fixdur_files+'stimuli/mult_bubble_pos','w') 
pickle.dump(image_list,mult_bubble_file)
mult_bubble_file.close()
all_images_file = open(path_to_fixdur_files+'stimuli/all_images','w') 
pickle.dump(all_images,all_images_file) 
all_images_file.close()
