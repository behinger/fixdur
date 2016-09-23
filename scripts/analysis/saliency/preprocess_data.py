# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 15:48:51 2015

@author: jwu
"""
""" 
This piece of code imports both 'all_res' and 'data_from_R' (data preprocessed 
in R @Bene, see prepreprocess_data.py; all columns are somehow of type str 
except the new calculated ones -> access difficulties). It drops the same rows
as data_from_R and adds all new columns. The resulting dataframe will be saved 
as data_final.py for further processing. 
"""
import os
home = '/net/store/nbp/users/jwu/fixdur/analysis/'
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/'
    
import sys 
sys.path.insert(0, home)
from prepreprocess_data import preprocess as prepreprocess
from pandas import DataFrame, concat
import pickle
import numpy as np

def preprocess(save='yes', save_as='data_final.p'):
#    path_to_all_res = '/net/store/nbp/users/jwu/fixdur/analysis/all_res.p' 
#    path_to_data_from_R = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_from_R_old.p'
    path_to_data_final = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final.p'
    
#    all_res = DataFrame(pickle.load(open(path_to_all_res)))
#    data_from_R =DataFrame(pickle.load(open(path_to_data_from_R)))
    data_from_R = prepreprocess()
    
#    """ drop rows that aren't existent in data_from_R """
#    to_drop = [x for x in all_res.index if str(x) not in data_from_R.index]
#    data_cleaned = all_res.drop(to_drop).copy()
    
    """ change str index into int index """
#    data_from_R.index = data_cleaned.index
    data_from_R.index = [int(i) for i in data_from_R.index]
    
    """ concatenate both df"""
#    common_columns = [x for x in all_res.columns if x in data_from_R.columns]
#    new_columns = [x for x in data_from_R.columns if x not in data_cleaned.columns]
#    data_final = concat([data_cleaned[common_columns], data_from_R[new_columns]], axis=1)
    data_final = data_from_R
    #data_final[['dispXcorrected','dispYcorrected']] = data_final[['dispX','dispY']].copy() # @ 8.1.16
    dispXcorrected, dispYcorrected = [], []    
    
    """ correct the bubble positions """
    for i in data_final.index:
        xSub, ySub = [], []
        for k in range(len(data_final.loc[i, 'dispX'])):
            x = int(data_final.loc[i, 'dispX'][k])
            y = int(data_final.loc[i,'dispY'][k]) 
            if x<0:
                print str(x)+'<0'
                xSub.append(np.nan)
                ySub.append(np.nan)
            else:          
                xSub.append(x-77-320) 
                ySub.append(y-77-60)
        dispXcorrected.append([xSub])
        dispYcorrected.append([ySub])

    dispXcorrected = DataFrame(data=dispXcorrected, index=data_final.index, columns=['dispXcorrected'])        
    dispYcorrected = DataFrame(data=dispYcorrected, index=data_final.index, columns=['dispYcorrected'])
    data_final = concat([data_final, dispXcorrected, dispYcorrected], axis=1)        
    
    """ save final dataframe to path """
    home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency'
    if save == 'yes':
        data_final.to_pickle(home + '/' + save_as)
        print 'data saved as %s'%(save_as)
    else:
        print 'data not saved as pickle file'
        
    return data_final
