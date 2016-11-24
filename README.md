## Probing the temporal dynamics of the exploration-exploitation dilemma of eye movements


### Overview
This github repository documents the code and data (bioRxiv forthcoming).


### Code

#### Prepare:
To fully reconstruct all data you need matlab (to convert Eyelink EDF to .mat), python 2.7 (to preprocess) and R (for statistics) and several packages (ggplot, ddply, rstan,...).

Do this to clone the repository:
'''git clone https://github.com/behinger/fixdur'''

If you do want to rerun the whole preprocessing pipeline, go to https://osf.io/wphbd/files and download the Raw-Eyetracking files into 'fixdur/data/experiment1'. The preprocessed data is included in the github repository (fixdur/cache/data/).

For further information consult [this readme.md](fixdur/scripts/preprocessing/readme.md)

##### Analysis
Run the R-Script [main_analysis.R](fixdur/scripts/analysis/main_analysis.R)
The plots should and information on the project used in the paper should appear.
