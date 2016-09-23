addpath('lib/edfread')

ISGIST = true;
if ISGIST
    basepath = 'data/
%     if isunix
%         basepath = '/home/student/l/lkaufhol/fixdur/data_gist';
%         if ~exist(basepath)
%             basepath = '/home/student/b/behinger/Documents/fixdur/data_gist';
            
%         end
%     end
%     
ba
    
else
    if isunix
        basepath = '/home/student/l/lkaufhol/fixdur/data';
        if ~exist(basepath)
            basepath = '/home/student/b/behinger/Documents/fixdur/data';
        end
        
    end
end
subject_num = '2';
subjects = {'1','2','3','5','6','7','8','10','11','13'}

for subject_num = subjects
    subject_num = subject_num{1}
    datapath = fullfile(basepath ,subject_num);
    d = dir(fullfile(datapath,'*.EDF'));
    datapath = fullfile(datapath,d(1).name);
    
    % Read EDF
    [data,info] = edfread(datapath,'TRIALID');
    
    training = 0;
    if strcmp(data(1).TRIALID.msg,'TRIALID 1000')
        training = 1;
        start = 3;
    else
        training = 0;
        start = 1;
    end
    
    bad_trials = [];
    if ~ISGIST
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
    
    
    for a = start:length(data)
        %if isfield(data(a).DISPLAYED_BUBBLES)
        et_data(a).trial = a-2;
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
        et_data(a).GIST = str2num(data(a).GIST.msg);
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
    if training
        et_data = et_data(3:length(et_data));
    end
    et_data(bad_trials) = [];
    
    
    %data from eyetracker on a sample level
    sample_data = struct('trial',{}, 'time', {}, 'x', {}, 'y', {});
    for a = start:length(data)
        sample_data(a).trial = a-2;
        sample_data(a).time = [];
        sample_data(a).x = [];
        sample_data(a).y = [];
        for b = 1:length(data(a).left.samples.time)
            sample_data(a).time = [sample_data(a).time;data(a).left.samples.time(b)];
            sample_data(a).x = [sample_data(a).x;data(a).left.samples.x(b)];
            sample_data(a).y = [sample_data(a).y;data(a).left.samples.y(b)];
        end
    end
    if training
        sample_data = sample_data(3:length(sample_data));
    end
    sample_data(bad_trials) = [];
    
    
    save([basepath,'/',subject_num,'/',subject_num,'_et_data.mat'],'et_data')
    save([basepath,'/',subject_num,'/',subject_num,'_sample_data.mat'],'sample_data')
    
end
