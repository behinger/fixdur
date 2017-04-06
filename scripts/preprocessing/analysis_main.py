# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 11:34:01 2015

@author: lkaufhol,behinger

#2015 - 12 - 10, added support for fixdur gist
"""

import numpy as np
import cPickle as pickle
import scipy.io
import resmat
reload(resmat)
#import tools, only needed for plots
import os
import collections

MAT = 154
PPD = 50

ISFIXDURGIST = False
ISEXPERIMENT2 = True
#paths

if ISFIXDURGIST:
    #path_to_fixdur_files = '/net/store/nbp/projects/fixdur/data_gist/'
    #if not os.path.isdir(path_to_fixdur_files):
    path_to_fixdur_files = '/home/student/b/behinger/Documents/fixdur/data_gist/'    
    
elif ISEXPERIMENT2:
    #path_to_fixdur_files = '/home/student/j/jschepers/thesis/fixdur_git/data/experiment2/'   
    path_to_fixdur_files = '/net/store/nbp/projects/fixdur/data_exp2/'
else:
    path_to_fixdur_files = '/net/store/nbp/projects/fixdur/data/'
    if not os.path.isdir(path_to_fixdur_files):
        path_to_fixdur_files = '/home/student/b/behinger/Documents/fixdur/data/'    


#all_res = dict(dispX = [],dispY = [],forcedTimeDiff=[],sacc_detect=[],badLocOLD=[],image=[],logFix=[],subject=[],forced_onset=[],trialNum=[],bubbleNum=[],bubbleY=[],bubbleX=[],fixstart=[],choicetime=[],fixend=[],forcedFixtime=[],numFixPerBubble=[],badLoc=[],badLocExceptFirst=[],badSaccade=[],fixX=[],fixY=[],goodFix=[],goodFixExceptFirst=[],pred=[],NumOfBubbles=[],stimulus_type=[],memory=[],noSaccade=[],goodFix2=[],plannedForcedFix=[],prevFixY=[],prevFixX=[],nextFixY=[],nextFixX=[])
all_res = collections.defaultdict(list)

if ISFIXDURGIST:
  # 4 & 9 ET problems, subjects moved a lot and calibrationw as really bad
  # 12 early stop because subject was too tired
    subjects = ['1','2','3','5','6','7','8','10','11','13']
    #subjects = ['1']
elif ISEXPERIMENT2:
    subjects = ['1','2','3','4','6','7','8','9','11','12','15','16','17','18','20','21','22','23','24','25']
    #subjects = ['8','9','11','12','15','16','17','18','20','21','22','23','24','25']
else:
  #subject 0: old updating method, subject 2: didn't look at bubbles, 7 et crashed -> no complete data set, 
#14 no complete data set #17 et chrashed -> pickle file missing, 19 = trialsnum weird, 24 2 trials missing. 25 1 trial missing
#8only 105 trials, 9 - 1 trial missing

    subjects = ['1','3','4','5','6','10','11','12','13','15','16','20','21','22','23','24','25','26','27','28','29','30','8','9','18','31','32','33','34','35','36','37','38','39','40']
    age = [36,24,19,20,25,20,21,21,27,23,18,27,20,23,20,20,23,42,34,21,27,19,23,21,25,19,21,22,33,22,20,25,27,25,25]
    sex = ['m','f','f','f','f','m','f','m','m','m','f','f','f','m','f','f','f','f','f','f','m','f','f','f','f','f','f','f','m','f','f','f','f','f','f']
num_trials = []
#subjects = ['32']


def get_data_trial_num(natural_trial_num):
    idx = []
    for num in natural_trial_num:
        if data[(num-1)*2][1]['trial'] == num:
            idx.append((num-1)*2)
        else:
            Warning('Wrong trial number')
        if ((data[(num-1)*2][1]['img'] == data[(num-1)*2+1]['correct'][0]) or (data[(num-1)*2][1]['img'] == data[(num-1)*2+1]['right_bubble'][0])):
            idx.append((num-1)*2+1)
        else:
            Warning('Wrong trial number')
    return idx

for subject in subjects:
    #check if et_data and sample data already exist, if not start matlab script
    if not (os.path.exists(path_to_fixdur_files+str(subject)+'/'+str(subject)+'_et_data.mat')):
        #os.system('matlab -nodisplay -r ../analysis/create_array_from_edf.m')
        Warning('First run analysis/create_array_from_edf.m with subject '+subject)
    
    
    '''load data'''
    data = pickle.load((open(path_to_fixdur_files+str(subject)+'/'+str(subject))))
    et_data = scipy.io.loadmat(path_to_fixdur_files+str(subject)+'/'+str(subject)+'_et_data.mat')
    et_data = et_data['et_data']
    et_data = et_data[0]
    num_trials.append(len(et_data))
    sample_data = scipy.io.loadmat(path_to_fixdur_files+str(subject)+'/'+str(subject)+'_sample_data.mat')
    sample_data = sample_data['sample_data']
    rand = np.load(path_to_fixdur_files+str(subject)+'/rand_'+str(subject)+'.npy')
    
    if (subject == '17') and not ISFIXDURGIST and not ISEXPERIMENT2:
        data2 = pickle.load((open(path_to_fixdur_files+str(subject)+'/'+str(subject)+'88')))
        for elem in data2:
            data.append(elem)
            
    if (subject == '6') and ISEXPERIMENT2:
        data2 = pickle.load((open(path_to_fixdur_files+str(subject)+'/'+str(subject)+'33')))
        for elem in data2:
            data.append(elem)
    if (subject == '20') and ISEXPERIMENT2:
        data2 = pickle.load((open(path_to_fixdur_files+str(subject)+'/'+str(subject)+'65')))
        for elem in data2:
            data.append(elem)
            
            
    '''remove bad trials from data'''
    idx = []
    if not ISFIXDURGIST and not ISEXPERIMENT2:
        if subject == '3':
            idx = get_data_trial_num([40])
        if subject == '5':
            idx = get_data_trial_num([117])
        if subject == '6':
            idx = get_data_trial_num([89])
        if subject == '10':
            idx = get_data_trial_num([30,74])
        idx.sort(reverse=True)
        for item in idx:
            data.pop(item)
    
    '''get result matrix'''
    # res = dict(fixstart=[],choicetime=[],fixend=[],forcedFixtime=[],numFixPerBubble=[],badLoc=[],badLocExceptFirst=[],badSaccade=[],fixX=[],fixY=[],goodFix=[],goodFixExceptFirst=[])
    #res,start_x,start_y,end_x,end_y = resmat.get_res(data,et_data,sample_data)
    res = resmat.get_res(data,et_data,sample_data,ISGIST=ISFIXDURGIST,ISEXPERIMENT2=ISEXPERIMENT2)
    
    #stuff for quantification
    
    ''' add subject number '''
    for bubble in range(len(res['bubbleNum'])):
        all_res['subject'].append(subject)
        
    for key in res:  
        for bubble in range(len(res[key])):
            all_res[key].append(res[key][bubble])
        

''' Convert List back to NP array '''
for key in all_res:
    all_res[key] = np.array(all_res[key])
    
if ISFIXDURGIST:
    pass
    pickle.dump(all_res,open("all_res_gist.p","w")) #XXX
elif ISEXPERIMENT2:
    pickle.dump(all_res,open("all_res_exp2.p","w")) #XXX
else:
    pass
    pickle.dump(all_res,open("all_res.p","w")) #XXX

#%% quantification of different "cleaning methods"
'''
diffLoc = []
diffgoodFixall = []
diffgoodFixwith1 = [] 
for a in range(len(subjects)):
    diffLoc.append(goodLocExceptFirst[a] - goodLoc[a])
    diffgoodFixall.append(goodLoc[a] - goodFix[a])
    diffgoodFixwith1.append(goodLocExceptFirst[a] - goodFixExceptFirst[a])

means = [np.mean(num_bubbles),np.mean(goodLocExceptFirst),np.mean(goodLoc),np.mean(diffLoc),np.mean(diffgoodFixwith1),np.mean(diffgoodFixall)]
stds = [np.std(num_bubbles),np.std(goodLocExceptFirst),np.std(goodLoc),np.std(diffLoc),np.std(diffgoodFixwith1),np.std(diffgoodFixall)]
labels = ('all','goodLoc1','goodLoc','goodLoc1-goodLoc','goodLoc1-goodFix1','goodLoc-goodFix')

import matplotlib.pyplot as plt    
plt.figure()
ind,width = np.arange(len(means)),0.3
fig,ax = plt.subplots()
rect = ax.bar(ind+width,means,width,color='y',yerr=stds)
ax.set_xticklabels(labels)
plt.show()
'''

#how often were die 3 methods to get the fixated bubble used
def get_sacc_detection(all_res):
    cleaned_res = tools.cut_structure(all_res,all_res['goodFix']==True)
    #cleaned_res = all_res
    fix_in_bubble = tools.cut_structure(cleaned_res,cleaned_res['sacc_detect']=='start_in_bubble')
    saccade_to_bubble = tools.cut_structure(cleaned_res,cleaned_res['sacc_detect']=='pred_in_bubble')
    no_saccade = tools.cut_structure(cleaned_res,cleaned_res['sacc_detect']=='random')
    res_dict = dict()
    res_dict['fix_in_bubble'] = float(len(fix_in_bubble['bubbleNum']))/float(len(cleaned_res['bubbleNum']))*100
    res_dict['saccade_to_bubble'] = float(len(saccade_to_bubble['bubbleNum']))/float(len(cleaned_res['bubbleNum']))*100
    res_dict['no_saccade'] = float(len(no_saccade['bubbleNum']))/float(len(cleaned_res['bubbleNum']))*100
    
    return res_dict

#how many bubbles are removed during cleaning 
#remove badDiff as a criterion from goodFix in resmat.py to get percentages before the last exclusion step   
def get_percentages(all_res):
    good_Loc = tools.cut_structure(all_res,all_res['badLoc']==False)
    good_fix = tools.cut_structure(all_res,all_res['goodFix']==True)
    choice_bigger_100 = tools.cut_structure(all_res,good_Loc['choicetime']>100)
    choice_bigger_100_good_fix = tools.cut_structure(all_res,good_fix['choicetime']>100)
    more_than_1_fix = tools.cut_structure(all_res,good_fix['numFixPerBubble']>1)
    neg_forcedFix = tools.cut_structure(all_res,good_Loc['forcedFixtime']<=0)
    badDiff = tools.cut_structure(all_res,abs(good_fix['forcedTimeDiff'])>40)
    
    perc_dict = dict()    
    perc_dict['good_Loc'] = float(len(good_Loc['bubbleNum']))/float(len(all_res['bubbleNum']))*100
    perc_dict['good_fix_all'] = float(len(good_fix['bubbleNum']))/float(len(all_res['bubbleNum']))*100
    perc_dict['good_fix'] = float(len(good_fix['bubbleNum']))/float(len(good_Loc['bubbleNum']))*100
    perc_dict['choice_100'] = float(len(choice_bigger_100['bubbleNum']))/float(len(good_Loc['bubbleNum']))*100
    perc_dict['choice_100_goodfix'] = float(len(choice_bigger_100_good_fix['bubbleNum']))/float(len(good_fix['bubbleNum']))*100
    perc_dict['more_than_1_fix'] = float(len(more_than_1_fix['bubbleNum']))/float(len(good_Loc['bubbleNum']))*100
    perc_dict['neg_forcedFix'] = float(len(neg_forcedFix['bubbleNum']))/float(len(good_Loc['bubbleNum']))*100
    perc_dict['badDiff'] = float(len(badDiff['bubbleNum']))/float(len(good_fix['bubbleNum']))*100

    return perc_dict    

#how mny fixations per subject contribute to the fdms    
def get_num_fix(all_res,subjects):
    cleaned_res = tools.cut_structure(all_res,all_res['goodFix']==True)
    num_fix = []
    num_fix_dict = dict()
    for subject in subjects:
        res = tools.cut_structure(cleaned_res,cleaned_res['subject']==subject)
        if len(tools.flatten_list(res['fixX'])) == len(tools.flatten_list(res['fixY'])):
            num_fix.append(len(tools.flatten_list(res['fixX'])))
        else:
            Warning('Number of X and Y Fixations dont match')
    num_fix_dict['min'] = min(num_fix)
    num_fix_dict['max'] = max(num_fix)
    num_fix_dict['mean'] = np.mean(num_fix)
    print num_fix
    return num_fix_dict

#how many bubbles per subject are included    
def get_num_bubble(all_res,subjects):
    cleaned_res = tools.cut_structure(all_res,all_res['goodFix']==True)
    num_bubbles = []
    num_bubbles_dict = dict()
    for subject in subjects:
        res = tools.cut_structure(cleaned_res,cleaned_res['subject']==subject)
        num_bubbles.append(len(res['bubbleNum']))
    num_bubbles_dict['min'] = min(num_bubbles)
    num_bubbles_dict['max'] = max(num_bubbles)
    num_bubbles_dict['mean'] = np.mean(num_bubbles)
    
    return num_bubbles_dict    
    
#how does forced_fix differ from planned forced_fix
def get_forced_fix_times(all_res):
    cleaned_res = tools.cut_structure(all_res,all_res['goodFix']==True)
    cleaned_res = tools.cut_structure(cleaned_res,cleaned_res['plannedForcedFix']>0)
    #cleaned_res = tools.cut_structure(cleaned_res,cleaned_res['plannedForcedFix']-cleaned_res['forcedFixtime'])
    diff = cleaned_res['forcedTimeDiff']
    #diff_smaller_40 = np.where(abs(diff)<40)
    import matplotlib.pyplot as plt
    plt.figure()
    plt.subplot(1,2,1)
    plt.hist(diff,1000,color='k')
    #plt.title('Emprical Forced-Fixation-Time - Planned Forced-Fixation-Time')
    plt.xlabel('Difference between empircal and planned Forced-Fixation-Time [ms]')
    plt.ylabel('count [#]')
    plt.subplot(1,2,2)
    plt.plot(cleaned_res['forcedFixtime'],cleaned_res['plannedForcedFix'],'.',color='k')
    plt.xlabel('Empirical Forced-Fixation-Time [ms]')
    plt.ylabel('Planned Forced-Fixation-Time [ms]')
    
    return diff

#%% plots
#
#plots.whole_image_fdm(res)
#plots.detection_timing(res)
#plots.detection_timing_pred(res)
#plots.detection_timing_start(res)
#plots.forcedFixVSChoice(res)
#plots.forcedFixVSChoice_average(res,subject)
#plots.forcedFixVSChoice_per_num_bubble(res)
#plots.detection_timing_per_num_bubble(res)
#plots.forcedVsCho_sorted(res)
#plots.desity_plot(all_res)
#plots.bubble_fdm(res)

''' FDM PLOTS '''
'''
#plots.bubble_fdm_all(all_res,subjects)
plots.bubble_fdm(res)
plots.bubble_fdm_all(tools.cut_structure(all_res,all_res['NumOfBubbles']==1),subjects)
plots.bubble_fdm_one_side(tools.cut_structure(all_res,all_res['NumOfBubbles']==1),subjects,right=0)
plots.bubble_fdm_one_side(tools.cut_structure(all_res,all_res['NumOfBubbles']==1),subjects,right=1)
plots.angle_from_last_bubble(all_res)
'''

''' MODEL PLOTS'''
#slopes, intercepts, p_values, r_values, std_errs = plots.linreg(all_res,subjects)
'''
x = res['forcedFixtime'][res['goodFix']==True]
y = res['choicetime'][res['goodFix']==True]
bins = np.linspace(0,8,num=20)
#import math
#bins = np.logspace(np.log(30),np.log(2000),num=10,base=math.e)
m,n = plots.runMean(np.log(x),y,bins)
plt.plot(np.exp(bins[range(len(bins)-1)]),m)
plt.plot(bins[range(len(bins)-1)],m)
plt.show()

from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(np.log(x),y)
plt.plot(np.arange(0,8),np.arange(0,8)*slope+intercept)
'''
