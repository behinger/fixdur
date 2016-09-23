fd_plot_X_choicetime= function(data,X,dataRange = NULL,returnPlot=TRUE){
  source('helper/calc_boot_ci.R')
  source('helper/fd_helper_ddply_MeanCIoverSubjects.R')
  
  data=data[!is.na(data$choicetime),]
  continuous = (!(length(unique(data[,X]))<20 | class(data[,X])=='factor'))
  if (continuous){
    #dataRange = range(data.3sd[,'nextBubbleDist'])
    #xRange = seq(dataRange[1],dataRange[2],length.out = 30) # Autorange does not work so well, we need manual ranges
    xRange = seq(dataRange[1],dataRange[2],length.out = 30)
    
    distInterval = findInterval(data[,X],xRange,all.inside=T)
    # Adjust Xrange:
    xRange = xRange[1:length(xRange)-1]+diff(xRange)/2
    
    X = paste(X,'_hist',sep='')
    data = cbind(data,data.frame(Xtmp = distInterval))
    colnames(data)[length(data)] = X
  }
  
  
  data = fd_helper_ddply_MeanCIoverSubjects(data,X)
  if (continuous) data[,X] = xRange[data[,X]]
  
  p = ggplot(data=data,aes_string(x=X,y='meanChoice'))+geom_point()+geom_errorbar(aes(ymax=conf.high,ymin=conf.low))+ylab('mean Choice-Time [ms]')
    
  if(returnPlot){  
  return(p)
  }else{
    return(data)
  }
}  
