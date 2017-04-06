clear all;
addpath('/home/student/j/jschepers/thesis/fixdur_git/lib/edfread/')

basepath = '/home/student/j/jschepers/thesis/fixdur_git/experiment/experiment2/data';
subjects = {'2','3','4','5'};

for subject_num = subjects
    subject_num = subject_num{1};
    datapath = fullfile(basepath ,subject_num);
    d = dir(fullfile(datapath,'*.EDF'));
    datapath = fullfile(datapath,d(1).name);
    
    % Read EDF
    [data,info] = edfread(datapath,'TRIALID');
end