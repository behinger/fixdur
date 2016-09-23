# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 11:35:01 2015

@author: lkaufhol
"""
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter
from resmat import flatten_list
from numpy import mean,median 
from scipy.interpolate import UnivariateSpline
from scipy import stats
import tools
import cPickle as pickle

MAT = 154
PPD = 50

path_to_resmat = '/home/student/l/lkaufhol/fixdur/analysis/'
all_res = pickle.load(open(path_to_resmat+'all_res.p'))
cleaned_res = tools.cut_structure(all_res,all_res['goodFix']==True)

def get_single_subject(all_res,subject):
    res_idx = all_res['subject']==subject
    res = {};
    for key in all_res:    
        res[key] = (all_res[key][res_idx])
    return res
    
def makeGaussian(size, fwhm, center=None):
    """ Make a square gaussian kernel.
 
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """
 
    x = np.arange(0, size, 1, float)
    y = x[:,np.newaxis]
    
    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]
    
    return np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)
    
def dist_from_bubble_center_simp(all_res):
    res = tools.cut_structure(all_res,all_res['goodFix']==True)
    x_samples = []; y_samples = []
    for a in range(len(res['fixX'])):
        for fix in res['fixX'][a]:
            x_samples.append(fix - (res['bubbleX'][a]-MAT/2))
        for fix in res['fixY'][a]:
            y_samples.append(fix - (res['bubbleY'][a]-MAT/2))
    dist = []   
    for a in range(len(x_samples)):
        dist.append(math.sqrt((x_samples[a]-MAT/2)**2 + (y_samples[a]-MAT/2)**2))
    plt.figure()
    plt.hist(dist,100,color='k')
    plt.xlabel("Distance from Bubble Center [Pixel]")
    plt.ylabel("Count [#]")
    plt.axvline(np.mean(dist),color='r',label='mean = '+"%.2f" % np.mean(dist))
    plt.axvline(np.median(dist),color='g',label='median = '+"%.2f" % np.median(dist))
    plt.legend()
	   
    return dist
    
    
def dist_from_bubble_center(all_res):
    res = tools.cut_structure(all_res,all_res['goodFix']==True)
    x_samples1 = []; y_samples1 = []
    x_samples2 = []; y_samples2 = []
    for a in range(len(res['fixX'])):
        #first fixation
        if len(res['fixX'][a])==1:
            for fix in res['fixX'][a]:
                x_samples1.append(fix - (res['bubbleX'][a]-MAT/2))
            for fix in res['fixY'][a]:
                y_samples1.append(fix - (res['bubbleY'][a]-MAT/2))
        if len(res['fixX'][a])>1:
            #first fixation
            x_samples1.append(res['fixX'][a][0] - (res['bubbleX'][a]-MAT/2))
            y_samples1.append(res['fixY'][a][0] - (res['bubbleY'][a]-MAT/2))
            #subsequent fixation
            for fix in res['fixX'][a][1:]:
                x_samples2.append(fix - (res['bubbleX'][a]-MAT/2))
            for fix in res['fixY'][a][1:]:
                y_samples2.append(fix - (res['bubbleY'][a]-MAT/2))
    dist1 = []  
    dist2 = []
    for a in range(len(x_samples1)):
        dist1.append(math.sqrt((x_samples1[a]-MAT/2)**2 + (y_samples1[a]-MAT/2)**2)) 
    for a in range(len(x_samples2)):
        dist2.append(math.sqrt((x_samples2[a]-MAT/2)**2 + (y_samples2[a]-MAT/2)**2)) 
    #gauss comparison
    fwhm = 60 #pix
    gauss_samp = np.random.multivariate_normal(mean=[0,0],cov=[[(fwhm/2.355)**2,0],[0,(fwhm/2.355)**2]],size=1000000)
    gauss_samp = np.transpose(gauss_samp)
    gauss_samp = np.sqrt((gauss_samp[0]**2 + (gauss_samp[1])**2))
    #plot
    plt.figure()
    hist1, bin_edges1 = np.histogram(dist1,100, normed = True)
    hist2, bin_edges2 = np.histogram(dist2,100, normed = True)
    hist3, bin_edges3 = np.histogram(gauss_samp,100, normed = True)
    plt.plot(np.convolve(bin_edges1,[0.5,0.5],'valid'), hist1, color='b',label ='First Fixation, mean = '+"%.2f" % np.mean(dist1))
    plt.plot(np.convolve(bin_edges2,[0.5,0.5],'valid'), hist2, color='r',label = 'Subsequent Fixations, mean = '+"%.2f" % np.mean(dist2))
    plt.plot(np.convolve(bin_edges3,[0.5,0.5],'valid'), hist3, color='g',label = 'Bubble Mask, mean = '+"%.2f" % np.mean(gauss_samp))
    plt.plot(np.mean(dist1),0.002,'*',color='b',markersize=10)
    plt.plot(np.mean(dist2),0.002,'*',color='r',markersize=10)
    plt.plot(np.mean(gauss_samp),0.002,'*',color='g',markersize=10)
    plt.xlim((0,77))
    plt.ylim((0,0.03))
    #plt.title('Distribution of Distances of Fixations on the Bubble from Bubble Center')
    plt.xlabel("Distance from Bubble Center [Pixel]")
    plt.ylabel("Probablity")
    plt.legend()
    
    return dist1,dist2,gauss_samp
    

def bubble_fdm(res,subjects=0,subject=0,counter = 0):
    fwhm=0.1
    scale_factor=1
    e_y = np.arange(0, np.round(scale_factor*MAT+1))
    e_x = np.arange(0, np.round(scale_factor*MAT+1))
    x_samples = []; y_samples = []
    for a in range(len(res['fixX'])):
        for fix in res['fixX'][a]:
            x_samples.append(fix - (res['bubbleX'][a]-MAT/2))
        for fix in res['fixY'][a]:
            y_samples.append(fix - (res['bubbleY'][a]-MAT/2))
    samples = np.array(zip((scale_factor*x_samples), (scale_factor*y_samples)))
    (hist, _) = np.histogramdd(samples, (e_x, e_y))
    kernel_sigma = fwhm * PPD * scale_factor
    kernel_sigma = kernel_sigma / (2 * (2 * np.log(2)) ** .5)
    fdm = gaussian_filter(hist, kernel_sigma, order=0, mode='constant')
    
    if subjects == 0:
        plt.figure()
        plt.imshow(fdm)
        plt.title('Fixation Desity Map on Bubble')
    else:
        plt.subplot(7,5,counter)
        #plt.subplot(2,2,counter)
        plt.imshow(fdm)
        plt.gray()
        #titel = ['A','B','C','D']
        #plt.title('Subject '+titel[counter-1])
        plt.colorbar()
    #import seaborn as sns    
    #sns.jointplot(np.array(x_samples),np.array(y_samples),xlim=(0,MAT),ylim=(0,MAT),kind='kde')
        
    
def bubble_fdm_all(all_res,subjects):
    counter = 0
    fig, axes = plt.subplots(9,4)
    #fig, axes = plt.subplots(1,3)
    for ax in axes.flat:
        res = tools.cut_structure(all_res,all_res['subject']==subjects[counter])
        fwhm=0.1
        scale_factor=1
        e_y = np.arange(0, np.round(scale_factor*MAT+1))
        e_x = np.arange(0, np.round(scale_factor*MAT+1))
        x_samples = []; y_samples = []
        for a in range(len(res['fixX'])):
            for fix in res['fixX'][a]:
                x_samples.append(fix - (res['bubbleX'][a]-MAT/2))
            for fix in res['fixY'][a]:
                y_samples.append(fix - (res['bubbleY'][a]-MAT/2))
        samples = np.array(zip((scale_factor*x_samples), (scale_factor*y_samples)))
        (hist, _) = np.histogramdd(samples, (e_x, e_y))
        kernel_sigma = fwhm * PPD * scale_factor
        kernel_sigma = kernel_sigma / (2 * (2 * np.log(2)) ** .5)
        fdm = gaussian_filter(hist, kernel_sigma, order=0, mode='constant')
        #im = ax.imshow(fdm,vmin=0,vmax=0.56)
        im = ax.imshow(fdm,vmin=0,vmax=0.75)
        #plt.gray()
        counter+=1
        
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im,cax=cbar_ax)
    plt.show()
    #for subject in subjects:
    #    res = get_single_subject(all_res,subject)       
    #    bubble_fdm(res,subjects,subject,counter)
    #    counter +=1
        
def bubble_fdm_4(all_res,subjects):
    counter = 1
    subjects = ['8','27','28','29']
    plt.figure()
    plt.title("Fixation Density Maps on Bubble")
    for subject in subjects:
        res = get_single_subject(all_res,subject)       
        bubble_fdm(res,subjects,subject,counter)
        counter +=1
    #plt.colorbar()
        
def desity_plot(res):
    import tools
    import seaborn as sns
    #res = tools.cut_structure(res,res['choicetime']<500)
    #res = tools.cut_structure(res,res['forcedFixtime']<1500)
    sns.jointplot(res['forcedFixtime'][res['goodFix']==True],res['choicetime'][res['goodFix']==True],xlim=(0,1500),ylim=(0,500),kind='hex')

def normalized(all_res):
    import seaborn as sns
    import tools
    res = tools.cut_structure(all_res,all_res['goodFix']==True)
    (h,edges) = np.histogramdd((res['forcedFixtime'],res['choicetime']),(range(0,1400,20),range(0,400,5)))
    (h,edges) = np.histogramdd((res['forcedFixtime'],res['choicetime']),(np.logspace(0,np.log(400),num=50),range(0,400,5)))
    h_norm = np.empty(h.shape)
    for a in range(h.shape[0]):
        h_norm[a] = h[a]/(0.0000000001+sum(h[a]))
    plt.figure()
    fig, ax = plt.subplots()
    #plt.imshow(h_norm,interpolation='none')
    ax.set_xscale('log')
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.0f'))
    plt.xlim((10,1400))
    plt.pcolor(edges[0],edges[1],np.transpose(h_norm))    
    plt.clim(0,0.1)
    plt.colorbar()
    plt.xlabel('log(ForcedFixTime)')
    plt.ylabel('Choice Time')
    plt.titel('ForcedFix vs. Choice with normalized bin-sizes for ForcedFix')
   
def angle_from_last_bubble(all_res,doPlot=1):
    import pandas
    from math import pi
    
    dat = pandas.DataFrame(all_res)
    ang = 180/pi*np.arctan2(np.diff(dat['bubbleY']),np.diff(dat['bubbleX']))

    if doPlot == 1:
        plt.figure()
        plt.hist(ang,100)
        plt.xlabel('Angle between current and last bubble in Degree')
        plt.show()
    return ang
    
def bubble_fdm_one_side(all_res,subjects,right):
    import tools
    counter = 1
    plt.figure()
    for subject in subjects:
        res = get_single_subject(all_res,subject)       
        ang = angle_from_last_bubble(res,doPlot=0)
        if right:
            ang = ang>0
        else:
            ang = ang<0
        res = tools.cut_structure(res,ang)       
        bubble_fdm(res,subjects,subject,counter)
        counter +=1
    

    

        
def linreg(all_res,subjects):
    slopes = []
    intercepts = []
    p_values = []
    r_values = []
    std_errs = []
    for subject in subjects:
        res = get_single_subject(all_res,subject) 
        x = res['forcedFixtime'][res['goodFix']==True]
        y = res['choicetime'][res['goodFix']==True]
        slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(x),y)
        slopes.append(slope)
        intercepts.append(intercept)
        r_values.append(r_value)
        p_values.append(p_value)
        std_errs.append(std_err)
    #plots
    plt.figure()
    for a in range(len(subjects)):    
        plt.plot(np.exp(np.arange(0,8)),np.arange(0,8)*slopes[a]+intercepts[a],alpha=0.5)
    plt.plot(np.exp(np.arange(0,8)),np.arange(0,8)*np.mean(slopes)+np.mean(intercepts),linewidth=2.0,color='k',linestyle='dashed',label='mean')
    plt.xlabel('ForcedFixTime')
    plt.ylabel('ChoiceTime')
    plt.legend()
    plt.figure()
    for a in range(len(subjects)):    
        plt.plot(np.arange(0,8),np.arange(0,8)*slopes[a]+intercepts[a],alpha=0.5)
    plt.plot(np.arange(0,8),np.arange(0,8)*np.mean(slopes)+np.mean(intercepts),linewidth=2.0,color='k',linestyle='dashed',label='mean')
    plt.xlabel('log(ForcedFixTime)')
    plt.ylabel('ChoiceTime')
    plt.legend() 
    
    return slopes, intercepts, p_values, r_values, std_errs
    
def whole_image_fdm(res):
    fwhm=0.5 #full width at half maximum of the Gaussian kernel used for convolution of the fixation frequency map.
    scale_factor=1 #scale factor for the resulting fdm. Default is 1. Scale_factor must be a float specifying the fraction of the current size.
    e_y = np.arange(0, np.round(scale_factor*1080+1))
    e_x = np.arange(0, np.round(scale_factor*1920+1))
    samples = np.array(zip((scale_factor*flatten_list(res['fixY'])), (scale_factor*flatten_list(res['fixX']))))
    (hist, _) = np.histogramdd(samples, (e_y, e_x))
    kernel_sigma = fwhm * PPD * scale_factor
    kernel_sigma = kernel_sigma / (2 * (2 * np.log(2)) ** .5)
    fdm = gaussian_filter(hist, kernel_sigma, order=0, mode='constant')
    plt.figure()
    plt.imshow(fdm)

def detection_timing_pred(res):
    plt.figure()
    plt.hist(res['fixstart'][res['pred']==True]-res['forced_onset'][res['pred']==True],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset (Only Pred)")
    plt.axvline(mean(res['fixstart'][res['pred']==True]-res['forced_onset'][res['pred']==True]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['pred']==True]-res['forced_onset'][res['pred']==True]),color= 'r',label ='median')
    plt.legend()
    plt.show()
    
def detection_timing_start(res):
    plt.figure()
    plt.hist(res['fixstart'][res['pred']==False]-res['forced_onset'][res['pred']==False],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset (Only Start)")
    plt.axvline(mean(res['fixstart'][res['pred']==False]-res['forced_onset'][res['pred']==False]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['pred']==False]-res['forced_onset'][res['pred']==False]),color= 'r',label ='median')
    plt.legend()
    plt.show()
    
def detection_timing(res):
    plt.figure()
    plt.hist(res['fixstart']-res['forced_onset'],bins=10000,range=(-100,100))
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart']-res['forced_onset']),color= 'g', label='mean')
    plt.axvline(median(res['fixstart']-res['forced_onset']),color= 'r',label ='median')
    plt.legend()
    plt.show()
   
def detection_timing_per_num_bubble(res):
    plt.figure()
    plt.subplot(2,3,1)
    plt.hist(res['fixstart'][res['NumOfBubbles']==1]-res['forced_onset'][res['NumOfBubbles']==1],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart'][res['NumOfBubbles']==1]-res['forced_onset'][res['NumOfBubbles']==1]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['NumOfBubbles']==1]-res['forced_onset'][res['NumOfBubbles']==1]),color= 'r',label ='median')
    plt.title('1')    
    plt.subplot(2,3,2)
    plt.hist(res['fixstart'][res['NumOfBubbles']==2]-res['forced_onset'][res['NumOfBubbles']==2],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart'][res['NumOfBubbles']==2]-res['forced_onset'][res['NumOfBubbles']==2]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['NumOfBubbles']==2]-res['forced_onset'][res['NumOfBubbles']==2]),color= 'r',label ='median')
    plt.title('2') 
    plt.subplot(2,3,3)
    plt.hist(res['fixstart'][res['NumOfBubbles']==3]-res['forced_onset'][res['NumOfBubbles']==3],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart'][res['NumOfBubbles']==3]-res['forced_onset'][res['NumOfBubbles']==3]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['NumOfBubbles']==3]-res['forced_onset'][res['NumOfBubbles']==3]),color= 'r',label ='median')    
    plt.title('3')
    plt.subplot(2,3,4)
    plt.hist(res['fixstart'][res['NumOfBubbles']==4]-res['forced_onset'][res['NumOfBubbles']==4],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart'][res['NumOfBubbles']==4]-res['forced_onset'][res['NumOfBubbles']==4]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['NumOfBubbles']==4]-res['forced_onset'][res['NumOfBubbles']==4]),color= 'r',label ='median')    
    plt.title('4') 
    plt.subplot(2,3,5)
    plt.hist(res['fixstart'][res['NumOfBubbles']==5]-res['forced_onset'][res['NumOfBubbles']==5],500)
    plt.title("Time Diff ETSaccEnd - ForcedFixOnset")
    plt.axvline(mean(res['fixstart'][res['NumOfBubbles']==5]-res['forced_onset'][res['NumOfBubbles']==5]),color= 'g', label='mean')
    plt.axvline(median(res['fixstart'][res['NumOfBubbles']==5]-res['forced_onset'][res['NumOfBubbles']==5]),color= 'r',label ='median')    
    plt.title('5') 
    plt.legend()
    plt.show()

    
def forcedFixVSChoice(res):
    plt.figure()
    plt.subplot(2,3,1)
    plt.plot(res['forcedFixtime'],res['choicetime'],'cx')
    plt.title("all data")
    plt.subplot(2,3,2)
    plt.plot(res['forcedFixtime'][res['badLocExceptFirst']==False],res['choicetime'][res['badLocExceptFirst']==False],'cx')
    plt.title("first fix may not be on bubble")
    plt.subplot(2,3,3)
    plt.plot(res['forcedFixtime'][res['badLoc']==False],res['choicetime'][res['badLoc']==False],'cx')
    plt.title("all fix have to be on bubble")
    plt.subplot(2,3,4)
    plt.plot(res['forcedFixtime'][res['goodFix']==True],res['choicetime'][res['goodFix']==True],'cx')
    plt.title("all fix on bubble & not more than 1 saccade til next bubble")
    plt.subplot(2,3,5)
    plt.plot(res['forcedFixtime'][res['goodFixExceptFirst']==True],res['choicetime'][res['goodFixExceptFirst']==True],'cx')
    plt.title("first fix may not be on bubble & not more than 1 saccade til next bubble")
    plt.subplot(2,3,6)    
    plt.plot(res['forcedFixtime'][res['bubbleNum']!=0],res['choicetime'][res['bubbleNum']!=0],'cx')
    plt.title("test")


def runMean(x,y,binEdges):
    #binEdges = np.array(binEdges)
    out = np.zeros(len(binEdges)-1)
    n = np.zeros(len(binEdges)-1)
    for k in range(len(binEdges)-1):
        idx = np.logical_and(x>=binEdges[k], x<binEdges[k+1])
        out[k] = np.mean(y[idx])
        n[k] = np.sum(idx)
    return out,n
    
    
def forcedFixVSChoice_average(res,subject):
    x = res['forcedFixtime'][res['goodFix']==True]
    y = res['choicetime'][res['goodFix']==True]
    s = UnivariateSpline(x,y,s=100,k=1)
    xs = x
    ys = s(xs)
    plt.figure()  
    plt.plot(x,y,'cx')
    plt.plot(xs,ys,'.')
    plt.title("ForcedFix vs. Choice for subject: "+subject)  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.show()
    
    
def forcedFixVSChoice_per_num_bubble(res):
    forced = [[],[],[],[],[]]
    choice = [[],[],[],[],[]]
    for idx in np.intersect1d(np.transpose(np.where(res['goodFix2']==True)),np.transpose(np.where(res['NumOfBubbles']==1))):
        forced[0].append(res['forcedFixtime'][idx])
        choice[0].append(res['choicetime'][idx])
    for idx in np.intersect1d(np.transpose(np.where(res['goodFix2']==True)),np.transpose(np.where(res['NumOfBubbles']==2))):
        forced[1].append(res['forcedFixtime'][idx])
        choice[1].append(res['choicetime'][idx])
    for idx in np.intersect1d(np.transpose(np.where(res['goodFix2']==True)),np.transpose(np.where(res['NumOfBubbles']==3))):
        forced[2].append(res['forcedFixtime'][idx])
        choice[2].append(res['choicetime'][idx])
    for idx in np.intersect1d(np.transpose(np.where(res['goodFix2']==True)),np.transpose(np.where(res['NumOfBubbles']==4))):
        forced[3].append(res['forcedFixtime'][idx])
        choice[3].append(res['choicetime'][idx])
    for idx in np.intersect1d(np.transpose(np.where(res['goodFix2']==True)),np.transpose(np.where(res['NumOfBubbles']==5))):
        forced[4].append(res['forcedFixtime'][idx])
        choice[4].append(res['choicetime'][idx])
    plt.figure()
    plt.title("ForcedFix vs. Choice for 1 subject")
    plt.subplot(2,3,1) 
    plt.plot(forced[0],choice[0],'bx')
    plt.title("1 bubble")  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.xlim([0,2000])
    plt.ylim([0,1000])
    plt.subplot(2,3,2) 
    plt.plot(forced[1],choice[1],'bx')
    plt.title("2 bubbles")  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.xlim([0,2000])
    plt.ylim([0,1000])
    plt.subplot(2,3,3) 
    plt.plot(forced[2],choice[2],'bx')
    plt.title("3 bubbles")  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.xlim([0,2000])
    plt.ylim([0,1000])
    plt.subplot(2,3,4) 
    plt.plot(forced[3],choice[3],'bx')
    plt.title("4 bubbles")  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.xlim([0,2000])
    plt.ylim([0,1000])
    plt.subplot(2,3,5) 
    plt.plot(forced[4],choice[4],'bx')
    plt.title("5 bubbles")  
    plt.xlabel("Forced Fixation Time in ms")
    plt.ylabel("Choice Time in ms")
    plt.xlim([0,2000])
    plt.ylim([0,1000])
    plt.show()
    
def forcedVsCho_sorted(res):
    #intersection of goodLoc and stimulus_types/memory
    plt.figure()
    plt.subplot(2,2,1)
    idx = [res['badLoc']==False] and [res['stimulus_type']=='urban']
    plt.plot(res['forcedFixtime'][idx],res['choicetime'][idx],'oc')
    plt.title('urban')
    plt.subplot(2,2,2)
    idx = [res['badLoc']==False] and [res['stimulus_type']=='noise']
    plt.plot(res['forcedFixtime'][idx],res['choicetime'][idx],'oc')
    plt.title('noise')
    plt.subplot(2,2,3)
    idx = [res['badLoc']==False] and [res['memory']==True]
    plt.plot(res['forcedFixtime'][idx],res['choicetime'][idx],'oc')
    plt.title('memory correct')
    plt.subplot(2,2,4)
    idx = [res['badLoc']==False] and [res['memory']==False]
    plt.plot(res['forcedFixtime'][idx],res['choicetime'][idx],'oc')
    plt.title('memory incorrect')