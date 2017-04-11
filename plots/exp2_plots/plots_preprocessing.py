#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 19:19:43 2017

@author: jschepers
"""
import numpy as np
from matplotlib import pyplot as plt
from pandas import DataFrame
#all_res = pickle.load(open(path_to_all_res))


'''
all_res['memory_left_xy']  = [np.array_str(p)[1:-1] for p in all_res['memory_left_xy']]
all_res['memory_right_xy'] = [np.array_str(p)[1:-1] for p in all_res['memory_right_xy']]

panda_all_res = DataFrame(all_res)


#fig, axs = plt.subplots(ncols=5,nrows=5,sharey=True, figsize=(21, 12))

for k,subset in panda_all_res.groupby('subject'):
    
    x = [np.array(f)-b for f,b in zip(subset['fixX'],subset['bubbleX']) if f]
    y = [np.array(f)-b for f,b in zip(subset['fixY'],subset['bubbleY']) if f]
    x = np.concatenate(x)
    y = np.concatenate(y)
    #ax=axs[int(k)]
    fig = plt.figure()
    
    plt.hexbin(x,y,gridsize=210)
    plt.xlim(xmin=-200, xmax=200)
    plt.ylim(ymin=-200, ymax=200)
    plt.title(subset['subject'].iloc[1] + ' %.1f%%'%(100*np.mean(np.sqrt(np.array(x)**2 + np.array(y)**2)<77)))
    np.mean(subset['badLoc'])
    #plt.plot([0], [0], 'b.', markersize=77.0)
    ax = fig.add_subplot(1,1,1)
    circ = plt.Circle((0,0), radius=77, color='w', fill=False)
    ax.add_patch(circ)
    
'''
# Plot: When is a subject looking outside a bubble? (x,y relative to bubble centre over time for one subject)

import scipy

# extract forced onset and forcedFixtime for subject 11
fo_11 = all_res['forced_onset'][all_res['subject']=='11']
#ft_11 = all_res['plannedForcedFix'][all_res['subject']=='11']
ft_11 = all_res['forcedFixtime'][all_res['subject']=='11']
# extract foveated previous for subject 11
fpo_11 = []
for i,elem in enumerate(all_res['foveated_prev_onset']):
    if all_res['subject'][i] == '11' and all_res['whitecondition'][i] == True:
        fpo_11.append(elem)
    elif all_res['subject'][i] == '11' and all_res['whitecondition'][i] == False:
        fpo_11.append(np.nan)

# extract white bubble for subject 11       
wo_11 = []
for i,elem in enumerate(all_res['forced_onset']):
    if all_res['subject'][i] == '11' and all_res['whitecondition'][i] == True:
        wo_11.append(elem-200)
    elif all_res['subject'][i] == '11' and all_res['whitecondition'][i] == False:
        wo_11.append(np.nan)
        
#fpo_11 = [elem for i,elem in enumerate(all_res['foveated_prev_onset']) if all_res['subject'][i] == '11' and all_res['whitecondition'][i] == True]
#fpo_11 = all_res['foveated_prev_onset'][all_res['subject']=='11']
#wo_11 = [elem-200 for i,elem in enumerate(all_res['forced_onset']) if all_res['subject'][i] == '11' and all_res['whitecondition'][i] == True]
#fpo_11 = fpo_11[fpo_11 != -997]
#wo_11 = [on-200 for on in fo_11]

# load sample data for subject 11
sample_data = scipy.io.loadmat('/net/store/nbp/projects/fixdur/data_exp2/11/11_sample_data.mat')
sample_data = sample_data['sample_data']

# Extract bubble coordinates for subject 11
bubbleX_11 = all_res['bubbleX'][all_res['subject']=="11"]
bubbleY_11 = all_res['bubbleY'][all_res['subject']=="11"]

# Compute indeces for forced_fixation time windows in sample_data
ind={}
time_windows = {}
x_fix = {}
y_fix = {}

plt.figure()

for period in range(3):
    if period == 0:
        start = fpo_11
        end = wo_11
        color = 'r'
        label = 'prev_foveated'
    elif period == 1:
        start = wo_11
        end = fo_11
        color = 'g'
        label = 'white_bubble'
    elif period == 2:
        start = fo_11
        end = fo_11 + ft_11
        color = 'k'
        label = 'forced_fixtime'
        #label = 'planned_forced_fixtime'
    
    ind[period] = {}
    
    for i in range(len(sample_data[0])):
        ind[period][i] = (np.array(sample_data[0][i][1]) > start[:]) & (np.array(sample_data[0][i][1]) < end[:])
    
    time_windows[period] = {}
    x_fix[period] = {}
    y_fix[period] = {}

    # Extract time points and x- and y-coordinates for the time_windows (#time_windows = len(fo_11))
    #for trial_ind in range(len(ind)):
    for trial_ind in range(29,30):
        for f in range(len(start)):
        #time_windows[f] = []
        #x_fix[f] = []
        #y_fix[f] = []
            if sum(ind[period][trial_ind][:,f]) != 0:
                time_windows[period][f] = sample_data[0][trial_ind][1][ind[period][trial_ind][:,f]]
                x_fix[period][f] = sample_data[0][trial_ind][2][ind[period][trial_ind][:,f]]
                y_fix[period][f] = sample_data[0][trial_ind][3][ind[period][trial_ind][:,f]]
            else:
                continue
#ind = (np.array(sample_data[0][0][1]) > fo_11[:]).ravel() & (np.array(sample_data[0][:][1]) < (fo_11[:]+ft_11[:])).ravel()


#plt.plot(sample_data[0][trial_ind][1],sample_data[0][trial_ind][2])
#for period in range(1):
    
    # Plot x-coordinate of fixations (relative to bubble centre) over time for different time windows (foveated_prev,white and forced_fixTime)
    # also include line for bubble centre and bubble borders
    
    for tw in x_fix[period].keys():#range(621,636):
        
        #plt.subplot(str('33'+str(tw%10)))
        x_fix_cen = [fix-bubbleX_11[tw] for fix in x_fix[period][tw]]
        plt.plot(time_windows[period][tw],x_fix_cen,color=color,label=label if tw == x_fix[period].keys()[0] else "")
        #plt.plot(time_windows[tw],bubbleX,'k',label='bubbleX')
        #plt.plot(time_windows[tw],upper,'r',label='bubbleX+77')
        #plt.plot(time_windows[tw],lower,'r',label='bubbleX-77')
        
        bubbleX = np.zeros(len(time_windows[period][tw]))
        bubbleX[:] = bubbleX_11[tw]
        upper = np.zeros(len(time_windows[period][tw]))
        #upper[:] = bubbleX_11[tw]+77
        upper[:] = 77
        lower = np.zeros(len(time_windows[period][tw]))
        #lower[:] = bubbleX_11[tw]-77
        lower[:] = -77


        plt.plot(time_windows[period][tw],np.zeros(len(time_windows[period][tw])),'k')#,label='bubbleX')
        plt.plot(time_windows[period][tw],upper,'r')#,label='bubbleX+77')
        plt.plot(time_windows[period][tw],lower,'r')#,label='bubbleX-77')
        #plt.ylim((-250,250))
        plt.xlabel('Time')
        plt.ylabel('fixX (relative to bubble centre)')
        plt.title('Subject 11, Trial 29')
        plt.legend()
plt.show()

# Compare difference between ForcedFixtime and PlannedForcedFixtime for all subjects
plt.figure()
subjects = list(set(all_res['subject']))
#subjects= ['20']
for s in subjects:
    diff_subject = all_res['plannedForcedFix'][all_res['subject']==s]-all_res['forcedFixtime'][all_res['subject']==s]
    plt.plot(diff_subject,label=s)
    plt.legend()

# Compare difference between ForcedFixtime and PlannedForcedFixtime for white and normal condition    
diff_normal = all_res['plannedForcedFix'][all_res['whitecondition']==False]-all_res['forcedFixtime'][all_res['whitecondition']==False]
diff_white = all_res['plannedForcedFix'][all_res['whitecondition']==True]-all_res['forcedFixtime'][all_res['whitecondition']==True]

plt.figure('Normal vs. white condition')
plt.plot(diff_normal,'x',label='normal')
#plt.figure('White condition')
plt.plot(diff_white,'x',label='white')
plt.legend()