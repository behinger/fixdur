fd_stan_to_ggmcmc = function(fit,label_dataframe){
  library(ggmcmc)
#  browser()
  #if (fit@sim$fnames_oi[1] == 'beta[1]'){ 
  #  # the labels in label_dataframe are sometimes saved as beta.1. instead of beta[1]. This seems to depend on some package versions...
  #  label_dataframe$Parameter = gsub('(beta[.])','beta[',label_dataframe$Parameter)
  #  label_dataframe$Parameter = gsub('([.]$)',']',label_dataframe$Parameter)
  #}
  
  S = ggs(fit,par_labels = label_dataframe,family = 'beta')
  source('./functions/fd_factorGroupMatch.R')
  S_custom = fd_factorGroupMatch(S)
 
  return(S_custom)
}
