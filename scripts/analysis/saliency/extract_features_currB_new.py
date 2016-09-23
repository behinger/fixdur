# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 17:09:46 2016

@author: jwu
"""
"""
Compute feature means for current bubbles
"""
home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/'
import sys
sys.path.insert(0, home)

import time  
from multiprocessing import Pool
from pandas import DataFrame, concat
import pickle
from compare_methods import extract
import numpy as np
import matplotlib.pyplot as plt
import rpy2.robjects as ro # this line is super important to load data manipulated in R

def correct_pos():
    """ correct the x and y cordinates for bubble position
        apply only once """
    data[['currXcorrected','currYcorrected']] = data[['currBubbleX','currBubbleY']].copy()
    for i in data.index:
        x = int(data.loc[i,'currBubbleX'])
        y = int(data.loc[i,'currBubbleY'])
        if x<0:
            data.loc[i,'currXcorrected'] = np.nan
            data.loc[i,'currYcorrected'] = np.nan
        else:    
            data.loc[i,'currXcorrected'] = int(x-77-320)
            data.loc[i,'currYcorrected'] = int(y-77-60)
    
#-----------------------------------------------------------------------------
       
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
    x = int(row['currXcorrected'])
    y = int(row['currYcorrected'])         
    path = "/net/store/nbp/projects/fixdur/stimuli/single_bubble_images/" + \
    str(row.loc['image']) + "/" + \
    "bubble_" + str(x) + "_" + str(y) + ".tiff"
    bubble = prepare_bubble(path)         
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
def save_means(fMaps, i):
    """ calculate for each feature the mean of feature maps on 3 levels """
    feat = []    
    """ this loop returns one mean per bubble per feature """
    for f in fMaps[0]:
#        if f not in fList:
#            fList.append(f)
        position = int(data.loc[i, 'currXcorrected']), int(data.loc[i, 'currYcorrected'])
        mean_level = []            
        """ this loop returns one mean per level """
        for l in range(3):                                               
            x, y = get_pos(position, l)
            mean = get_mean(l, x, y, fMaps[l][f])
            mean_level.append(mean)
        mean_f = np.mean(mean_level) 
        feat.append(mean_f)
    return feat
        
def get_pos(pos, l):
    x, y = pos
    return (x/2**l, y/2**l)
    
def get_mean(l, x, y, fmap):
    size = 154/2**l
    bubble = fmap[y:y+size, x:x+size]
    mean = np.asarray(bubble).mean()
    return mean    
    
def extract_features():
    features = []        
    for i in data.index:
        feat = [i]
        if np.isnan(data.loc[i,'currXcorrected']):
            feat[1:10] = [np.nan for i in range(9)]        
        else:
            img = generate_image(data.loc[i])           
            features_maps = extract(img)
            feat[1:10] = save_means(features_maps, i)    
        features.append(feat)
    return features  

#------------------------------------------------------------------------------
""" parallelizing the process """
def main(i):
    """ for each row generate the path of the single bubble image, 
        extract the salient features and calculate the means for each feature """    
    if i%1000 == 0:
        print i
    feat = [i]
    if np.isnan(data.loc[i,'currXcorrected']):
        feat[1:10] = [np.nan for i in range(9)]
    else:
        img = generate_image(data.loc[i])
        features_maps = extract(img)
        feat[1:10] = save_means(features_maps, i) 
    return feat
    
#------------------------------------------------------------------------------

#path_to_data_final = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final.p'
path_to_data_final = home + 'data_pre.p'
#path_to_data_final = home + 'one_bubble.p'
data = DataFrame(pickle.load(open(path_to_data_final)))  
data = data[0:100]
fList = ['Idx', 'sobCurr', 'idXCurr', 'lumtCurr', 'id2Curr', 'lumsCurr', 'id0Curr', 'id1Curr', 'sobsCurr', 'lumcCurr']

if 'currXcorrected' not in data.columns:
    correct_pos()    
    
# not parallelized, for testing purposes
#start_time = time.time()
#features = extract_features()
#print "runtime: ", time.time()-start_time

# parallelized    
n = 8
start_time = time.time()
if __name__ == '__main__':
    p = Pool(n)
    features = p.map(main, data.index)
print "runtime: ", time.time()-start_time, '('+str(n)+' pools)'  

# convert to dataframe  
df = DataFrame(data=features, columns=fList, index=data.index)

# check whether the result of multiprocessing remains the order of data
if (df.index == df.Idx).all():
    df = df.drop('Idx', axis=1)
    
result = concat([data[['currXcorrected', 'currYcorrected']], df], axis=1)

#save_to = home + 'features_curr_bubbles.p'
save_to = home + 'one_bubble_curr.p'
#result.to_pickle(save_to)
#print 'dataframe saved to %s' %(save_to)