fd_formula_and_lm = function(data,gist=F){
  #formulaList = list(
  data$stimulus_type = as.factor(data$stimulus_type)
  formula.complexStandard =  choicetime~
    forcedFixtime+
    log_forcedFixtime+
    log_NumOfBubbles+
    stimulus_type+
    lag1_choicetime+
    lag1_forcedFixtime+
    log_nextBubbleDist+log_prevBubbleDist+#nextHorizSacc+prevHorizSacc+
    angleDiff+
    sin_nextBubbleAngle+cos_nextBubbleAngle+
    sin2_nextBubbleAngle+cos2_nextBubbleAngle+
    sin_prevBubbleAngle+cos_prevBubbleAngle+
    sin2_prevBubbleAngle+cos2_prevBubbleAngle+
    as.numeric(trialNum)+
    log_NumOfBubbles:log_forcedFixtime+
    (1|subject)
  #(1+log_forcedFixtime+as.factor(stimulus_type)+log_NumOfBubbles|subject)
  #(1|image)
  #)
  
  if(gist) formula.complexStandard = update.formula(formula.complexStandard,~.*gist)
 
  mres = lmer(formula = formula.complexStandard,data=data,REML=F)
  return(mres)
}
# dataList = list(
#   "data.3mad"
# )
# 
# for (d in 1:length(dataList)){
#   for (f in 1:length(formulaList)){
#     
#     # I will die in shame for using eval, but this is the only way I could think of, that allows us to compare the automatical model fits here with
#     # later modelcomparisons manually on e.g. data.cook.
#     modelName = gsub("^.*?[.]","",names(formulaList)[f])
#     dataName =  gsub("^.*?[.]","",dataList[d])
#     #dataName =  gsub("^.*?[.]","",names(dataList)[d])
#     
#     print(paste("Running Model",modelName,"with data:",dataName))
#     modelName = paste('mres.',modelName,sep='')
#     if( dataName != ""){
#       modelName = paste(modelName,'.', dataName,sep='')
#     }
#     tryCatch(    eval(parse(text=paste(modelName," <-lmer(formula=",formulaList[[f]][2],'~',formulaList[[f]][3],",data=",dataList[[d]],",REML=FALSE)",sep=''))),
#                  warning=function(w){print(w)})
#     
#     #assign(,mres)
#   }
# }
