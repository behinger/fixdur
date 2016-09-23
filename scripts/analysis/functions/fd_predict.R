fd_predict <- function(mres,NumOfBubbles=1,stimulus_type='noise',forcedFixtime = seq(1,1500),subject=NULL,fillitwith=c('average','zeros'),data){  
  fillitwith <- match.arg(fillitwith)
  
  # Make the primary data grid
  if(!is.null(subject)){
    newDat = data.frame(expand.grid(
            forcedFixtime,
            NumOfBubbles,
            stimulus_type,
            subject))
    colnames(newDat) <- c('forcedFixtime','NumOfBubbles','stimulus_type','subject')  
    newDat$subject = as.factor(newDat$subject)
  }else{
    
    newDat = data.frame(expand.grid(
      forcedFixtime,
      NumOfBubbles,
      stimulus_type))
    colnames(newDat) <- c('forcedFixtime','NumOfBubbles','stimulus_type')  
  }
  
    #levels(newDat$stimulus_type) = c('noise','urban')
    #newDat$stimulus_type[1] = 'noise'
    newDat$NumOfBubbles = as.factor(newDat$NumOfBubbles)
    
    # add the other fixed effects we need
    allFix = (colnames(mres@frame))
    allFix = setdiff(allFix,names(mres@flist))
    curFix = c('choicetime',colnames(newDat))
    
    for (k in 1:length(curFix)){
      ma = which(curFix[k]==allFix)
      ma = c(ma,grep(paste('\\(',curFix[k],'\\)',sep=''),allFix)) # ma.tch
      if (length(ma)>0){
        allFix = allFix[-unique(ma)]
      }
    }
    # we now need to add them
    
    print(paste('adding',length(allFix),'predictors with a value'))
    classList = sapply(data, class)
    nameList = colnames(data)
    for (k in 1:length(allFix)){
      if (length(grep('\\(',allFix[k]))>0){
        allFix[k] = regmatches(allFix[k], gregexpr("(?<=\\().*?(?=\\))", allFix[k], perl=T))[[1]]
        rad2degString = regmatches(allFix[k],gregexpr("/180 * pi",allFix[k],fixed=T),invert=T)[[1]][1]
        if(length(rad2degString)!=0){
          allFix[k]  = rad2degString 
        }
        times2String = regmatches(allFix[k],gregexpr("2 * ",allFix[k],fixed=T),invert=T)[[1]]
        if(!is.na(times2String[2])){
          allFix[k]  = times2String[2]
        }
      }
      #newDat[,allFix[k]] = round(runif(length(newDat[,1]),min = 0,max=1))#alternatively you could fill in the average value of mres
      if (fillitwith == 'zeros'){
      newDat[,allFix[k]] = rep(0,length(newDat[,1]))#alternatively you could fill in the average value of mres
      }else if(fillitwith=='average'){
        #newDat[,allFix[k]] = rep(mean(mres@frame[,allFix[k]],na.rm = TRUE),length(newDat[,1]))
        newDat[,allFix[k]] = rep(mean(data[,allFix[k]],na.rm = TRUE),length(newDat[,1]))
      }
      if (classList[nameList==allFix[k]]=='factor'){
        newDat[,allFix[k]]= as.factor(newDat[,allFix[k]])
      }
      if (classList[nameList==allFix[k]]=='logical'){
        newDat[,allFix[k]]= as.logical(newDat[,allFix[k]])
      }
    }
    if(is.null(subject)){
      
      prediVal = cbind(newDat,choicetime=predict(mres,newdata = newDat,re.form=NA))
      
    }else{
#       ranFormula = ''
#       idx = which(names(ranef(mres.complex.3sd)) == 'subject')
#       re = names(ranef(mres.complex.3sd)[[idx]])
#       for (k in 1:length(re)){
#         if (re[k] == '(Intercept)') {ranFormula = paste(ranFormula,'1',sep='')}
#         else{
#         ranFormula = paste(ranFormula,re[k],sep='+')
#         }
#       }
#       ranFormula = formula(paste('~(',ranFormula,'|subject)',sep=''))
      ranFormula =  formula("~(1+log(forcedFixtime)+as.factor(stimulus_type)+log(as.numeric(NumOfBubbles))|subject)")

      prediVal = cbind(newDat,choicetime=predict(mres,newdata = newDat,re.form = ~(1+log(forcedFixtime)+log(as.numeric(NumOfBubbles))|subject)))
    }
    return(prediVal)
  #subject=c(1,3,4,  5,  6,  10, 11, 12, 13, 15, 16, 20, 21, 22, 23, 24, 25,  26, 27, 28, 29, 30, 8,  9,  18, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40)
}
