# Plot by bubble
source("scripts/analysis/functions/fd_predict.R")
source("scripts/analysis/functions/fd_runningAverage.R")
fd_plot.pred_data <- function(data,model,factor,range=NULL){
  
  data.meanH = fd_plot_X_choicetime(data,X=factor,returnPlot=F,dataRange=range)
  
  data.fit = data
  
  
  fittedData= fitted(model)
  naFillin = function(mres,dataToBeFilledIn){
    naRemoved = as.numeric((attr(mres@frame,'na.action')))
    tmp <- numeric(length(dataToBeFilledIn)+length(naRemoved))
    tmp[naRemoved] = NA
    tmp[!is.na(tmp)] = dataToBeFilledIn
    return(tmp)
  }
  
  
  
  if (class((attr(model@frame,'na.action'))) == 'omit'){
    # if the na action omit was used, we need to fill in back the omitted NAs to get to the same length as the original data frame.
    fittedData = naFillin(model, fittedData)
  }
  data.fit$choicetime = fittedData
  
  data.fitH = fd_plot_X_choicetime(data.fit,X=factor,returnPlot=F,dataRange=range)
  
  
  
  
  
  
  
  dat.all = combine_df_ggplot(data.meanH,data.fitH,groupNames =c('Raw Data Mean','Model Fit'))
  
  
  if(is.null(range)){ # Not connected
  p = ggplot(data=dat.all,
             aes_string(x=colnames(dat.all)[1],y="meanChoice",colour="ggplotGrouping",ymax='conf.high',ymin='conf.low'))+
    geom_point(size=5, aes(shape=ggplotGrouping),position=position_dodge(width=0.9))+
    geom_errorbar(size=1.5,alpha=0.5,position=position_dodge())+
    ylab(label = "Saccadic Reaction Time [ms]")  
}else{                # Connected lines
  p = ggplot(data=dat.all,
             aes_string(x=colnames(dat.all)[1],y="meanChoice",colour="ggplotGrouping"))+
    geom_path(size=1.5)+
    geom_ribbon(aes(ymax=conf.high,ymin=conf.low),alpha=0.3)+
    ylab(label = "Saccadic Reaction Time [ms]")
}
  return(p+ggtitle('95% Cousineau Corrected CI'))
}



# Plot by bubble
plot.pred_runAVG.byBubble <- function(data,mres,stat='convFilter.mean'){
  
  dat.runAvg = fd_runningAverage(data,grouping='NumOfBubbles',selection = data$stimulus_type=='noise',stat=stat)
  #dat.runAvg = fd_runningAverage(data,grouping='NumOfBubbles',selection = data$stimulus_type=='noise',windowType="gaussian",stat="winsor")
  dat.runAvg$NumOfBubbles = as.factor(dat.runAvg$NumOfBubbles)
  dat.predict = fd_predict(mres,NumOfBubbles=1:5,data=data)
  
  
  
  dat.all = combine_df_ggplot(dat.runAvg,dat.predict,groupNames =c('data average','prediction'))
  
  p = ggplot()+
    geom_line(data=dat.all,aes(x=forcedFixtime,y=choicetime,linetype=ggplotGrouping,colour=factor(NumOfBubbles)))+ ylab("Choice-Time [ms]")+xlab('Forced-Fixation-Time [ms]')+ 
    coord_cartesian(xlim=c(0,1500))
  return(p)
}

plot.pred_runAVG.bySubject <- function(data,mres){
  # Plot by subject
  dat.runAvg = fd_runningAverage(data,grouping='subject',selection = data$stimulus_type=='noise'&data$NumOfBubbles==1,stat="convFilter.mean")
  dat.runAvg$subject = as.factor(dat.runAvg$subject)
  #dat.runAvg = fd_runningAverage(data,grouping='subject',selection = data$stimulus_type=='noise'&data$NumOfBubbles==1,windowType="gaussian",stat="winsor")

  dat.predict = fd_predict(mres,NumOfBubbles=1,subject=sort(unique(data$subject)),data=data)
  
  dat.all = combine_df_ggplot(dat.runAvg,dat.predict,groupNames =c('data average','prediction'))
                              
  p = ggplot()+
    geom_line(data=dat.all,aes(x=forcedFixtime,y=choicetime,colour=ggplotGrouping))+facet_wrap(~subject,ncol=8)+ ylab("Choice-Time [ms]")+xlab('Forced-Fixation-Time [ms]')+ 
    coord_cartesian(xlim=c(0,1500))
  
  #p = ggplot(data=dat.all,aes(x=forcedFixtime))+geom_line(aes(y=runAvg))+geom_line(aes(y=choiceTimeModel))+facet_wrap(~subject,ncol=8)
  return(p)
  #actual choicetime vs. predicted choicetime
  #qplot(data.trim$choicetime,fitted(mres),aes(alpha=0.01))+ geom_jitter()+geom_smooth(method='lm')+geom_abline(slope=1,colour="red")
}

plot.pred_runAVG.byBubbleAndSubject <- function(data,mres){
  # Plot by subject
  datList = list()
  for (k in 1:5){
  dat.runAvg = fd_runningAverage(data,grouping='subject',selection = data$stimulus_type=='noise'&data$NumOfBubbles==k,stat="convFilter.mean")
  dat.runAvg$NumOfBubbles = as.factor(k)
  dat.runAvg$subject = as.factor(dat.runAvg$subject)
  datList[[k]] = dat.runAvg
  }
  
  #dat.runAvg = fd_runningAverage(data,grouping='subject',selection = data$stimulus_type=='noise'&data$NumOfBubbles==1,windowType="gaussian",stat="winsor")
  dat.runAvg = do.call("rbind",datList)
  dat.predict = fd_predict(mres,NumOfBubbles=1:5,subject=sort(unique(data$subject)),data=data)
  
  dat.all = combine_df_ggplot(dat.runAvg,dat.predict,groupNames =c('data average','prediction'))
  
  p = ggplot()+
    geom_line(data=dat.all,aes(x=forcedFixtime,y=choicetime,colour=NumOfBubbles,linetype=ggplotGrouping))+facet_wrap(~subject,ncol=8)+ ylab("Choice-Time [ms]")+xlab('Forced-Fixation-Time [ms]')+ 
    coord_cartesian(xlim=c(0,1500),ylim=c(140,200))
  
  #p = ggplot(data=dat.all,aes(x=forcedFixtime))+geom_line(aes(y=runAvg))+geom_line(aes(y=choiceTimeModel))+facet_wrap(~subject,ncol=8)
  return(p)
  #actual choicetime vs. predicted choicetime
  #qplot(data.trim$choicetime,fitted(mres),aes(alpha=0.01))+ geom_jitter()+geom_smooth(method='lm')+geom_abline(slope=1,colour="red")
}

plot.variance <- function(mres){
  # Variance of residuals gaussian model
  varDat = data.frame(choicetime = residuals(mres),
                      forcedFixtime = mres@frame$forcedFixtime)
                      #forcedFixtime = fitted(mres))
  
#   varDat = data.frame(choicetime =rnorm(37177,mean = 200,sd = 20),
#                       forcedFixtime = fitted(mres))
  
  dat.runAvgR = fd_runningAverage(varDat,windowType='rect',xmin = 0,winsize = 20)
  dat.runAvg = fd_runningAverage(varDat,windowType='rect',stat='std',xmin = 0,winsize = 20)
  dat.runAvgWin = fd_runningAverage(varDat,windowType='rect',stat='winsor.std',xmin = 0,winsize = 20)
  dat.runAvg$yWin = dat.runAvgWin$choicetime

  p1 <- qplot(mres@frame$forcedFixtime,residuals(mres))+coord_fixed()+coord_cartesian(xlim=c(0,1500))+xlab('Forced-Fixation-Time [ms]')+ylab('Residuals')
  p2 <- ggplot(data=dat.runAvg,aes(x=forcedFixtime)) + geom_line(aes(y=yWin))+coord_cartesian(xlim=c(0,1500))+xlab('Forced-Fixation-Time [ms]')+ylab('Variance over Residuals (Winsorized)')
  p3 <- ggplot(data=dat.runAvg,aes(x=forcedFixtime)) + geom_line(aes(y=choicetime))+coord_cartesian(xlim=c(0,1500))+xlab('Forced-Fixation-Time [ms]')+ylab('Variance over Residuals')
  p4 <- ggplot(data=dat.runAvgR,aes(x=forcedFixtime)) + geom_line(aes(y=choicetime))+coord_cartesian(xlim=c(0,1500))+xlab('Forced-Fixation-Time [ms]')+ylab('Mean over Residuals')
  multiplot(p1,p4,cols=1)
  multiplot(p2,p3,cols=1)
}


plot.variance.logModel <- function(mres){
  # Variance of residuals LOG model
  varDat = data.frame(choicetime = residuals(mres),
                      forcedFixtime = fitted(mres))
  dat.runAvg = fd_runningAverage(varDat,windowType='rect',stat='winsor.std',xmin = 4,xmax=6,nX = 100,winsize=0.1)
  
  p1 <- qplot(fitted(mres),residuals(mres))+coord_fixed()+coord_cartesian(xlim=c(4,log(500)))
  p2 <-ggplot() + geom_line(data=dat.runAvg,aes(x=x,y=y))+coord_cartesian(xlim=c(4,log(500)))
  multiplot(p1,p2,cols=1)
  
}
  

plot.compareMovingaverages <- function(data){
  source('helper/combine_df_ggplot.R')
  
#   add_grouping <- function(df,g){
#     df$grouping=rep(g,length(df[,1]))
#     return(df)
#   }
  rM1 = fd_runningAverage(data,stat="convFilter.mean")
  #rM1 = add_grouping(rM1,'convFilter gaussian')
  rM2 = fd_runningAverage(data,windowType="rect",stat="winsor") 
  #rM2 = add_grouping(rM2,'winsor rect')
  rM3 = fd_runningAverage(data,windowType="gaussian",stat="mean") 
  #rM3 = add_grouping(rM3,'mean Gaussian')
  
  rM4 = loess(formula=choicetime~forcedFixtime,data=data)  
  rM4 = data.frame(forcedFixtime = 1:1500, choicetime=predict(rM4,data.frame(forcedFixtime=1:1500)))
  #rM4 = add_grouping(rM4,'loess')
  colnames(rM4) = c('forcedFixtime','choicetime')
  
  rM5 = fd_runningAverage(data,windowType="rect",stat="median") 
  #rM5 = add_grouping(rM5,'median rect')
  
  
  allM = combine_df_ggplot(rM1,rM2,rM3,rM4,rM5,groupNames = c('convFilter gaussian','windsor rect','mean gaussian','loess','median rect'))
  
  colnames(allM) = c('choicetime','forcedFixtime','ggplotGrouping')
  p = ggplot()+
    geom_line(data=allM,aes(x=choicetime,y=forcedFixtime,colour=factor(ggplotGrouping)))+
    coord_cartesian(xlim=c(0,1000))
  return(p)

}