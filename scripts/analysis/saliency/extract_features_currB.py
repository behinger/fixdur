# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 13:17:59 2016

@author: jwu
"""

# -*- coding: utf-8 -*-
"""
generated on Mon Dec  7 14:20:29 2015

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
#from joblib import Parallel, delayed
from pandas import DataFrame, concat
import pickle
from compare_methods import extract
import numpy as np
#import matplotlib.pyplot as plt
import rpy2.robjects as ro # this line is super important to load the df at all!!
                       # otherwise python fails to load data manipulated in R

#path_to_data_final = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final.p'
path_to_data_final = home + 'one_bubble.p'
data = DataFrame(pickle.load(open(path_to_data_final)))  
#data = data[0:100]
fList = ['Idx', 'id0Curr', 'id1Curr', 'id2Curr', 'idXCurr',  'lumcCurr', 'lumsCurr', 'lumtCurr', 'sobCurr', 'sobsCurr']


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
            data.loc[i,'currXcorrected'] = x-77-320
            data.loc[i,'currYcorrected'] = y-77-60
    #data.to_pickle(path_to_data_final)
if 'currXcorrected' not in data.columns:
    correct_pos()    
    
def save_means(fMaps, row):
    """ calculate for each feature the mean of feature maps on 3 levels """
    feat = []    
    """ this loop returns one mean per bubble per feature """
    for f in fMaps[0]:
        mean_level = []            
        """ this loop returns one mean per level """
        for l in range(3):                                               
            mean = np.asarray(fMaps[l][f]).mean()
            mean_level.append(mean)
        mean_f = np.mean(mean_level)        
        feat.append(mean_f)
    return feat
            
            
def get_path(i):
    """ generate the path for a given row """
    path = "/net/store/nbp/projects/fixdur/stimuli/single_bubble_images/" + \
            str(data.loc[i,'image']) + "/" + "bubble_" + \
            str(int(data.loc[i, 'currXcorrected'])) + "_" + \
            str(int(data.loc[i, 'currYcorrected'])) + ".tiff"
    return path
    
def currBubbles():
    """ for each row generate the path of the single bubble image, 
        extract the salient features and calculate the means for each feature """
    features = []
    for i in data.index:
        feat = [i]
        if np.isnan(data.loc[i,'currXcorrected']):
            feat[1:10] = [np.nan for i in range(9)]
        else:
            path = get_path(i)
            fMaps = extract('single bubble', path)
            feat[1:10] = save_means(fMaps, i)
        features.append(feat)
    return features

""" before parallelizing """    
#start_time = time.time()
#serial = currBubbles()
#print "runtime: ", time.time()-start_time
#df = DataFrame(data=serial, columns=fList, index=data.index)

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
        path = get_path(i)
        fMaps = extract('single bubble', path)
        feat[1:10] = save_means(fMaps, i)    
    return feat
    
start_time = time.time()
if __name__ == '__main__':
    p = Pool(8)
    features = p.map(main, data.index)
print "runtime: ", time.time()-start_time  
  
df = DataFrame(data=features, columns=fList, index=data.index)

# check whether the result of multiprocessing remains the order of data
if (df.index == df.Idx).all():
    df = df.drop('Idx', axis=1)
    
#result = concat([data,df], axis=1)
result = concat([data[['currXcorrected', 'currYcorrected']], df], axis=1)

## combine the old dataframe with current one
#old_data = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_with_features.p'
#old = DataFrame(pickle.load(open(old_data)))
#f = ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']
#result[f] = old[f]

#save_to = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_with_currB.p'
save_to = home + 'one_bubble_curr.p'
result.to_pickle(save_to)
print 'dataframe saved to %s' %(save_to)