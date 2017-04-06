# -*- coding: utf-8 -*-
"""
Created on Fri May  8 13:55:11 2015

@author: behinger
"""

from pandas import DataFrame

import pickle

import os
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import numpy as np
ISFIXDURGIST = False
ISEXPERIMENT2 = True

if ISFIXDURGIST:
    path_to_all_res = './all_res_gist.p'
elif ISEXPERIMENT2:
    path_to_all_res = './all_res_exp2.p'
else:
    path_to_all_res = './all_res.p'        
    if not os.path.isfile(path_to_all_res):
        path_to_all_res = '/home/student/l/lkaufhol/fixdur/analysis/all_res.p'

all_res = pickle.load(open(path_to_all_res))

all_res['memory_left_xy']  = [np.array_str(p)[1:-1] for p in all_res['memory_left_xy']]
all_res['memory_right_xy'] = [np.array_str(p)[1:-1] for p in all_res['memory_right_xy']]

all_res['dispX']  = [np.array_str(np.array(p))[1:-1] for p in all_res['dispX']]
all_res['dispY']  = [np.array_str(np.array(p))[1:-1] for p in all_res['dispY']]

all_res['fixX']   = [np.array_str(np.array(p))[1:-1] for p in all_res['fixX']]
all_res['fixY']   = [np.array_str(np.array(p))[1:-1] for p in all_res['fixY']]
#del all_res['memory_left_xy']
#del all_res['memory_right_xy']

panda_all_res = DataFrame(all_res)
#panda_all_res = panda_all_res.drop('dispX',1);
#panda_all_res = panda_all_res.drop('dispY',1);
#panda_all_res = panda_all_res.drop('fixX',1);
#panda_all_res = panda_all_res.drop('fixY',1);



pandas2ri.activate()


#base = importr('base')
#base.save(panda_all_res,file='all_res_exp2-v2.RData')


#rDat = pandas2ri.py2ri_pandasdataframe(panda_all_res)
ro.globalenv['data'] = panda_all_res


if ISFIXDURGIST:
    ro.r(''' save(data,file='all_res_gist.RData') ''')    
elif ISEXPERIMENT2:
    ro.r(''' save(data,file='all_res_exp2.RData') ''')    
    #rDat.to_csvfile('all_res_gist.csv')
else:
    ro.r(''' save(data,file='all_res.RData') ''')
    #rDat.to_csvfile('all_res.csv')

