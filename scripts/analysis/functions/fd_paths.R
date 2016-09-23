library(plyr)
library("lme4")
library("ggplot2")
library('magrittr')

source('scripts/tools/multiplot.R')
source('scripts/tools/combine_df_ggplot.R')
source('scripts/tools/calc_boot_ci.R')
source('scripts/tools/position_dodgev.R')
source('scripts/tools/fd_plot_themes.R')
source('scripts/tools/fd_helper_ddply_MeanCIoverSubjects.R')


source('scripts/analysis/functions/fd_plot_predict.R')
source('scripts/analysis/functions/fd_plot_X_choicetime.R')
source('scripts/analysis/functions/fd_stan_to_ggmcmc.R')
source('scripts/analysis/functions/fd_plot_postpred.R')
source('scripts/analysis/functions/fd_stan_main.R')
source('scripts/analysis/functions/fd_formula_and_lm.R')
source('scripts/analysis/functions/fd_stan_grid_collect.R')
source('scripts/analysis/functions/fd_loaddata.R')

