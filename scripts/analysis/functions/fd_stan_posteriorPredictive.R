model_stan_posteriorPredictive = function(fit,fullModelMatrix,subjectIndexVector,varName=NULL,cosineau=F,
                                          nIter = 100,nSub = 35,continuous_var=F,dataRange=NULL,customvar=NULL){
 #browser()
  
  
  source('scripts/analysis/functions/fd_convert_continuous_discrete.R')
  check_param_in_model = function(param,model){
    return(length(grep(param,colnames(model),fixed=T))>0)
  }
  
  if(!is.null(customvar)){
    varName =  'customvar'
    varNameS =  'customvar'
  }else if (any(!sapply(varName,FUN=function(x)check_param_in_model(x,fullModelMatrix)))){
    names = colnames(fullModelMatrix)
    print(colnames(fullModelMatrix))
    stop('could not find: ', varName, ' in X colnames')
  }
  
  library(ggmcmc)
  if(class(fit)=='stanfit'){
    S = ggs(fit)
  }else{
    S = fit
    S$Parameter = S$ParameterOriginal
  }
  #parmList = unique(S$Parameter)
  #fit@par_dims
  # beta = fixed effects
  # sigma_u = random-variances
  # L_u = random-correlations (half of matrix
  # z_u = ?
  # u = subjRanef
  
if(is.list(dataRange)){
    for(k in 1:length(dataRange)){
      if(continuous_var[[k]]){
        customvar[[k]] = fd_convert_continuous_discrete(data.frame("customvar"=customvar[[k]]),varName,dataRange[[k]])
      }
    }
    
  }else{
  if(continuous_var){
    if(is.null(customvar)){
      
      fullModelMatrix = fd_convert_continuous_discrete(fullModelMatrix,varName,dataRange)
      
    }else{
        customvar = fd_convert_continuous_discrete(customvar,varName,dataRange)  
    }
  }
    
  }
  
  fullModelMatrix = fullModelMatrix
 # browser()  
  subjectIndexVector = as.numeric(subjectIndexVector)
  predDat = NULL
  S$InteractionChainIter = (S$Chain-1)*max(S$Iteration) + S$Iteration
  #Rprof('prof1.out')
  
  iter_list =  sample.int(max(S$InteractionChainIter),nIter)


  for (it in 1:nIter){
    #X = fullModelMatrix[as.numeric(subjectIndexVector) == sample.int(max(as.numeric(subjectIndexVector)),1),]
    nTrials = length(fullModelMatrix[,1])
    show(sprintf('iteration %i',it))
    


    it_idx = iter_list[it]
    
    k = S[S$InteractionChainIter==it_idx,]
    beta = k$value[grep('beta',k$Parameter)]
    # beta[c(1:3,5:20)] = 0
    sigma = k$value[grep('sigma.u',k$Parameter)]
    u = k$value[grep('^u.',k$Parameter)]%>%matrix(ncol=length(grep('beta',k$Parameter)))
    sigma_e = k$value[grep('sigma.e',k$Parameter)]
    covmat= k$value[grep('L.u',k$Parameter)]%>%matrix(nrow=length(grep('beta',k$Parameter)))
    covmat = (covmat)%*%t(covmat)
    #sigma[1:length(sigma)] = 0.01
    
    # This is pulling new subjects out of the estimated random effects matrix, i.e. measuring nSub new subjects
    ran = mnormt::rmnorm(n=nSub,mean=beta,varcov=diag(sigma) %*% covmat %*%diag(sigma))
    
    # This is taking the estimates of the subjects values, i.e. measuring the same subjects again
    ran.sub = t(t(u)+beta)
    
    # This is a bit ugly because I did not know how to use adply with an additional loop-index (which one needs to tile down the fullModelMatrix.
    # Thus the head/tail combo
    ran = cbind(ran,1:nSub)
    ran.sub = cbind(ran.sub,1:nSub)
    
    #show(tail(ran[5,],1))
    #show(head(ran[5,],-1))
    #sigma_e=0.1
    get_pred = function(ran,fullModelMatrix){
    
    pred = adply(ran,1,function(x){
      X=fullModelMatrix[subjectIndexVector==tail(x,1),]
      return(cbind(data.frame(y=rnorm(dim(X)[1], head(x,-1)%*%t(X), sigma_e),trial=1:dim(X)[1]),
                   X))},
      .id='subject',.inform=F)
    return(pred)}
    
    pred = get_pred(ran,fullModelMatrix)
    pred.sub = get_pred(ran.sub,fullModelMatrix)
    
    if(!is.null(customvar)){
      pred = cbind(pred,customvar=customvar)
      pred.sub = cbind(pred.sub,customvar=customvar) 
      if (is.list(dataRange)){
        customvarName = NULL
        for(k in 1:length(dataRange)){
          colnames(pred)[length(pred)-length(dataRange)+k] = paste0('customvar_',k)
          colnames(pred.sub)[length(pred.sub)-length(dataRange)+k] = paste0('customvar_',k)
          customvarName = c(customvarName,paste0('customvar_',k))
        }
        varNameS = customvarName
        #varName = substr(customvar,1,nchar(customvar)-1)
      }
      
     
    }else{
      varNameS = paste0("`",varName,"`")
  }
      


    
    postPredStat_raw = ddply(pred,varNameS,function(x){data.frame(t(quantile(x$y,c(0.025,0.25,0.5,0.75,0.975),na.rm=T)),mean=mean(x$y))})
    #}
    #ggplot(pred,aes(x=customvar,y=y))+stat_smooth(method='lm',formula = y~log(x))+geom_line(data=postPredStat_raw,aes(x=customvar,y=`50%`))
    #postPredStat_raw = ddply(pred,paste0('`',varName,'`'),function(x){quantile(x$y,c(0.025,0.25,0.5,0.75,0.975))})
    #browser()
     if(cosineau){
       cosineaufactor = ddply(pred.sub,.(subject),summarise,m=mean(y))$m
    }else{
      cosineaufactor = rep(0,nSub)
    }
    postPredStat_subjectwise.sub = ddply(pred.sub,varNameS,
                                     function(x,cf){
                                       ym = ddply(x,.(subject),function(x,cf){ym=mean(cf)+mean(x$y-cf[x$subject[1]])},cf)$V1
                                       data.frame(t(quantile(ym,c(0.025,0.25,0.5,0.75,0.975),na.rm=T)),mean=mean(ym))},cosineaufactor)
    
    
    postPredStat_subjectwise = ddply(pred,varNameS,
                                      function(x){
                                        ym = ddply(x,.(subject),function(x,cf){ym=mean(x$y)})$V1
                                        data.frame(t(quantile(ym,c(0.025,0.25,0.5,0.75,0.975),na.rm=T)),mean=mean(ym))})
    
    predDat = rbind(predDat,cbind(type='raw',postPredStat_raw),
                            cbind(type='subject',postPredStat_subjectwise),
                            cbind(type='subfit.subject',postPredStat_subjectwise.sub))
    #browser()
    
  }
 # Rprof(NULL)
  # colnames(predDat) = c('difficulty','maxY','minY')
  
  colnames(predDat)[(length(predDat)-5):(length(predDat)-1)] = c('Q2.5','Q25','Q50','Q75','Q97.5')
  return(predDat)
}

