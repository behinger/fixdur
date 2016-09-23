### Steps to preprocess data and their output
The steps are a bit messy. Basically you need matlab, python and R in order to process the data. The reason is more or less historical, at that point in time EDF files could only be read in in matlab (now a python package is available). Then we tried doing all our processing in python but failed with the mixed models and moved on to R. But other processing later was again done in python. Sorry for the mess.

In order to go from EDF to .p to .RData
1. *create_array_from_edf.m*: Allows to read in the EDF eyetracking files and extracts subjectwise all important information. Saves them in a .mat file
2. *analysis_main.py*: requires *resmat.py* This function adds all preprocessing things e.g. marks trials with multiple saccades etc.
3a. *process_data_in_R.py*: This function runs the *fd_loaddata.R* function on the python pickled dataset. It removes trials that are >3*mad per subject and adds a lot of new features e.g. bubbleangles etc. in the end you get a python pandas data frame
3b. *fd_loaddata.R*: Run this to get the data_frame in R directly.
