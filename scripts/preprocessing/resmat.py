# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 11:34:47 2015

@author: lkaufhol,behinger

# 2015-12-10 added support for gist data
"""

import numpy as np
import collections
import warnings
MAT = 154
PPD = 50

def flatten_list(nested_list):
    return [item for sublist in nested_list for item in sublist]

def get_res(data,et_data,sample_data,ISGIST=False,ISEXPERIMENT2=False):    
    
    
    '''get bubble position'''
    chosen_x = []
    chosen_y = []  
    disp_x = []      
    disp_y = []
    num_bubbles = [] #number of displayed bubbles
    trial_num = []
    bubble_num = [] #number of subtrial
    stimulus_type = [] #urban vs. noise
    memory_correct = []
    gist = []
    memory_right_xy = []
    memory_left_xy = []
    memory_right = []
    memory_left = []
    planned_forced_fix = []
    image = []
    whitecondition = []
    if ISEXPERIMENT2:
        #difference between image and screen
        shiftBubbleX = (1920 - 1280)/2 
        shiftBubbleY = (1080-960)/2
    else:
        MAT = 154 # the bubble size in pixels
        shiftBubbleX = MAT/2+(1920 - 1280)/2
        shiftBubbleY = MAT/2+(1080-960)/2
    for j in range(len(data)):
       
        # check trial_type
        if (np.mod(j,2) == 1):
            if ISEXPERIMENT2 or (data[j]['trial_type'] == 'seq'):
                if ISEXPERIMENT2 == ('trial_type' in data[j].keys()):
                  raise('error, you should have trial_type if it is not experiment2')
                num_subtrial = (len(data[j-1]))
                # take corresponding trail (data[0-1,2-3,4-5, etc.])
                #first bubble for each subtrial
                chosen_x.append(data[j-1][0]['first_bubble'][0]+shiftBubbleX)
                chosen_y.append(data[j-1][0]['first_bubble'][1]+shiftBubbleY)
                trial_num.append(j/2)
                bubble_num.append(-1)
                disp_x.append(data[j-1][0]['first_bubble'][0]+shiftBubbleX)
                disp_y.append(data[j-1][0]['first_bubble'][1]+shiftBubbleY) # BUG until 21.02.2017 there was a bug, and shiftBubbleX was addedhere
                num_bubbles.append(1)
                #stimulus type
                if 'image' in data[j-1][0]['img']:
                    stimulus_type.append('urban')
                if 'noise' in data[j-1][0]['img']:
                    stimulus_type.append('noise')
                image.append(data[j-1][0]['img'])
                #planned_forced_fix.append(data[j-1][0]['planned_disp_time'])
                #memory task correct?
                if data[j]['correct']!='no_memory_task':
                    if not ('trial_type' in data[j].keys()): # Experiment 2, we fixed the switched fields bug from experiment 1/gist!
                        #warnings.warn('FIXME: this after you fixed memory task (adding the image')
                        #memory_left.append(np.nan)
                        #memory_left_xy.append(np.nan)
                        #memory_right.append(np.nan)
                        #memory_right_xy.append(np.nan)
                        # Warning: Experiment 2 has switched labels
                        memory_left.append(data[j]['left_bubble'][1])
                        memory_left_xy.append(data[j]['left_bubble'][0])
                        
                        memory_right.append(data[j]['right_bubble'][1])                                       
                        memory_right_xy.append(data[j]['right_bubble'][0])                    
                        
                        if data[j]['correct']:
                            memory_correct.append(True)
                        else:
                            memory_correct.append(False)
                    else: # Gist and Experiment 1
                        #bug:left_bubble = correct, right_bubble = right_bubble, correct = left_bubble
                        memory_left.append(data[j]['correct'][0])
                        memory_left_xy.append(data[j]['correct'][1])
                        
                        memory_right.append(data[j]['right_bubble'][0])                                       
                        memory_right_xy.append(data[j]['right_bubble'][1])                    
                        if data[j]['left_bubble']:
                            memory_correct.append(True)
                        else:
                            memory_correct.append(False)
                else:
                    memory_left.append('None')
                    memory_left_xy.append([np.nan,np.nan])
                    memory_right.append('None')
                    memory_right_xy.append([np.nan,np.nan])
                    memory_correct.append(np.nan)
                    
                if ISGIST:
                    if data[j]['gist']=='1.0':
                        gist.append(True)
                    else:
                        gist.append(False)
                if ISEXPERIMENT2:
                        if data[j-1][0]['control_condition']==1:
                             whitecondition.append(True)
                        else:
                            whitecondition.append(False)
                #rest of the bubbles for each subtrial
                for b in range(len(data[j-1])-1): #no forced_fixation for last subtrial of each trial (-1)
                    trial_num.append(j/2)
                    bubble_num.append(b)
                    num_bubbles.append(len(data[j-1][b]['disp_bubbles']))
                    #add half of mat size to get center (77)
                    #add difference between image and monitor resolution to chosen_bubble_position (320,60)
                    chosen_x.append(data[j-1][b]['chosen_bubble'][0][0]+shiftBubbleX)
                    chosen_y.append(data[j-1][b]['chosen_bubble'][0][1]+shiftBubbleY)
                    tmp_x = []
                    tmp_y = []
                    for c in range(len(data[j-1][b]['disp_bubbles'])):
                        tmp_x.append(data[j-1][b]['disp_bubbles'][c][0]+shiftBubbleX)
                        tmp_y.append(data[j-1][b]['disp_bubbles'][c][1]+shiftBubbleY)
                    disp_x.append(tmp_x)
                    disp_y.append(tmp_y)
                    #stimulus type
                    if 'image' in data[j-1][b]['img']:
                        stimulus_type.append('urban')
                    if 'noise' in data[j-1][b]['img']:
                        stimulus_type.append('noise')
                    image.append(data[j-1][b]['img'])
                    #memory task correct?
                    #bug:left_bubble = correct, right_bubble = right_bubble, correct = left_bubble
                    
                    if data[j]['correct']!='no_memory_task':
                        if ISEXPERIMENT2: # Experiment 2, we fixed the bug!
                            memory_left.append(data[j]['left_bubble'][0])
                            memory_left_xy.append(data[j]['left_bubble'][1][0])
                        
                            memory_right.append(data[j]['right_bubble'][0])                                       
                            memory_right_xy.append(data[j]['right_bubble'][1][0])                    
                        
                            if data[j]['correct']:
                                memory_correct.append(True)
                            else:
                                memory_correct.append(False)
                        else: # Gist and Experiment 1
                            #bug:left_bubble = correct, right_bubble = right_bubble, correct = left_bubble
                            memory_left.append(data[j]['correct'][0])
                            memory_left_xy.append(data[j]['correct'][1])
                            
                            memory_right.append(data[j]['right_bubble'][0])                                       
                            memory_right_xy.append(data[j]['right_bubble'][1])                    
                            if data[j]['left_bubble']:
                                memory_correct.append(True)
                            else:
                                memory_correct.append(False)
                    else:
                        memory_left.append('None')
                        memory_left_xy.append([np.nan, np.nan])
                        memory_right.append('None')
                        memory_right_xy.append([np.nan,np.nan])
                        memory_correct.append(np.nan)
                    if ISGIST:
                        if data[j]['gist']=='1.0':
                            gist.append(True)
                        else:
                            gist.append(False)
                    if ISEXPERIMENT2:
                        if data[j-1][0]['control_condition']==1:
                            whitecondition.append(True)
                        else:
                            whitecondition.append(False)
                    planned_forced_fix.append(data[j-1][b]['planned_disp_time'])
                #add dummy value for last subtrial, because there is no last forced_fix_time        
                planned_forced_fix.append(-999)                     
    #return chosen_x, num_bubbles
    
    if ISEXPERIMENT2:
        for i in range(len(disp_y)):
            if isinstance(disp_y[i],list):
                for j in range(len(disp_y[i])):
                    disp_y[i][j] = 1080 - disp_y[i][j]
            else:
                disp_y[i] = 1080 - disp_y[i]
                
        for i in range(len(chosen_y)):
            if isinstance(chosen_y[i],list):
                for j in range(len(chosen_y[i])):
                    chosen_y[i][j] = 1080 - chosen_y[i][j]
            else:
                chosen_y[i] = 1080 - chosen_y[i] 
            
    '''get forced_fix_onset and stim_onset from et_meta_data'''
    forced_onset = [] #onset of forced_fix display
    forced_offset = [] #end of forced fix_display/ onset of choise time
    #start and end positions of saccade prediction
    start_x = [] 
    start_y = []
    end_x = []
    end_y = []
    sacc_detection = []
    for j in range(len(et_data)):
        #check trial type
        if np.all(et_data[j]['Displayed_Bubbles'] != '-1'):
            for b in range(len(et_data[j]['Forced_Fix_Onset'])):
                forced_onset.append(et_data[j]['Forced_Fix_Onset'][b][0]) 
                forced_offset.append(et_data[j]['Stimulus_Onset'][b][0])
                sacc_detection.append(et_data[j]['sacc_detection'][b])
                #start_x.append(float(et_data[j]['start_x'][b]))
                #start_y.append(float(et_data[j]['start_y'][b]))
                #end_x.append(float(et_data[j]['end_x'][b]))
                #end_y.append(float(et_data[j]['end_y'][b]))
    
    
    '''get fixation and saccade data from et_data'''
    et_fix_start = []
    et_fix_end = []
    et_fix_x = []
    et_fix_y = []
    et_foveated_prev_onset = []
    et_saccade_end_x = []
    et_saccade_end_y = []
    et_saccade_start_x = []
    et_saccade_start_y = []
    for j in range(len(et_data)):
        #check trial type
        if len(et_data[j]['Forced_Fix_Onset']) > 1:
            et_fix_start.append([k[0] for k in et_data[j]['fix_start']])
            et_fix_end.append([k[0] for k in et_data[j]['fix_end']])
            et_fix_x.append([k[0] for k in et_data[j]['fix_x']])
            et_fix_y.append([k[0] for k in et_data[j]['fix_y']])
            if ISEXPERIMENT2:
                et_foveated_prev_onset.append([k[0] for k in et_data[j]['foveated_prev_onset']])
                
            et_saccade_end_x.append([k[0] for k in et_data[j]['saccade_ex']])
            et_saccade_end_y.append([k[0] for k in et_data[j]['saccade_ey']])
            et_saccade_start_x.append([k[0] for k in et_data[j]['saccade_sx']])
            et_saccade_start_y.append([k[0] for k in et_data[j]['saccade_sy']])
    #flatten lists
    et_fix_start = flatten_list(et_fix_start)
    et_fix_end = flatten_list(et_fix_end)
    et_fix_x = flatten_list(et_fix_x)
    et_fix_y = flatten_list(et_fix_y)
    et_foveated_prev_onset = flatten_list(et_foveated_prev_onset)
    et_saccade_end_x = flatten_list(et_saccade_end_x)
    et_saccade_end_y = flatten_list(et_saccade_end_y)
    et_saccade_start_x = flatten_list(et_saccade_start_x)
    et_saccade_start_y = flatten_list(et_saccade_start_y)
    
    #res = dict(dispX=[],dispY=[],forcedTimeDiff=[],sacc_detect=[],badLocOLD=[],image=[],logFix=[],goodFix2=[],fixstart=[],choicetime=[],fixend=[],forcedFixtime=[],numFixPerBubble=[],badLoc=[],badLocExceptFirst=[],badSaccade=[],fixX=[],fixY=[],goodFix=[],goodFixExceptFirst=[],pred=[],NumOfBubbles=[],stimulus_type=[],memory=[],noSaccade=[],plannedForcedFix=[],prevFixY=[],prevFixX=[],nextFixY=[],nextFixX=[])
    res = collections.defaultdict(list)


    for k,item in enumerate(forced_onset):
        #index of closest fixation start to bubble start
        if bubble_num[k] == -1:
            continue
        
        indEnd = np.where(et_fix_end>forced_offset[k])[0][0]
        res['fixend'].append(et_fix_end[indEnd])
        
        if ISEXPERIMENT2 and whitecondition[k]:
            tmp = abs(et_foveated_prev_onset[k]- np.array(et_fix_start))
        else:
            tmp = abs(item - np.array(et_fix_start))
        tmp = tmp[np.array(et_fix_start)<et_fix_end[indEnd]]
        indStart = np.argmin(tmp)
                                 
        #indStart = np.where(et_fix_start<forced_onset[k])[0][-1]
        res['fixstart'].append(et_fix_start[indStart])

        res['choicetime'].append(et_fix_end[indEnd] - forced_offset[k])
        
        if ISEXPERIMENT2 and whitecondition[k]:
            res['forcedFixtime'].append(forced_offset[k] - item)
        else:
            res['forcedFixtime'].append(forced_offset[k] - et_fix_start[indStart])
            
        if (int(indEnd-indStart+1) == 0):
            raise('No Fixation on Bubble for Bubble Number: '+str(k))
        res['numFixPerBubble'].append(indEnd-indStart+1)

        #badloc is true if fixation not within bubble
        #res['badLoc'].append(not np.all(abs(chosen_x[k] - np.array(et_fix_x[indStart:indEnd+1]))<77) & np.all(abs(chosen_y[k] - np.array(et_fix_y[indStart:indEnd+1]))<77))
        res['badLoc'].append(not np.all(np.sqrt(((chosen_x[k] - np.array(et_fix_x[indStart:indEnd+1]))**2 +(chosen_y[k] - np.array(et_fix_y[indStart:indEnd+1]))**2))<77))
        res['badLocOLD'].append(not np.all(abs(chosen_x[k] - np.array(et_fix_x[indStart:indEnd+1]))<77) & np.all(abs(chosen_y[k] - np.array(et_fix_y[indStart:indEnd+1]))<77))
        #badlocExceptFirst is true if fixations after the first fixation not within bubble 
        #badlocExceptFirst is false (uses distance in x and y, instead of radius/euclidian distance)
        res['badLocExceptFirst'].append(not np.all(abs(chosen_x[k] - np.array(et_fix_x[indStart+1:indEnd+1]))<77) & np.all(abs(chosen_y[k] - np.array(et_fix_y[indStart+1:indEnd+1]))<77))   
        #true if there are more than one saccade until next Forced_Fix_Onset
        if k+1<len(forced_onset):
            if ISEXPERIMENT2 and whitecondition[k]:
                testAgainst = et_foveated_prev_onset[k+1]
            else:
                testAgainst = forced_onset[k+1]
                
            if et_fix_end[indEnd+1] < testAgainst:
                res['badSaccade'].append(True)
            else:
                res['badSaccade'].append(False)
        else:
            res['badSaccade'].append(False)
        #true if there are no saccades between previous bubble offset and onset
        if k-1>=0 and k+1<len(forced_onset):
            if (et_fix_start[indStart] < forced_offset[k-1]) or (forced_offset[k+1]<et_fix_end[indEnd]):
                res['noSaccade'].append(True)
            else:
                res['noSaccade'].append(False)
        else:
            res['noSaccade'].append(False)
        
        
        res['fixX'].append(et_fix_x[indStart:indEnd+1])
        res['fixY'].append(et_fix_y[indStart:indEnd+1])
        
        res['dispX'].append(disp_x[k])
        res['dispY'].append(disp_y[k])
        
        res['goodFix'].append(False)
        res['goodFix2'].append(False)
        res['goodFixExceptFirst'].append(False)
        #res['smallchoice'].append(False)
        #true if prediction is used, false if starting point already in bubble
        if sacc_detection[k] == 'pred_in_bubble':
            res['pred'].append(True)
        else:
            res['pred'].append(False)
        res['NumOfBubbles'].append(num_bubbles[k])
        res['stimulus_type'].append(stimulus_type[k])
        res['memory'].append(memory_correct[k])
        res['memory_left_stim'].append(memory_left[k])
        res['memory_right_stim'].append(memory_right[k])
        res['memory_left_xy'].append(memory_left_xy[k])
        res['memory_right_xy'].append(memory_right_xy[k])
        if ISGIST:
            res['gist'].append(gist[k])
        if ISEXPERIMENT2:
            res['whitecondition'].append(whitecondition[k])
            res['foveated_prev_onset'].append(et_foveated_prev_onset[k])
        res['plannedForcedFix'].append(planned_forced_fix[k])
        res['logFix'].append(np.nan)
        res['image'].append(image[k])
        res['sacc_detect'].append(sacc_detection[k])
        res['forcedTimeDiff'].append(res['forcedFixtime'][-1]-planned_forced_fix[k])
        #res['forcedTimeDiff'].append((forced_offset[k] - et_fix_start[indStart])-planned_forced_fix[k])
        res['prevFixX'].append(et_fix_x[indStart-1])
        res['prevFixY'].append(et_fix_y[indStart-1])
        res['nextFixX'].append(et_fix_x[indEnd+1])
        res['nextFixY'].append(et_fix_y[indEnd+1])
        
  
            
        
    #delete first subtrial    
    res['bubbleNum'] = np.array(bubble_num)[np.array(bubble_num) != -1]
    res['trialNum'] =  np.array(trial_num) [np.array(bubble_num) != -1]    
    res['bubbleX'] =   np.array(chosen_x)  [np.array(bubble_num) != -1]
    res['bubbleY'] =   np.array(chosen_y)  [np.array(bubble_num) != -1]
    res['forced_onset'] = np.array(forced_onset)[np.array(bubble_num) != -1]
    
    #add entry for log of forcedFix
    res['logFix'] = np.log(res['forcedFixtime']) 
    
    #np.arrays
    for listidx in res:
        #print(listidx)
        res[listidx] = np.array(res[listidx])
        
        
        
    #true if all fixations after the first are within bubble and there is no more than one saccade before the next bubble onset
    for idx in np.intersect1d(np.transpose(np.where(res['badLocExceptFirst'] == False)),np.transpose(np.where(res['badSaccade'] == False))):    
        res['goodFixExceptFirst'][idx] = True 
    #true if all fixations are within bubble and there is no more than one saccade before the next bubble onset
    for idx in np.intersect1d(np.transpose(np.where(res['badLoc'] == False)),np.transpose(np.where(res['badSaccade'] == False))):    
        res['goodFix'][idx] = True
    #true if all fixations after within bubble, forced_fix time is positive, choice_time>100, and there was at least 1 saccade between previous offset and current onset of bubble
    for idx in np.intersect1d(np.transpose(np.where(res['badLoc'] == False)),np.transpose(np.where(res['noSaccade'] == False))):    
        res['goodFix2'][idx] = True 
    res['goodFix2'][np.where(res['forcedFixtime']<=0)] = False
    res['goodFix2'][np.where(res['choicetime']<100)] = False
        
    #mark all negative Forced_fix_times
    res['goodFixExceptFirst'][np.where(res['forcedFixtime']<=0)] = False
    res['goodFix'][np.where(res['forcedFixtime']<=0)] = False
    res['goodFix'][np.where(abs(res['forcedTimeDiff'])>40)] = False
    
    #mark all entries where there was no Saccade between bubble offset and next onset
    res['goodFixExceptFirst'][res['noSaccade'] == True] = False
    res['goodFix'][res['noSaccade'] == True] = False
    res['badLocExceptFirst'][res['noSaccade'] == True] = True
    res['badLoc'][res['noSaccade'] == True] = True
    
    #for idx in np.intersect1d(np.transpose(np.where(res['goodFix'] == True)),np.transpose(np.where(res['choicetime'] < 80))):    
    #    res['smallchoice'][idx] = True       
        
    """ check whether bubbleX, bubbleY are contained in dispX, dispY""" # @jwu

    for i in range(len(res['bubbleX'])):
        if res['NumOfBubbles'][i] == 0:
            # Whole Image condition fo experiment 2
            res['dispX'][i] = [-998.]
            res['dispY'][i] = [-998.]
        elif not (res['bubbleX'][i] in res['dispX'][i] and res['bubbleY'][i] in res['dispY'][i]):
            print "Error: chosen bubble is not contained in the list of previously displayed bubbles"
    
        
    return res
    

