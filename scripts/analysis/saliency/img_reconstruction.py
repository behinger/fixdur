# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 17:12:13 2015

@author: jwu
"""
"""
reconstruct the images shown during the experiment, i.e. bubbles on grey bg
(not containing the image with the chosen bubble)
"""

import numpy as np
import cv2
import PIL
 
 
def select_samples(all_bubbles, n, start):
    """ for testing purposes return a subset of the dataframe """    
    return all_bubbles[start:start+n]    


def create_image(all_bubbles):
    """ reconstruct the images shown during the experiment  
        return an array with all images """
    images = []
    for i in all_bubbles.index:
        image = np.zeros((960, 1280, 4), np.uint8) 
        image[:,:] = (128, 128, 128, 255)
        for k in range(len(all_bubbles.loc[i, 'dispX'])):
            bubble = PIL.Image.open(all_bubbles.loc[i, 'path'][k]).convert('RGBA')
            bubble = np.array(bubble)
            x = all_bubbles.loc[i,'dispX'][k]
            y = all_bubbles.loc[i,'dispY'][k]          
            image[y:y+154, x:x+154] = bubble
        # store the image
        # cv2.imwrite('screenshots/img_'+str(i)+'.bmp', image)
        images.append(image)
    return images
    
    
def show_image(image):
    """ display a given image """
    cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)
    cv2.imshow("image", image)
    cv2.waitKey(100000)
    cv2.destroyAllWindows()


def display_bubbles(all_bubbles, all_or_not):   
    """ main function callable with amount=='all' or anything else
        return a list containing images in np array format """        
    if all_or_not != 'all': 
        if type(all_or_not)==int:
            n = 1
            start = all_or_not
        else:
            n = int(raw_input("number of bubbles: "))
            start = int(raw_input("start at number: "))
        bubbles = select_samples(all_bubbles, n, start)
        images = create_image(bubbles)
#        for i in range(len(images)):
#            show_image(images[i])
        return images
    else:
        images = create_image(all_bubbles)
        return images