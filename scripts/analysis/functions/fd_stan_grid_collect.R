fd_stan_grid_collect <-function(name='2015-11-20_unstandardized',combine_again=F){
  
  
  full.path = paste0('../../cache/','stanfit/')
  #if (combine_again==F && file.exists(paste0(full.path,name,'.RData'))){
  #  show('Already combined file Found, loading it')
  #  fd_stan_main(name=name)
  #}
  #else{
  files = list.files(full.path,patter=paste0(name,'.*RData'))
  show(paste0('Loading ',length(files),' files'))
  fitList = NULL
  for(k in files){
    load(paste0(full.path,k))
   fitList = c(fitList,fit) 
  }
  fit = rstan::sflist2stanfit(fitList)
  #show('Saving Fit')
#  save(fit,modelMatrix,label_dataframe,file=paste0(full.path,name,'.RData'))
  #}
  return(list(fit=fit,label_dataframe=label_dataframe,modelMatrix=modelMatrix))
  
}
