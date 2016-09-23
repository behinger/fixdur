# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:57:12 2016

@author: jwu
"""

""" this is the master script """

import os
home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/'
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/saliency/'

import sys
sys.path.insert(0, home) # enables import from working directory

# my modules
import preprocess_data
import extract_features
#import pca
#import lme
#import main_analysis

# python modules
from pandas import DataFrame, concat
import pickle
import os

def load(filename):
    """ handy function to load a file from the working directory SALIENCY """
    path = home + filename
    if os.path.isfile(path):
        df = DataFrame(pickle.load(open(path, 'rb')))
        return df
    else:
        print 'file not found'
    
    
""" Step 0:
specify the filenames:
"""
#file_data_pre = 'data_pre.p' # data imported from R
#file_features_next = 'features_next_bubbles.p' # dataframe containing only the feature means calculated for next bubbles
#file_features_curr = 'features_curr_bubbles.p' # dataframe containing only the feature means calculated for current bubbles
file_data_pre = 'one_bubble.p'
file_features_next = 'one_bubble_next.p'
file_features_curr = 'one_bubble_curr.p'

""" Step 1:
Get the preprocessed data from R:
    - run fd_loaddata.R on all_res.p and import the result in python
    - add columns 'dispXcorrected', 'dispYcorrected'
You need to save the dataframe for step 3, so specify the flags
"""
if os.path.isfile(home + file_data_pre):
    data = load(file_data_pre)
    print 'dataframe %s loaded from working directory' %(file_data_pre)
else:
    data = preprocess_data.preprocess(save='yes', save_as=file_data_pre)
    print 'preprocessed data imported from R and saved as %s' %(file_data_pre)

# if you wanna run preprocess_data.preprocess without saving:    
# data = preprocess_data.preprocess(save='no') 


""" Step 2:
Extract features from next bubbles 
"""
if os.path.isfile(home + file_features_next):
    df_features_next = load(file_features_next)
    print 'dataframe %s loaded from working directory' %(file_features_next)
    data = concat([data, df_features_next], axis=1) 
else:
    print 'Warning: The analysis of features for next bubbles is not \
    parallelized! You should optimize it or run it overnight.'
    answer = raw_input('Do you want to continue? (y / n)' )
    if answer=='y':
        print 'Good night!'        
        df_features_next = extract_features.extract_features(data)
        df_features_next.to_pickle(home + file_features_next)
        print 'dataframe saved as %s' %file_features_next
        data = concat([data, df_features_next], axis=1) 
    if answer=='n':
        print 'no feature information contained in data'
        

""" Step 3:
Extract features from current bubbles 
"""
if os.path.isfile(home + file_features_curr):
    df_features_curr = load(file_features_curr)
    print 'dataframe %s loaded from working directory' %(file_features_curr)
    data = concat([data, df_features_curr], axis=1)
else:
    command = '%run /net/store/nbp/users/jwu/fixdur/analysis/saliency/extract_features_currB_new.py'
    print "Run the following command in an ipython console! Otherwise you'll \
           kill the kernel! (~ 10 minutes)"
    print command
    print 'Before running go to the script and ensure that the right paths are given.'
    sys.exit('rerun the script after having executed the above lines')
    

""" Step 4:
Run Principle Component Analysis on the entire dataset where trials with more
than one bubbles displayed are splitted and feature values for next and current
bubbles are combined
"""
#pc_next, pc_curr = main_analysis.pca_all(data)


""" Step 5:
"""




""" 
If you want to reproduce the plots for comparing the following methods:
    (1) feature maps of single bubbles on grey background 154x154
    (2) feature maps of many bubbles displayed on the grey background (as shown
        during the experiment) 
    (3) feature maps of the original grey image, non-bubble regions then cut 
        out while bubble regions are remained with a gaussian mask applied,
Call the following function:
"""
def compare_methods():
    from compare_methods import all_images
    # call the function with an index, e.g. n=149
    all_images()
    # data loaded from all_res.p stored into all_bubbles_with_path.p