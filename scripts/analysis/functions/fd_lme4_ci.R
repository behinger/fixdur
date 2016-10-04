fd_lme4_ci = function(mres.standardized,varName,continuous=F,customvar=NULL,dataRange=NULL){
  
  source('./functions/fd_convert_continuous_discrete.R')
  dat = mres.standardized@frame
  if(!is.null(customvar)){
    # If customvar go here
   varName = 'customvar'
   varName2 = varName
   if(is.list(dataRange)){
     # if there are multiple factors e.g. interaction go here
     for(k in 1:length(dataRange)){
       if(continuous[[k]]){
         customvar[[k]] = fd_convert_continuous_discrete(data.frame("customvar"=customvar[[k]]),varName,dataRange[[k]])
       }
     }
   }
   #now that we delt with the interaction actually add the customvar to the dataset
   dat = cbind(dat,customvar=customvar)
     
     if (is.list(dataRange)){
       customvarName = NULL
       for(k in 1:length(dataRange)){
         colnames(dat)[length(dat)-length(dataRange)+k] = paste0('customvar_',k)
         customvarName = c(customvarName,paste0('customvar_',k))
       }
       varName2 = customvarName   
    }
  }else{
      varName2 = paste0("`",varName,"`")
  }
  if (!is.list(dataRange)){
    if(continuous){dat = fd_convert_continuous_discrete(dat,varName,dataRange)}
  }
  #browser()
  
  dat.ci = ddply(dat,varName2,function(x)quantile(x$choicetime,c(0.025,0.25,0.5,0.75,0.975)))%>%set_colnames(.,c(varName2,'Q2.5','Q25','Q50','Q75','Q97.5'))
  dat.ci.mean = ddply(dat,varName2,function(x){data.frame(mean=mean(x$choicetime))})
  dat.ci.subject = ddply(dat,varName2,function(x)quantile(ddply(x,.(subject),summarise,ym=mean(choicetime))$ym,c(0.025,0.25,0.5,0.75,0.975)))%>%set_colnames(.,c(varName2,'Q2.5','Q25','Q50','Q75','Q97.5'))
  
  #browser()
  dat.ci.subject.mean = fd_helper_ddply_MeanCIoverSubjects(dat,varName2)
  #dat.ci.subject.mean = ddply(dat,paste0('`',varName,'`'),function(x){data.frame(mean=mean(ddply(x,.(subject),summarise,ym=mean(choicetime))$ym))})
  
  
  dat.ci = rbind.fill(cbind(type='raw',dat.ci,mean=dat.ci.mean$mean),
                 cbind(type='subject',dat.ci.subject,mean=dat.ci.subject.mean$meanChoice,low=dat.ci.subject.mean$conf.low,high=dat.ci.subject.mean$conf.high))
  dat.ci = reshape2::melt(dat.ci,measure.vars=c(grep('Q[1-9]',colnames(dat.ci)),which(colnames(dat.ci)=='mean')))
  colnames(dat.ci)[which(colnames(dat.ci)=='value')] = 'median'
  dat.ci$low[dat.ci$variable!='mean'] = NA
  dat.ci$high[dat.ci$variable!='mean'] = NA
  return(dat.ci)  
}

