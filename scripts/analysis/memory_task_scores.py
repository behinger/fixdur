# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 15:50:15 2016

@author: behinger
"""

    
from pandas import DataFrame

import pickle
import tools
import os
import numpy as np
import re
import scikits.bootstrap as bootstrap
ISFIXDURGIST = True

if ISFIXDURGIST:
    path_to_all_res = '/home/student/b/behinger/Documents/fixdur/analysis/all_res_gist.p'
else:
    path_to_all_res = '/home/student/b/behinger/Documents/fixdur/analysis/all_res.p'        
    if not os.path.isfile(path_to_all_res):
        path_to_all_res = '/home/student/l/lkaufhol/fixdur/analysis/all_res.p'

all_res = pickle.load(open(path_to_all_res))

noiseR = np.array([re.search('noise',x)!=None for x in all_res['memory_right_stim']])
noiseL = np.array([re.search('noise',x)!=None for x in all_res['memory_left_stim']])
correct= np.array(all_res['memory'])
df = DataFrame([noiseR,noiseL, correct, np.array(all_res['subject']),all_res['gist']],index=['nR','nL','correct','subject','gist']).transpose()


bothNoise=(df[(df.nR == True) &(df.nL==True)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
noNoise=(df[(df.nR == False) &(df.nL==False)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
oneNoise=(df[(df.nR != df.nL)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)



print('bothNoise:',np.mean(bothNoise),bootstrap.ci(bothNoise),np.std(bothNoise))
print('noNoise:',np.mean(noNoise),bootstrap.ci(noNoise),np.std(noNoise))
print('oneNoise:',np.mean(oneNoise),bootstrap.ci(oneNoise),np.std(oneNoise))

if ISFIXDURGIST:

    bothNoiseGist=(df[(df.nR == True) &(df.nL==True)&(df.gist==True)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    noNoiseGist=(df[(df.nR == False) &(df.nL==False)&(df.gist==True)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    oneNoiseGist=(df[(df.nR != df.nL)&(df.gist==True)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    bothNoiseNoGist=(df[(df.nR == True) &(df.nL==True)&(df.gist==False)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    noNoiseNoGist=(df[(df.nR == False) &(df.nL==False)&(df.gist==False)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    oneNoiseNoGist=(df[(df.nR != df.nL)&(df.gist==False)].groupby('subject').agg(lambda x:np.mean(0+x.correct)).correct)
    
    
    
    print('bothNoise:',np.mean(bothNoiseGist),bootstrap.ci(bothNoiseGist),np.std(bothNoiseGist))
    print('noNoise:',np.mean(noNoiseGist),bootstrap.ci(noNoiseGist),np.std(noNoiseGist))
    print('oneNoise:',np.mean(oneNoiseGist),bootstrap.ci(oneNoiseGist),np.std(oneNoiseGist))
    
    print('bothNoise:',np.mean(bothNoiseNoGist),bootstrap.ci(bothNoiseNoGist),np.std(bothNoiseNoGist))
    print('noNoise:',np.mean(noNoiseNoGist),bootstrap.ci(noNoiseNoGist),np.std(noNoiseNoGist))
    print('oneNoise:',np.mean(oneNoiseNoGist),bootstrap.ci(oneNoiseNoGist),np.std(oneNoiseNoGist))