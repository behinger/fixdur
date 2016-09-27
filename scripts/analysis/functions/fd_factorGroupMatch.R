fd_factorGroupMatch = function(S){
  grouping = list(c( "(Intercept)"),
                  c("forcedFixtime","log_forcedFixtime","log_NumOfBubbles","stimulus_type","log_forcedFixtime:log_NumOfBubbles"),
                  c("log_nextBubbleDist","log_prevBubbleDist","angleDiff",
                    "sin_nextBubbleAngle","cos_nextBubbleAngle",
                    "sin2_nextBubbleAngle","cos2_nextBubbleAngle",
                    "sin_prevBubbleAngle","cos_prevBubbleAngle",
                    "sin2_prevBubbleAngle","cos2_prevBubbleAngle",
                    "sq_chosenBubbleX","sq_chosenBubbleY","chosenBubbleX","chosenBubbleY",
                    "centerDistance"),
                  c("lag1_choicetime","lag1_forcedFixtime","trialNum",'bubbleNum'))
  #grouping = rev(grouping)
  
  
  factorGroupMatch = data.frame(name=unlist(grouping),num=sapply(unlist(grouping),FUN = function(x){which(laply(grouping,.fun = function(y){x %in% y}))}))
  S_custom = ddply(S,.(Parameter),function(x,factorGroupMatch){cbind(x,group=rep(factorGroupMatch$num[stringdist::amatch(as.character(x$Parameter[1]),factorGroupMatch$name,maxDist=Inf)],length(x$Parameter)))},factorGroupMatch) 
  return(S_custom)
}