fd_plot_postpred = function(varName,mres,
                            mres.standardized=NULL,
                            fit,continuous_var,
                            plotType=1,
                            nIter=100,
                            cosineau=F,
                            returnData = F,
                            customvar=NULL,dataRange = NULL){
  
  
  library('magrittr')
  source('scripts/analysis/functions/fd_stan_posteriorPredictive.R')
  source('scripts/analysis/functions/fd_posteriorpredictive_hdi.R')
  source('scripts/analysis/functions/fd_lme4_ci.R')
  
  
  if(is.null(mres.standardized)){
   mres = mres
  }else{
    mres.unstandardized = mres
    mres = mres.standardized
    warning('not sure if the standardized case works so nicely! please check it')
  }
  if(is.null(dataRange)){
    if(!is.null(customvar)){
      dataRange = c(min(customvar)-1,max(customvar)+1)  
    }else{
    dataRange = c(min(modelMatrix[,varName])-1,max(modelMatrix[,varName])+1)
    }
  }
  
  # First we get the posterior predictive data
  modelMatrix = model.matrix(mres)
  
  
  
  
  predDat = data.frame( model_stan_posteriorPredictive(fit,
                                                       modelMatrix,
                                                       subjectIndexVector=sort(mres@frame$subject),# LME4 resorts the data frame but not the modelMatrix, weird
                                                       varName,
                                                       nIter=nIter,
                                                       continuous_var = continuous_var,
                                                       customvar=customvar,
                                                       cosineau=cosineau,
                                                       dataRange =dataRange ))
  
  
  # we calculate the confidence intervals of the quartiles  

  predDat.ci = fd_posteriorpredictive_hdi(predDat,columns=seq(length(continuous_var)+1))
#  browser()
  # we get the quartiles of the real data
  dat.ci = fd_lme4_ci(mres,varName,continuous =continuous_var,customvar= customvar,dataRange = dataRange)
  
  tmp = subset(dat.ci,dat.ci$type =='subject')
  tmp$type = 'subfit.subject'
  dat.ci = rbind(dat.ci,tmp)
  # we combine it
  
  ggplotdat = rbind.fill(cbind(predDat.ci,predReal='pred'),cbind(dat.ci,predReal='real'))
  
  #'de'-standardize
  if(!is.null(mres.standardized)){ 
    orgPos = stringdist::amatch(varName,colnames(mres.unstandardized@frame),maxDist=Inf)
    orgSD = sd(mres.unstandardized@frame[,orgPos])
    orgMean = mean(mres.unstandardized@frame[,orgPos])
    ggplotdat[,1] = (orgMean+2*orgSD*as.numeric(ggplotdat[,1]))
  }
  #browser()
  if(is.list(dataRange)){
    for(k in 1:length(dataRange)){
      if(continuous_var[[k]]){
        ggplotdat[,colnames(predDat.ci)[k]] = factor(ggplotdat[,colnames(predDat.ci)[k]])
      }
    }
  }else{
  if(!continuous_var){
    ggplotdat[,colnames(predDat.ci)[1]] = factor(ggplotdat[,colnames(predDat.ci)[1]])
  }
  }
  #browser()
  if(!returnData){
  if(plotType==1){
    if(continuous_var){
    p = ggplot(ggplotdat,aes_string(x=colnames(predDat.ci)[1],ymax="high",ymin="low",y="median",color='variable',linetype="predReal"))+
      geom_ribbon(alpha=0.1)+geom_line()+
      facet_grid(type~variable)
    }else{
      
      p = ggplot(ggplotdat,aes_string(x=colnames(predDat.ci)[1],ymax="high",ymin="low",y="median",color='variable',shape="predReal"))+
        geom_errorbar(position=position_dodge(width=0.5))+geom_point(position=position_dodge(width=0.5))+
        facet_grid(type~variable)
      
    }
    
  }
  if(plotType==2){
    
    p = ggplot(ggplotdat,aes(x=variable,ymax=high,ymin=low,y=median,color=predReal))+
      geom_point()+
      geom_errorbar(alpha=0.4)+
      
      facet_grid(paste0("type~",colnames(predDat.ci)[1]))
    
  }
  p = p +xlab(varName) + ylab('choicetime [ms]')
  }
ifelse(returnData,return(ggplotdat),return(p))
#return(p)
}