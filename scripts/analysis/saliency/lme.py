# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:10:20 2016

@author: jwu
"""
home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/'

import os
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/saliency/'
    
import sys
sys.path.insert(0, home) # enables import from working directory

import pca
from scipy import stats
import statsmodels.api as sm
import numpy as np

formula_prev = 'choicetime~\
forcedFixtime+\
log_forcedFixtime+\
stimulus_type+\
lag1_choicetime+\
lag1_forcedFixtime+\
log_nextBubbleDist+\
log_prevBubbleDist+\
angleDiff+\
sin_nextBubbleAngle+cos_nextBubbleAngle+\
sin2_nextBubbleAngle+cos2_nextBubbleAngle+\
sin_prevBubbleAngle+cos_prevBubbleAngle+\
sin2_prevBubbleAngle+cos2_prevBubbleAngle+\
trialNum'
#(1+log_forcedFixtime+C(stimulus_type)+log_NumOfBubbles|subject)'

def get_formula(data, mode):
    """ generate the formula for different modes """
    if mode == 'prev': # Lilli's
        formula = formula_prev
    elif mode in ['next', 'curr', 'diff']:
        PCs = [col for col in data if (col[:2]=='PC' and col[-4:]==mode)]
        formula = formula_prev + '+' + '+'.join(PCs)
    elif mode == 'all':        
        PCs = [col for col in data if col[:2]=='PC']
        formula = formula_prev + '+' + '+'.join(PCs)
    elif mode == 'no diff': # this is the one we decided for
        PCs = [col for col in data if 'PC' in col and not('diff' in col)]
        formula = formula_prev + '+' + '+'.join(PCs)
    elif mode == 'null':
        formula = 'choicetime ~ 1'
    return formula
    
def adjust_data_to_formula(data):
    """ MixedLM can't handle missing values, so manuelly drop all rows 
        containing NaNs in one of the predictors """
    factors = formula_prev.split('~')[1].split('+')
    tail = factors[-1].split(':')
    factors = factors[:-1]
    factors.extend(tail)
    factors.remove('stimulus_type')
    for f in factors:
        data = pca.missing_values(data, f) 
    return data
        
def fit_lme(data, mode):
    """ fit data to one of the models and return the modelfit """
    formula = get_formula(data, mode)
    data = adjust_data_to_formula(data)
    md = sm.MixedLM.from_formula(formula, data, groups=data['subject'])
    mdf = md.fit(reml=False) # use ml estimator instead of reml for .llf to get the log-likelihood function value 
    return mdf
    
def explained_variance(mres, mres_null):
    """ calculate the explained variance / R^2 """    
    result = 1 - (np.var(mres.resid) / np.var(mres_null.resid))
    return result

def lrt(null, full):
    lr = 2 * (full.llf - null.llf)
    df = null.df_resid - full.df_resid
    pvalue = stats.chi2.sf(lr, df)
#    print null.llf, null.df_resid
#    print full.llf, full.df_resid
#    print lr
#    print df
#    print pvalue
    return lr, df, pvalue

def lme(data, h0='prev', h1='all'):
    """ fit the models and print the explained variance """
    mres_null = fit_lme(data, h0)
    mres = fit_lme(data, h1)  
    print mres.summary()        
    print 'Explained variance: ' + str(explained_variance(mres, mres_null))
    print
    lrtResult = lrt(mres_null, mres)
    print 'P-value obtained by likelihood ratio test: ' + str(lrtResult)
    print
    return mres