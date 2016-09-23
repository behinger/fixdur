fd_factorGroupMatch = function(S){
  grouping = list(c( "(Intercept)"),
                  c("forcedFixtime","log(forcedFixtime)","log(NumOfBubbles)","as.factor(stimulus_type)urban","log(forcedFixtime):log(as.numeric(NumOfBubbles))"),
                  c("log(nextBubbleDist)","log(prevBubbleDist)","angleDiff","sin(nextBubbleAngle/180 * pi)","cos(nextBubbleAngle/180 * pi)","sin(2 * nextBubbleAngle/180 * pi)","cos(2 * nextBubbleAngle/180 * pi)","sin(prevBubbleAngle/180 * pi)","cos(prevBubbleAngle/180 * pi)","sin(2 * prevBubbleAngle/180 * pi)","cos(2 * prevBubbleAngle/180 * pi)"),
                  c("lag1_choicetime","lag1_forcedFixtime","as.numeric(trialNum)"))
  #grouping = rev(grouping)
  
  
  factorGroupMatch = data.frame(name=unlist(grouping),num=sapply(unlist(grouping),FUN = function(x){which(laply(grouping,.fun = function(y){x %in% y}))}))
  S_custom = ddply(S,.(Parameter),function(x,factorGroupMatch){cbind(x,group=rep(factorGroupMatch$num[stringdist::amatch(as.character(x$Parameter[1]),factorGroupMatch$name,maxDist=Inf)],length(x$Parameter)))},factorGroupMatch) 
  return(S_custom)
}