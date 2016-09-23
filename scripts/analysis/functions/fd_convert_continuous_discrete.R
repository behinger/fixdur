
fd_convert_continuous_discrete = function(pred,varName,dataRange=NULL){
  #browser()
  if(is.null(dataRange)){
    xRange = seq(min(pred[,varName])-1,max(pred[,varName])+1,length.out = 30)
  }else{
    xRange = seq(dataRange[1],dataRange[2],length.out = 30) 
  }
  
  if(is.null(dim(pred))){
   pred = data.frame(pred)
   colnames(pred)[1] = varName
  }
  distInterval = findInterval(pred[,varName],xRange,all.inside=T)
  # Adjust Xrange:
  xRange = xRange[1:length(xRange)-1]+diff(xRange)/2
  
  # We want to clip the datapoints that are outside of our range.
  #if( any(distInterval==30))  xRange = c(xRange,NA)
  #if( any(distInterval==0)){  xRange = c(NA,xRange);distInterval=distInterval+1}
  pred[,varName] = xRange[distInterval]
  return(pred)
}