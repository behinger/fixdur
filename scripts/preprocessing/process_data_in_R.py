# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 14:55:25 2015

@author: jwu
"""

"""
data contains 35+ additional columns calculated based on panda_all_res
data has 32349 rows less than panda_all_res (due to data cleaning)
"""

from pandas import DataFrame, concat
import rpy2.robjects as ro
import pickle
import os
from rpy2.robjects import pandas2ri

def preprocess():
    path_to_all_res = '/home/student/b/behinger/Documents/fixdur/analysis/all_res.p'
    if not os.path.isdir(path_to_all_res):
        path_to_all_res = '/home/student/l/lkaufhol/fixdur/analysis/all_res.p'
        if not os.path.isdir(path_to_all_res):
            path_to_all_res = '/net/store/nbp/users/jwu/fixdur/analysis/all_res.p'
    
    all_res = pickle.load(open(path_to_all_res))
    panda_all_res = DataFrame(all_res)
    panda_all_res = panda_all_res.drop('fixX',1);
    panda_all_res = panda_all_res.drop('fixY',1);
    
    pandas2ri.activate()
    ro.globalenv['data'] = panda_all_res
    ro.r(''' library(ggplot2) ''')
    data = ro.r(''' source('/net/store/nbp/users/jwu/fixdur/analysis/R/fd_loaddata.R');fd_loaddata(data)''')
    #y = pandas2ri.ri2py_dataframe(ro.r['data'])
    return data
#data2 = data.loc[[str(x) for x in range(data.shape[0])]]

""" 8.1.16
Bene added 13 new columns and deleted 2
>>> new columns saved while the 2 deleted ones are dropped in the old files (both data_from_R_old and data_final_old)
"""
#path_to_old = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_from_R_old.p'
#
#data_old = DataFrame(pickle.load(open(path_to_old)))
#new_col = [col for col in data.columns if col not in data_old.columns]
#data_new = data[new_col]
#
#save_to = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_from_R_newCol.p'
#data_new.to_pickle(save_to)
#
#dropped_col = [col for col in data_old.columns if col not in data.columns]
#data_old = data_old.drop(dropped_col, axis=1).copy()
#data_old.to_pickle(path_to_old)
#
#path_to_final_old = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final_old.p'
#final_old = DataFrame(pickle.load(open(path_to_final_old)))
#data_new.index = final_old.index
#final_new = concat([final_old, data_new], axis=1)
#
#save_to = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/data_final.p'
#final_new.to_pickle(save_to)