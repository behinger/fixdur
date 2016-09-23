# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 18:05:43 2016

@author: 01
"""
home = '/net/store/nbp/users/jwu/fixdur/analysis/saliency/'
import os
if not os.path.isdir(home):
    home = 'C:/Users/01/fixdur/analysis/saliency/'

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def plot_feature_corr(data):
    """ correlation heatmaps """
    feat = ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']
    featCurr = [f + 'Curr' for f in feat] 
    plt.figure()
    sns.heatmap(data[feat].corr())
    plt.figure()
    sns.heatmap(data[featCurr].corr())
    
def plot_regression(data, var):
    """ hexbin + regression line with marginals """
    for x in var:
        #plt.figure()
        figure = sns.jointplot(x, 'choicetime', data=data, kind='hex')
        sns.regplot(x, 'choicetime', data=data, lowess=True, ax=figure.ax_joint, scatter=False)
        plt.savefig(home+'figures/hex_reg_%s.svg'%x)

def plot_sub(data, var):
    """ regression line for each subject """    
    # standardize the data within subject
    data['choicetimeNorm'] = data.groupby(['subject']).choicetime.transform(lambda x: x-np.mean(x))   
    for x in var:    
        sns.lmplot(x, 'choicetime', hue='subject', col='subject', col_wrap=7, data=data, lowess=True,  scatter_kws={'color':'grey','alpha':0.1}, line_kws={'color':'black','alpha':1})
        plt.savefig(home+'figures/subject_%s_sep.pdf'%x)
        #sns.lmplot(x, 'choicetimeNorm', data=data, lowess=True, scatter_kws={'color':'grey','alpha':0.1}, line_kws={'color':'black','alpha':1})   
        #plt.savefig(home+'figures/POM/subject_%s_mean.pdf'%x)
    return data
    
def urban_vs_noise(data):
    """ compare distributions of feature values for diff. conditions """
    noise = data[data.stimulus_type == 'noise']
    urban = data[data.stimulus_type == 'urban']
    for f in feat:
        plt.figure()
        plt.hist([noise[f], urban[f]], 100, label=['noise', 'urban']) 
        plt.legend()
        plt.title(f)

feat = ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']
featCurr = [f + 'Curr' for f in feat] 

def hist_feat(data, feat):
    for f in feat:    
        plt.figure()
        sns.distplot(data.loc[:, f], kde=False, ax=ax)
        #plt.savefig(home + 'figures/features_distribution/%s.svg'%f)
        #plt.savefig(home + 'figures/features_distribution/%s.png'%f)
    plt.close('all')

def hist_feat_all(data, feat):
    fig, axes = plt.subplots(nrows=3, ncols=3)        
    for level in range(3):    
        for ax, f in zip(axes[level], feat[level*3:level*3+3]):
            fig = sns.distplot(data.loc[:, f], kde=False, ax=ax)
    plt.savefig(home + 'figures/distribution_univariate/all.svg')
    
def choicetime_dist(data):
    sns.distplot(data.loc[:, 'choicetime'])
    single = data.loc[data.NumOfBubbles=='1']
    multi = data.loc[data.NumOfBubbles!='1']
    plt.figure()
    sns.distplot(single.loc[:, 'choicetime'])
    plt.figure()
    sns.distplot(multi.loc[:, 'choicetime'])
    single.choicetime.describe()
    multi.choicetime.describe()
    import scipy.stats 
    scipy.stats.ttest_ind(single.choicetime, multi.choicetime, equal_var=False)
    