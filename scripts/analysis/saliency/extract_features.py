# -*- coding: utf-8 -*-
"""
generated on Mon Dec  7 14:20:29 2015

@author: jwu
"""

"""
For each image shown in the experiment extract the features (9) from each 
bubble separatedly. Then compute the mean per feature per bubble and store it 
into a dataframe.
"""

from pandas import DataFrame, concat
import pickle

import matplotlib.pyplot as plt


#------------------------------------------------------------------------------
   
import numpy as np
import PIL

def prepare_bubble(path):
    """ load the bubble image as numpy array and set the bg to grey """    
    img = load_ipl_as_array(path)
    img = gray_bg(img)
    return img

    
def load_ipl_as_array(path):
    """ load a .tiff image as numpy array for further processing """    
    img = PIL.Image.open(path).convert('RGBA')
    img = np.array(img)
    return img

    
def gray_bg(img):
    """ set the transparent part of the bubble image to grey """    
    for i in range(len(img)):
        for k in range(len(img[i])):
            if img[i][k][3] == 0:
                img[i][k] = [128, 128, 128, 255]
    return img
    
def generate_image(row):
    """ reconstruct the images shown during the experiment  
        return an array with all images """
    image = np.zeros((960, 1280, 4), np.uint8) 
    image[:,:] = (128, 128, 128, 255)
    for k in range(len(row['dispXcorrected'])):
        x = row['dispXcorrected'][k]
        y = row['dispYcorrected'][k]         
        path = "/net/store/nbp/projects/fixdur/stimuli/single_bubble_images/" + \
                str(row.loc['image']) + "/" + \
                "bubble_" + str(x) + "_" + str(y) + ".tiff"
        bubble = prepare_bubble(path)
        x = row['dispXcorrected'][k]
        y = row['dispYcorrected'][k]          
        image[y:y+154, x:x+154] = bubble

    return image
    
#------------------------------------------------------------------------------
    
import cv
from bifl import my_features as features
    
def extract(img):
    img = del_alpha(img)
    img = array2ipl(img)
    img_features = features.extract(img)
    return img_features


def del_alpha(img):
    """ delete the alpha channel of a img (numpy array)  
        for some reason features.extract() works only for 3 channel images """    
    img = img[:,:,0:3].copy()
    return img

    
def array2ipl(img):
    """ convert a ndarray image to ipl as
        features.extract*() works only for ipl format """    
    img_new = cv.CreateImageHeader((img.shape[1], img.shape[0]), cv.IPL_DEPTH_8U, 3)
    cv.SetData(img_new, img.copy().data,img.dtype.itemsize*3*img.shape[1])
    img_new[50,75]
    return img_new
    
#------------------------------------------------------------------------------

        
def save_means(fMaps, row, feat):
        
    positions = zip(row['dispXcorrected'], row['dispYcorrected'])
    """ this loop returns one mean per bubble per feature """
    for f in fMaps[0]:
        mean_f = []
        """ this loop returns one mean per bubble"""
        for i in range(int(row['NumOfBubbles'])):
            position = positions[i]
            mean_level = []            
            """ this loop returns one mean per level """
            for l in range(3):                                
                x, y = get_pos(position, l)                
                mean = get_mean(l, x, y, fMaps[l][f])
                mean_level.append(mean)
            
            mean_bubble = np.mean(mean_level)        
            mean_f.append(mean_bubble)    
        
        feat[f].append(mean_f)
    return feat
        
def get_pos(pos, l):
    x, y = pos
    return (x/2**l, y/2**l)
    
def get_mean(l, x, y, fmap):
    size = 154/2**l
    bubble = fmap[y:y+size, x:x+size]
#    plt.figure()    
#    im = plt.imshow(bubble)
#    im.set_cmap('YlGnBu')
    mean = np.asarray(bubble).mean()
    return mean    

#------------------------------------------------------------------------------

def extract_features(data):
    """ main function """    
    feat = {key : [] for key in ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']} 
    for row in data.index:
        img = generate_image(data.loc[row])
#        plt.figure()
#        plt.imshow(img)
        features_maps = extract(img)
        feat = save_means(features_maps, data.loc[row], feat)
    df = DataFrame(feat, index=data.index)
    return df
    
#path_to_data_final = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final.p'
#
#data = DataFrame(pickle.load(open(path_to_data_final)))    
#data = data[0:10]    
#df = extract_features()
#
## save df into data
#new_data = concat([data, df], axis=1)
#save_to = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_with_features.p'
#new_data.to_pickle(save_to)