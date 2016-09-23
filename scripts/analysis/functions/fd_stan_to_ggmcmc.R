fd_stan_to_ggmcmc = function(fit,label_dataframe){
  library(ggmcmc)
  
  S = ggs(fit,par_labels = label_dataframe,family = 'beta')
  source('scripts/analysis/functions/fd_factorGroupMatch.R')
  S_custom = fd_factorGroupMatch(S)
 
  return(S_custom)
}
