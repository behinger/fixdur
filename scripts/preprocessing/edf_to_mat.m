addpath('lib/edfread')

ISGIST = false;
ISEXP2 = true;
if ISGIST
    basepath = 'data/experiment_gist';
    subjects = {'1','2','3','5','6','7','8','10','11','13'};
elseif ISEXP2
    %basepath = 'data/experiment2';
    basepath = '/net/store/nbp/projects/fixdur/data_exp2';
    %     subjects = {'1','2','3','4','6',
    subjects = {'7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25'};
    %subjects = {'12','20'}
    subjects = {'1'}
else
    basepath = 'data/experiment1';
    subjects = {'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40'};
end


%%
for subject_num = subjects
    
    subject_num = subject_num{1};
    fprintf('Running subject %s \n',subject_num)
    datapath = fullfile(basepath ,subject_num);
    try
        d = dir(fullfile(datapath,'*.EDF'));
        if length(d)>1
            fprintf('multiple EDF files found, fixing %s \n',subject_num)
            
            [data1,info1] = edfread(fullfile(datapath,d(1).name),'TRIALID');
            [data2,info2] = edfread(fullfile(datapath,d(2).name),'TRIALID');
            
            % sort them
            if str2num(data1(3).TRIALID.msg(end-1:end))> str2num(data2(3).TRIALID.msg(end-1:end))
                data_tmp = data1;
                data1 = data2;
                data2 = data_tmp;
                clear data_tmp
            end
            %concat them
            
                
             f = unique([fieldnames(data1);fieldnames(data2)]);
             data = struct();
             for i = 1:length(f)
                 data(length(data2)+length(data1)).(f{i}) = [];
             end
             
             % fill data 1
             for i = 1:length(data1)
                 for f = fieldnames(data1)'
                     data(i).(f{1}) = data1(i).(f{1});
                 end
             end
             % fill data 2
            for i = 1:length(data2)
                 for f = fieldnames(data2)'
                     data(i+length(data1)).(f{1}) = data2(i).(f{1});
                 end
             end
            
        else
        datapath = fullfile(datapath,d(1).name);
        
        % Read EDF
        [data,info] = edfread(datapath,'TRIALID');
        end
        
        if strcmp(subject_num,'8')
            % we only have data of the second part
            data(1).foveated_prev_onset = [];
            data(1).white_onset = []; 
        end
        if strcmp(subject_num,'12')
            data(66) = []; %it crashed during the last trial, incomplete data
        end
        
    catch e
        e
        fprintf('could not read subject %s \n',subject_num)
        continue
    end
    
    
    
    bad_trials = [];
    if ~ISGIST && ~ISEXP2
        if strcmp(subject_num,'3')
            bad_trials = [bad_trials;40];
        end
        if strcmp(subject_num,'5')
            bad_trials = [bad_trials;117];
        end
        if strcmp(subject_num,'6')
            bad_trials = [bad_trials;89];
        end
        if strcmp(subject_num,'10')
            bad_trials = [bad_trials;30;74];
        end
    end
    %if subject_num =='17'
    %    bad_trials = [bad_trials;39];
    %end
    
    %subject 19: 2*48,3*32,2*28
    
    %% data from eyetracker based on fixation/saccade classification
    et_data = struct('Image',{},'Displayed_Bubbles',{},'Selected_Bubble',{},'Display_Time',{},'Forced_Fix_Onset',{},'Stimulus_Onset',{},'Saccade_offset_subtrial',{},'fix_start',{},'fix_end',{},'fix_x',{},'fix_y',{},'saccade_start',{},'saccade_end',{},'saccade_sx',{},'saccade_sy',{},'saccade_ex',{},'saccade_ey',{},'sacc_detection',{});
    
    training_trials = [];
    %for a = trialSequence
    for a = 1:length(data)
        trial_id = regexp(data(a).TRIALID.msg,'[0-9]+','match');
        trial_id = str2num(trial_id{1,1});
        if trial_id >= 1000
            %if ~isempty(str2num(deblank(data(a).TRIALID.msg(end-3:end))))
            training_trials = [training_trials;a];
            continue
        end
        %if isfield(data(a).DISPLAYED_BUBBLES)
        et_data(a).trial = a;
        et_data(a).fix_start = [];
        et_data(a).fix_end = [];
        et_data(a).fix_x = [];
        et_data(a).fix_y = [];
        et_data(a).saccade_start = [];
        et_data(a).saccade_end = [];
        et_data(a).saccade_sx = [];
        et_data(a).saccade_sy = [];
        et_data(a).saccade_ex = [];
        et_data(a).saccade_ey = [];
        if ISGIST
            et_data(a).GIST = str2num(data(a).GIST.msg);
        end
        et_data(a).Image = data(a).BUBBLE_IMAGE.msg;
        %if displayed bubbles is not empty i.e. sequential trial
        if (strcmp(data(a).DISPLAYED_BUBBLES.msg,'-1') == 0)
            
            %how many subtrials per trial
            num_of_subtrials = size(data(a).DISPLAYED_BUBBLES.msg);
            num_of_subtrials = num_of_subtrials(1);
            %get arrays to store subtrials
            et_data(a).Displayed_Bubbles = [];
            et_data(a).Selected_Bubble = [];
            et_data(a).Display_Time = [];
            et_data(a).Forced_Fix_Onset = [];
            et_data(a).Saccade_offset_subtrial = [];
            et_data(a).Stimulus_Onset = [];
            et_data(a).foveated_prev_onset = [];
            %metadata for saccade detection
            %et_data(a).start_x = [];
            %et_data(a).start_y = [];
            %et_data(a).end_x = [];
            %et_data(a).end_y = [];
            et_data(a).sacc_detection = [];
            %add data for subtrials
            for b =1:num_of_subtrials
                %which bubbles could have been chosen by subject
                et_data(a).Displayed_Bubbles = [et_data(a).Displayed_Bubbles;data(a).DISPLAYED_BUBBLES.msg(b,:)];
                %which bubble did subject choose
                et_data(a).Selected_Bubble = [et_data(a).Selected_Bubble;data(a).CHOSEN_BUBBLE.msg(b,:)];
                %how long was selected_bubble supposed to be displayed
                et_data(a).Display_Time = [et_data(a).Display_Time;str2num(data(a).BUBBLE_DISPLAY_TIME.msg(b,:))];
                %trials(a).Saccade_on_velocity = [trials(a).Saccade_on_velocity;str2num(data(a).SACCADE.msg(b,:))];
                %trials(a).Saccade_onset = [trials(a).Saccade_onset;(data(a).SACCADE.time(b))];
                et_data(a).Forced_Fix_Onset = [et_data(a).Forced_Fix_Onset;data(a).forced_fix_onset.time(b)];
                et_data(a).Saccade_offset_subtrial = [et_data(a).Saccade_offset_subtrial;data(a).saccade_offset.time(b)];
                et_data(a).Stimulus_Onset = [et_data(a).Stimulus_Onset;data(a).stimulus_onset.time(b)];
                if ~isempty(data(a).foveated_prev_onset)
                    if b == 1
                        et_data(a).foveated_prev_onset = [et_data(a).foveated_prev_onset; -996];
                    else
                        et_data(a).foveated_prev_onset = [et_data(a).foveated_prev_onset;data(a).foveated_prev_onset.time(b-1)];
                    end
                else
                    et_data(a).foveated_prev_onset = [et_data(a).foveated_prev_onset;-997];
                end
                %et_data(a).start_x = [et_data(a).start_x;data(a).start_x.msg(b,:)];
                %et_data(a).start_y = [et_data(a).start_y;data(a).start_y.msg(b,:)];
                %et_data(a).end_x = [et_data(a).end_x;data(a).end_x.msg(b,:)];
                %et_data(a).end_y = [et_data(a).end_y;data(a).end_y.msg(b,:)];
                et_data(a).sacc_detection = [et_data(a).sacc_detection;data(a).sacc_detection.msg(b,:)];
                
            end
        else
            et_data(a).Displayed_Bubbles = ['-1'];
        end
        for b = 1:length(data(a).left.fixation.start)
            et_data(a).fix_start = [et_data(a).fix_start;data(a).left.fixation.start(b)];
            et_data(a).fix_end = [et_data(a).fix_end;data(a).left.fixation.end(b)];
            et_data(a).fix_x = [et_data(a).fix_x;data(a).left.fixation.x(b)];
            et_data(a).fix_y = [et_data(a).fix_y;data(a).left.fixation.y(b)];
        end
        for b = 1:length(data(a).left.saccade.start)
            et_data(a).saccade_start = [et_data(a).saccade_start;data(a).left.saccade.start(b)];
            et_data(a).saccade_end = [et_data(a).saccade_end;data(a).left.saccade.end(b)];
            et_data(a).saccade_sx = [et_data(a).saccade_sx;data(a).left.saccade.sx(b)];
            et_data(a).saccade_sy = [et_data(a).saccade_sy;data(a).left.saccade.sy(b)];
            et_data(a).saccade_ex = [et_data(a).saccade_ex;data(a).left.saccade.ex(b)];
            et_data(a).saccade_ey = [et_data(a).saccade_ey;data(a).left.saccade.ey(b)];
        end
    end
    % loop over et_data
    % if et_data(X).fix_start is empty
    % remove it
    % This should only happen in training trials. Check that!
    %et_data = et_data(3:length(et_data));
    et_data([training_trials bad_trials]) = [];
    
    
    %data from eyetracker on a sample level
    sample_data = struct('trial',{}, 'time', {}, 'x', {}, 'y', {});
    for a = 1:length(data)
        
        trial_id = regexp(data(a).TRIALID.msg,'[0-9]+','match');
        trial_id = str2num(trial_id{1,1});
        if trial_id >= 1000
            %if ~isempty(str2num(deblank(data(a).TRIALID.msg(end-3:end))))
            continue
        end
        sample_data(a).trial = a;
        sample_data(a).time = [];
        sample_data(a).x = [];
        sample_data(a).y = [];
        for b = 1:length(data(a).left.samples.time)
            sample_data(a).time = [sample_data(a).time;data(a).left.samples.time(b)];
            sample_data(a).x = [sample_data(a).x;data(a).left.samples.x(b)];
            sample_data(a).y = [sample_data(a).y;data(a).left.samples.y(b)];
        end
    end
    %sample_data = sample_data(3:length(sample_data));
    sample_data([training_trials bad_trials]) = [];
    
    
    save([basepath,'/',subject_num,'/',subject_num,'_et_data.mat'],'et_data')
    save([basepath,'/',subject_num,'/',subject_num,'_sample_data.mat'],'sample_data')
    
end
