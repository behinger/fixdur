# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 13:30:16 2015

@author: jwu
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

def unlist_entry(data):
    """ unlist the columns, only works for lists with one element as entries """
    unlist = lambda l: l[0] if len(l) != 0 else None
    unwrap = lambda l: unlist(l) if isinstance(l, list) else l
    data = data.applymap(unwrap)
    return data


def zscore(data):
    """ returns the same result (dataframe) as sklearn.preprocessing.scale 
        (array): data.mean() == 0, data.std() == 1 """
    for f in data.columns:
        temp = (data[f] - data[f].mean())/data[f].std(ddof=0)
        data[f] = temp.copy()
    return data


def pca(data, n, figure):
    """ run pca and print explained variance ratio """
    n_components = n
    pca = PCA(n_components=n_components)
    reduced = pca.fit(data).transform(data)
    reduced = pd.DataFrame(data=reduced, index=data.index, columns=['PC%s'%i for i in range(1, n+1)])
    print('explained variance ratio (first %d components): \n %s \n sum: %.2f'
          %(n_components, str(pca.explained_variance_ratio_), sum(pca.explained_variance_ratio_)))
    if figure == 'yes':
        plot_exp_var(pca.explained_variance_ratio_)
    return reduced

    
def plot_exp_var(exp_var):
    """ plot principal components """
    n = len(exp_var)
    cumulative = np.cumsum(exp_var)    
    fig = plt.figure()
    fig.patch.set_facecolor('white')
    plt.title('Explained Variance by Different Principal Components', fontsize='large')
    plt.ylabel('Percentage of variance explained')
    #plt.xlim(-0.5, n+0.5)
    plt.xticks([i for i in range(0,n)], ['PC%s' %i for i in range(1,n+1)])
    plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], [i*20 for i in range(6)])
    #plt.ylim(-0.1, 1.1)
    line1, = plt.plot(exp_var, '-D', color='dodgerblue', label='explained variance ratio')
    line2, = plt.plot(cumulative, '-o', color='orange', label='cumulative explained variance')
    plt.legend(handles=[line2, line1], loc=7, fontsize='medium')
    plt.show()

def missing_values(data, var):
    isnan = data[np.isnan(data[var])]
    discarded = data.drop(isnan.index, axis=0)
    return discarded
    
def difference(data, feat, featCurr):
    """ calculate the diffenrence between current and next feature values
        for each row """    
    diff = []
    for i in range(len(feat)):
        f = feat[i]
        g = featCurr[i]
        diff.append(data[f] - data[g])
    diff = pd.DataFrame(data=diff)
    diff = diff.abs()
    diff = diff.T    
    return diff

def combine(data, feat, featCurr):
    """ create a dataframe that contains both curr and next below each other
        being in the same columns """
    #diff = difference(data, feat, featCurr)
    result = data[feat].copy()
    result.columns = featCurr
    #result['nextORcurr'] = pd.Series('next', index=result.index)
    temp = data[featCurr].copy()
    #temp['nextORcurr'] = pd.Series('current', index=temp.index)
    #diff.columns = feat
    #result = result.append([data[feat], diff])
    result = result.append(temp)
    return result
    
def apply_pca(data, bubbles, n_components, figure):
    feat = ['id0', 'id1', 'id2', 'idX', 'lumc', 'lums', 'lumt', 'sob', 'sobs']
    featCurr = [f + 'Curr' for f in feat]      
#    data = data.loc[data.NumOfBubbles=='1']
#    data = missing_values(data, 'id0Curr')
#    data = unlist_entry(data)  
    if bubbles == 'next':
        scaled = zscore(data[feat].copy())      
    elif bubbles == 'current':  
        scaled = zscore(data[featCurr].copy())          
    elif bubbles ==  'difference':
        diff = difference(data, feat, featCurr)
        scaled = zscore(diff)  
    elif bubbles == 'combined': 
        comb = combine(data, feat, featCurr)   
        scaled = zscore(comb)      
    else:
        raise Exception('mode not defined, check spelling')
        
    reduced = pca(scaled, n_components, figure)
#    result = pd.concat([data, reduced], axis=1)  
#    return result
    
    if bubbles == 'combined':
        nextORcurr =  pd.concat([pd.Series('next', index=data.index), pd.Series('curr', index=data.index)], axis=0)
        reduced['nextORcurr'] = nextORcurr
        
    return reduced