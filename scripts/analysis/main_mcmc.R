#!/usr/bin/Rscript

setwd('/net/store/nbp/users/behinger/projects/fixdur/git') #path to GIT
cfg = list(gist=TRUE)
#cfg = list(gist=FALSE)
paste0('gist on? ',cfg$gist)
source("scripts/analysis/functions/fd_paths.R") # this adds lots of paths & functions




if(cfg$gist){
  filename = paste0(Sys.Date(),'_gist_unstandardized')
  data.3mad = fd_loaddata('./cache/data/all_res_gist.RData')
}else{
  filename = paste0(Sys.Date(),'_unstandardized_')
  data.3mad = fd_loaddata()
}

mres.complexStandard.3mad = fd_formula_and_lm(data.3mad,gist = cfg$gist)

tmp = fd_stan_main(mres.complexStandard.3mad,niter = 1000,name=filename,rerun=T,is_on_grid = T)
#source('fd_runModels2.R')
if (1==0){
  cfg = list(nchains = 1,
             gridOutputPath = file.path('cache/gridoutput'),
             requirements = 'mem=2G,h=!ramsauer.ikw.uni-osnabrueck.de',
             job_name = 'fd_stan'
  )
  
  t = '1:5'
  #t = '1'
  cmd=paste0('qsub -cwd -t ',t, ' -o ', cfg$gridOutputPath, '/ -e ', cfg$gridOutputPath, '/ -l ', cfg$requirements, ' -N ', cfg$job_name, ' -pe default ', 1, ' -q nbp.q scripts/analysis/main_mcmc.R')
  system(cmd)
}
