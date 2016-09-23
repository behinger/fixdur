# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 13:10:03 2016

@author: 01
"""

home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/'

import os
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/saliency/'
    
import sys
sys.path.insert(0, home) # enables import from working directory

import pca
#import plot
import lme

import pandas as pd
import pickle
import rpy2.robjects as ro
#import matplotlib.pyplot as plt

feat = ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']
featCurr = [f + 'Curr' for f in feat]   
  
def load_df(path):
    data = pd.DataFrame(pickle.load(open(path,'rb')))
    return data
    
def pca_all(data):
    """ run pca on the entire dataset with both next and current bubble features
        and return two dataframes: nexT (splitted PC values, NumOfBubbles, 
        chosenBubbleX), curr (PC calues, NumOfBubbles)
    """
    # split feat+dispX on separate rows
    splitted = split_and_combine(data)
    # append featCurr (9 cols) to the splitted dataset (10 cols)
    curr = pca.missing_values(data[featCurr], 'id0Curr')
    curr.columns = [c[:-4] for c in curr.columns]
    splittedAll = splitted.append(curr) # dispX filled up with NaN for curr
    # apply pca on the combined dataset
    PCs = pca.apply_pca(splittedAll, bubbles='next', n_components=6, figure='no')            
    # separate the curr bubbles from next bubbles 
    curr_len = curr.shape[0]
    pc_curr = PCs[-curr_len:]
    pc_next = PCs[:-curr_len]
    # add other variablels that are needed for later
    pc_next.loc[:, 'dispX'] = splitted.loc[:, 'dispX']      
    pc_next = pc_next.join(data.loc[:, ['NumOfBubbles', 'chosenBubbleX']])
    pc_curr = pc_curr.join(data.loc[:, ['NumOfBubbles']])
    return pc_next.pipe(set_index), pc_curr, PCs, splittedAll  

def split(col):
    """ split the each entry in this column (which is a list with n elements) 
        onto n rows; return the new column """
    # dispX is a R vector & has to be converted to a list before applying pd.Series
    if col.name in ['dispX']:
        col = col.apply(list)
    s = col.apply(pd.Series, 1).stack()
    s.index = s.index.droplevel(-1)
    s.name = col.name
    return s

def split_and_combine(data):
    """ for each feature split the list entries onto single rows and combine
        the new rows with the old ones with .join; return a df where each entry
        in a feature list is on a separate line and other information are 
        retained """
    columns = feat + ['dispX']
    for i,f in enumerate(columns):
        if i == 0 :
            result = split(data[f])
        else:
            result = pd.concat([result, split(data[f])], axis=1)   
            #result.index.names = ['Idx', 'Num']
    #return data.drop(columns, axis=1).join(result)
    return result    

def set_index(data):
    """ multiindexing, level 1 == chosen/not chosen """
    data.index = [data.index, data.dispX==data.chosenBubbleX]
    data = data.drop(['dispX', 'chosenBubbleX'], axis=1)
    return data
        
#def splitted_PCs(data, n=5, figure='no'):
#    """ split list entries of the feature values on single rows and apply pca
#        on the splitted values; return only the PCs with both original index 
#        and boolean index indicating whether the bubble is chosen """        
#    return (data
#            .pipe(split_and_combine)
#            .join(data['chosenBubbleX'])
#            .pipe(set_index)
#            .pipe(pca.apply_pca, bubbles='next', n_components=n, figure=figure)
#            )
        
## single bubbles --------------------------------------------------------------

#def get_diff(grouped, data):
#    """ calculate the difference between the PCs_next and PCs_curr """
#    diff = grouped.get_group('next').ix[:, 0:5] - grouped.get_group('curr').ix[:, 0:5]
#    diff = diff.abs() # explained variance lme, abs: 0.004, else 0.0008
#    columns = [col + 'diff' for col in diff.columns]
#    data[columns] = diff
#    return data
    
def single_bubble(data, pc_next, pc_curr):
    pc_next = pc_next.loc[pc_next.NumOfBubbles=='1']
    pc_curr = pc_curr.loc[pc_curr.NumOfBubbles=='1']
    data = data.loc[data.NumOfBubbles=='1']
    pc_curr.columns = [col + 'curr' for col in pc_curr.columns]
    pc_next.columns = [col + 'next' for col in pc_next.columns]
    pc_next.index = pc_next.index.droplevel(-1)
    data = pd.concat([data, pc_next, pc_curr], axis=1)
    data = pca.missing_values(data, 'PC1curr')
    return data

# multibubbles ----------------------------------------------------------------     

def diff(data):
    """ calculate the mean of the not chosen bubbles for each PC and 
        the difference between this mean and the chosen bubble """
    grouped = data.groupby(level=[0,1])
    meanNotChosen = grouped.mean() 
    grouped = meanNotChosen.groupby(level=0)
    return grouped.first() - grouped.last()
    
def multi_bubble(data, pc_next):
    """ main function: fit data of multi-bubbles trials to lme """
    data = data.loc[data.NumOfBubbles!='1']
    pc_next = pc_next.loc[pc_next.NumOfBubbles!='1']
    difference = diff(pc_next)    
    #data = pd.concat([data.reset_index(), difference.reset_index()], axis=1, ignore_index=True)
    data = pd.concat([data, difference], axis=1)
    return data
    
def chosen_bubble(data, pc_next):
    """ main function: fit data of multi-bubbles trials to lme with PCs of the
        chosen bubbles as fixed effect """
    data = data.loc[data.NumOfBubbles!='1']
    pc_next = pc_next.loc[pc_next.NumOfBubbles!='1']
    #splitted = splitted_PCs(data)  
    chosen = pc_next.groupby(level=0).first()   
    data = pd.concat([data, chosen], axis=1)
    #mres, mres_null = lme.lme(data)
    return data#, mres
    
def multi_chosen(data, pc_next):
    """ main function: fit data of multi-bubbles trials with PCs of the chosen 
        bubbles and the difference between them and the not chosen ones as
        fixed effects """
    data = data.loc[data.NumOfBubbles!='1']
    pc_next = pc_next.loc[pc_next.NumOfBubbles!='1']
    #splitted = splitted_PCs(data)  
    difference = diff(pc_next) 
    difference.columns = [x + 'diff' for x in difference.columns]
    chosen = pc_next.groupby(level=0).first()   
    data = pd.concat([data, chosen, difference], axis=1)
    #mres, mres_null = lme.lme(data)
    return data#, mres
    
def chosen_all(data, pc_next):
    """ main function: fit data of all trials to lme with PCs of the
        chosen bubbles as fixed effect """
    #splittedAll = splitted_PCs(data, 5)  
    chosen = pc_next.groupby(level=0).first()   
    data = pd.concat([data, chosen], axis=1)
    #mres, mres_null = lme.lme(data)
    return data#, mres
    
    
def construct_df():   
    file_data = 'data_complete.p'
    data = load_df(home + file_data) 
    pc_next, pc_curr, pcs, splitted = pca_all(data)
    #pcs_ct = pcs.join(data.loc[:, 'choicetime'])    
    #plot_regression(pcs_ct, pcs.columns)
    single = single_bubble(data, pc_next, pc_curr)
    multi = multi_bubble(data, pc_next)
    chosen = chosen_bubble(data, pc_next)
    m_chosen = multi_chosen(data, pc_next)
    a_chosen = chosen_all(data, pc_next)
    return data, single, multi, chosen, m_chosen, a_chosen

def main():
    data, single, multi, chosen, m_chosen, a_chosen = construct_df()
    mres_s = lme.lme(single)
    mres_m = lme.lme(multi)
    mres_c = lme.lme(chosen)
    mres_mc = lme.lme(m_chosen)
    mres_ac = lme.lme(a_chosen)
    
def plot_figures():
    import seaborn as sns
    import matplotlib.pyplot as plt
    
    """ correlation matrix of features on all values: """
    sns.heatmap(splitted[feat].corr())    
    """ explained variance ratio plot: """
    PCs = pca.apply_pca(splitted, bubbles='next', n_components=9, figure='yes')
    """ distribution histgrams: """
    hist_feat_all(splitted, feat)    
    hist_feat_all(pcs, pcs.columns)
    """ PC vs. choicetime: """ 
    pcs_ct = pcs.join(data.loc[:, 'choicetime'])
    plot.plot_regression(pcs_ct, pcs.columns)