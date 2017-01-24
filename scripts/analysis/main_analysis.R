#' ---
#' output: pdf_document
#' ---
#' ----
#' title: "Fixdur Plots ECEM 03 08 2015"
#' author: "Benedikt Ehinger Lilli Kaufhold"
#' date: "`r format(Sys.time(), '%d %B, %Y')`"
#' ----
#+ setup, include=FALSE
knitr::opts_chunk$set(echo=FALSE, warning=FALSE, autodep=TRUE,message=FALSE,cache=T,fig.width=7.5, fig.asp=0.75) #usually fig height 8


#+ set-options, echo=FALSE, cache=TRUE
#options(width = 120)


#setwd('/net/store/nbp/users/behinger/projects/fixdur/git') #path to GIT
source("functions/fd_paths.R") # this adds lots of paths & functions

#cfg = list(nIter=100,gist=TRUE)
cfg = list(nIter=100,gist=FALSE)

source('fd_load_midlevel.R')

#if(cfg$gist){ 
data.3madGist = fd_loaddata('../../cache/data/all_res_gist.RData')
outGist = fd_load_midlevel(data.3madGist,list(gist=TRUE))
#}else{
data.3mad = fd_loaddata()
out = fd_load_midlevel(data.3mad,list(gist=FALSE))
#}


stanfit =  out$fit
label_dataframe = out$label_dataframe
modelMatrix = out$modelMatrix
hdiDataFrame=out$hdiDataFrame
hdiDataFrameNorm=out$hdiDataFrameNorm
hdiDataFrameNormLabels=out$hdiDataFrameNormLabels
S_custom=out$S_custom
mres.complexStandard.3mad=out$mres.complexStandard.3mad


#+ outlierplot, fig.asp=0.25
#outlier.3mad = fd_loaddata(returnOutlier = TRUE)
#outlier.3mad = ddply(outlier.3mad,.(subject),transform,index = 1:length(bad))
#ggplot(outlier.3mad,aes(x=index,y=choicetime,color=bad))+geom_point(alpha=0.2)+facet_grid(.~subject,space = 'free_x',scales = 'free_x')+tBE(base_size = 10)+scale_x_continuous(breaks=round(seq(0,900,by=500)))



#+ custom functions
naRM = function(mresframe,data){
  naRemoved = as.numeric((attr(mresframe,'na.action')))
  data = data[!((1:length(data)) %in% naRemoved)]
  return(data)
}

plot_posteriorpredictive = function(dat){
  if (length(unique(dat[,1]))<20){
    p =ggplot(subset(dat,with(dat,type=='subfit.subject'&variable=='mean')),
              aes_string(x=colnames(dat)[1],
                         ymax="high",ymin="low",y="median",
                         group = 'predReal',
                         shape="predReal",color='predReal'))+
      geom_point(position=position_dodge(width=.9),size=4)+
      geom_errorbar(position=position_dodge(width=.9))+
      tBE(base_size = 10)
  }else{
    #continuous regressor
    p =ggplot(subset(dat,with(dat,type=='subfit.subject'&variable=='mean')),
              aes_string(x=colnames(dat)[1],fill='predReal',
                         ymax="high",ymin="low",y="median",
                         linetype="predReal",color='predReal'))+
      geom_ribbon(alpha=0.1)+
      geom_line()+
      tBE(base_size = 10)
  }
  return(p)
}



#+ horizontalErrorbarParameterplot
ggplot(hdiDataFrameNorm,aes(y=Parameter,x=Estimate,color=as.factor(group)))+
    geom_errorbarh(aes(xmax=high,xmin=low),height=0,lwd=1,position=position_dodgev(height=.5))+
    geom_point(position=position_dodgev(height=.5))+
    
    scale_color_discrete(guide=FALSE)+ # hide the unnessecary colour legend
    geom_text(data=data.frame(group=hdiDataFrameNorm$group,
              Parameter =hdiDataFrameNorm$Parameter,
              transformRule=hdiDataFrameNormLabels),#transformRule=paste0('`',hdiDataFrameNormLabels,'`')
              aes(x=40,label=transformRule),color='gray',hjust='outward',parse=T)+
  
  facet_grid(group~.,scale='free_y',space='free_y')+
    coord_cartesian(xlim=c(-45,90))+
    geom_vline(xintercept=0)+tBE()+theme(strip.background = element_blank(),strip.text.x=element_blank())+ylab("")

# Same Plot but for gist data

ggplot(outGist$hdiDataFrameNorm,aes(y=Parameter,x=Estimate,color=as.factor(group)))+
  geom_errorbarh(aes(xmax=high,xmin=low),height=0,lwd=1,position=position_dodgev(height=.5))+
  geom_point(position=position_dodgev(height=.5))+
  
  scale_color_discrete(guide=FALSE)+ # hide the unnessecary colour legend
  geom_text(data=data.frame(group=outGist$hdiDataFrameNorm$group,
                            Parameter =outGist$hdiDataFrameNorm$Parameter,
                            transformRule=outGist$hdiDataFrameNormLabels),#transformRule=paste0('`',hdiDataFrameNormLabels,'`')
            aes(x=40,label=transformRule),color='gray',hjust='outward',parse=T)+
  
  facet_grid(group~.,scale='free_y',space='free_y')+
  coord_cartesian(xlim=c(-45,90))+
  geom_vline(xintercept=0)+tBE()+theme(strip.background = element_blank(),strip.text.x=element_blank())+ylab("")

#+
  out = arrange(hdiDataFrameNorm,hdiDataFrameNorm[,'group'])
  out = subset(out,select=c('Parameter','low','Estimate','high','group'))
is.num <- sapply(out, is.numeric)
out[is.num] <- lapply(out[is.num], round, 2)


#+,include=F
#   datGen = data.frame(forcedFixtime = rep(1:1000,5),
#                       NumOfBubbles = sort(rep(1:5,1000)))
#   ggplot(datGen,aes(x=forcedFixtime,y=-6.166764*log(forcedFixtime)+17.16949*log(NumOfBubbles)+log(forcedFixtime)*log(NumOfBubbles)*-1.574885,color=factor(NumOfBubbles)))+geom_line()+coord_cartesian(xlim=c(0,1000))
#   ggplot(datGen,aes(x=forcedFixtime,y=-6.166764*log(forcedFixtime)+17.16949*log(NumOfBubbles)+log(forcedFixtime)*log(NumOfBubbles)*0,color=factor(NumOfBubbles)))+geom_line()+coord_cartesian(xlim=c(0,1000))
#   
#   ggplot(datGen,aes(x=forcedFixtime,y=182-5*log(forcedFixtime)+19*log(NumOfBubbles)+log(forcedFixtime)*log(NumOfBubbles)*-1.8,color=factor(NumOfBubbles)))+geom_line()+coord_cartesian(xlim=c(0,1000))+scale_x_continuous(trans='log1p')
#   ggplot(datGen,aes(x=forcedFixtime,y=186-6*log(forcedFixtime)+9.8*log(NumOfBubbles)+log(forcedFixtime)*log(NumOfBubbles)*0,color=factor(NumOfBubbles)))+geom_line()+coord_cartesian(xlim=c(0,1000))+scale_x_continuous(trans='log1p')
#   
#   
#   
# 
#     ggplot(data.3mad,aes(x=forcedFixtime,y=choicetime,color=factor(NumOfBubbles)))+stat_smooth()+scale_x_continuous(trans='log1p')+coord_cartesian(xlim=(c(1,1000)))
#   lm(data = data.3mad,formula = choicetime~log(forcedFixtime)*log(as.numeric(NumOfBubbles)))
#   lm(data = data.3mad,formula = choicetime~log(forcedFixtime)+log(as.numeric(NumOfBubbles)))
  
  
ggplot(data.3mad,aes(x=forcedFixtime,y=choicetime,color=factor(NumOfBubbles)))+stat_smooth(method='gam',formula=y~s(x))+scale_x_continuous(trans='log1p',breaks=c(30,50,100,500,1000))+coord_cartesian(xlim=(c(30,1000)),ylim=c(140,200))+tBE()


#+ NoBPostPredData,results='hide'

#p.NumOfBubbles = fd_plot_postpred('log_NumOfBubbles',
#                                  mres=mres.complexStandard.3mad,
#                                  fit=stanfit,
#                                  continuous_var = F,
#                                  customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$NumOfBubbles)),
#                                  cosineau = T,nIter=cfg$nIter)




#+ NoBPostPredPlot
  ## TODO: Choose one line and only one
# p.NumOfBubbles + xlab('NumOfBubbles') + ylab('choicetime [ms]')+tBE()



#+ dataFF,results='hide'
d.forcedFixtime = fd_plot_postpred(mres=mres.complexStandard.3mad,
                                   fit=stanfit,
                                   dataRange = c(0,1500),
                                   continuous_var = T,
                                   cosineau = T,
                                   customvar = naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$forcedFixtime)),
                                   returnData=T,
                                   nIter=cfg$nIter)

#d.forcedFixtime$forcedFixtime[is.na(d.forcedFixtime$forcedFixtime)] = d.forcedFixtime[is.na(d.forcedFixtime$forcedFixtime),8]





#+ dataNoB, results='hide'

d.NumOfBubblesC = fd_plot_postpred('log_NumOfBubbles',
                                   mres=mres.complexStandard.3mad,
                                   fit=stanfit,continuous_var =F,
                                   customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$NumOfBubbles)),
                                   cosineau = T,returnData=T,
                                   nIter=cfg$nIter)
  





#+ results='hide'
d.stimulus_type = fd_plot_postpred('',
                                   mres=mres.complexStandard.3mad,
                                   fit=stanfit,continuous_var =F,
                                   customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$stimulus_type)),
                                   cosineau = T,returnData=T,
                                   nIter=cfg$nIter)
  


#+ results='hide'

d.nextBubbleAngle = fd_plot_postpred('',
                                     mres=mres.complexStandard.3mad,
                                     fit=stanfit,continuous_var =T,
                                     customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$nextBubbleAngle)),
                                     cosineau = T,returnData=T,
                                     nIter=cfg$nIter)

d.prevBubbleAngle = fd_plot_postpred('',
                                     mres=mres.complexStandard.3mad,
                                     fit=stanfit,continuous_var =T,
                                     customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$prevBubbleAngle)),
                                     cosineau = T,returnData=T,
                                     nIter=cfg$nIter)


  


#+ results='hide'
d.angleDiff = fd_plot_postpred('angleDiff',
                               mres=mres.complexStandard.3mad,
                               fit=stanfit,continuous_var =T,
                               cosineau = T,returnData=T,
                                customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$angleDiff)),
                               nIter=cfg$nIter)

d.trialNum = fd_plot_postpred('`as.numeric(trialNum)`',
                               mres=mres.complexStandard.3mad,
                               fit=stanfit,continuous_var =T,
                               cosineau = T,returnData=T,
                               customvar=naRM(mres.complexStandard.3mad@frame,as.numeric(data.3mad$trialNum)),
                               nIter=cfg$nIter)


#+ results='hide'
d.nextBubbleDist = fd_plot_postpred('',
                                    mres=mres.complexStandard.3mad,
                                    fit=stanfit,continuous_var =T,
                                    cosineau = T,returnData=T,
                                    customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$nextBubbleDist),
                                    nIter=cfg$nIter)
d.prevBubbleDist = fd_plot_postpred('',
                                    mres=mres.complexStandard.3mad,
                                    fit=stanfit,continuous_var =T,
                                    cosineau = T,returnData=T,
                                    customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$prevBubbleDist),
                                    nIter=cfg$nIter)

d.bubbleY = fd_plot_postpred('',
                                    mres=mres.complexStandard.3mad,
                                    fit=stanfit,continuous_var =T,
                                    cosineau = T,returnData=T,
                                    customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$bubbleY),
                                    nIter=cfg$nIter)
d.bubbleX = fd_plot_postpred('',
                             mres=mres.complexStandard.3mad,
                             fit=stanfit,continuous_var =T,
                             cosineau = T,returnData=T,
                             customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$bubbleX),
                             nIter=cfg$nIter)

d.centerdistance = fd_plot_postpred('',
                             mres=mres.complexStandard.3mad,
                             fit=stanfit,continuous_var =T,
                             cosineau = T,returnData=T,
                             customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$centerDistance),
                             dataRange = c(0.5,13.5), # for 0 - 0.5 only few data points exist and vice versa for 13.5 - 14
                             nIter=cfg$nIter)
 

d.bubbleNum = fd_plot_postpred('',
                                    mres=mres.complexStandard.3mad,
                                    fit=stanfit,continuous_var =T,
                                    cosineau = T,returnData=T,
                                    customvar=naRM(mres.complexStandard.3mad@frame,data.3mad$bubbleNum),
                                    nIter=cfg$nIter)
#+ results='hide'

d.ff_NoB = fd_plot_postpred('',
                                    mres=mres.complexStandard.3mad,
                                    fit=stanfit,continuous_var =list(T,F),
                                    cosineau = T,returnData=T,
                                    customvar=list(naRM(mres.complexStandard.3mad@frame,data.3mad$forcedFixtime),as.numeric(naRM(mres.complexStandard.3mad@frame,data.3mad$NumOfBubbles))),
                            dataRange = list(c(0,1000),c(1,5)),
                                    nIter=cfg$nIter)



#+ interactionFF_NoB,results='hide',fig.asp=0.25
# INTERACTION FF / NOB PLOTS 
 p3 = ggplot(subset(d.ff_NoB,with(d.ff_NoB,type=='subfit.subject'&variable=='mean')),
              aes(x=as.numeric(as.character(customvar_1)),group=customvar_2,fill=factor(customvar_2),color=factor(customvar_2),
                 ymax=high,ymin=low,y=median))+
      geom_ribbon(alpha=0.1)+
      geom_line()+facet_grid(.~predReal)+
      tBE(base_size = 10)



p1 = ggplot(subset(d.ff_NoB,with(d.ff_NoB,type=='subfit.subject'&variable=='mean')),
       aes(x=as.numeric(as.character(customvar_1)),group=interaction(predReal,factor(customvar_2)),fill=factor(customvar_2),color=factor(customvar_2),
           ymax=high,ymin=low,y=median))+
  stat_smooth(geom='line',method='gam',formula=y~s(x))+
  geom_ribbon(alpha=0.2)+
  geom_line(alpha=0.3)+facet_grid(predReal~customvar_2)+xlab("Forced Fixationtime [ms]")+ylab("Choicetime [ms]")+
  coord_cartesian(ylim=c(140,190))+scale_x_continuous(breaks=c(0,500,1000))+
  tBE(base_size = 10)+scale_color_discrete(guide=F)+scale_fill_discrete(guide=F)


datModified_real = subset(data.3mad,data.3mad$forcedFixtime<1000)
meanList = ddply(datModified_real,.(NumOfBubbles),summarise,mean(choicetime))

datModified = subset(d.ff_NoB,with(d.ff_NoB,type=='subfit.subject'&variable=='mean'&predReal=='real'))
datModified$customvar_1 = as.numeric(as.character(datModified$customvar_1))

datModified2 = ddply(datModified,.(customvar_2),function(x,meanList){x$median=x$median-meanList$`mean(choicetime)`[as.numeric(as.character(x$customvar_2[1]))];return(x)},meanList)
p2 = ggplot(datModified2,
       aes(x=as.numeric(as.character(customvar_1)),fill=factor(customvar_2),color=factor(customvar_2),
           ymax=high,ymin=low,y=median))+
  #geom_line()+
  stat_smooth(geom='line',method='gam',formula=y~s(x))+xlab("Forced Fixationtime [ms]")+ylab("Choicetime [ms]")+
  scale_x_continuous(breaks=c(0,500,1000))+coord_cartesian(ylim=c(-15,15))+
  tBE(base_size = 10)+scale_color_discrete('Number of Bubbles')

cowplot::plot_grid(p1,p2,labels=c('A','B'))


#+,fig.asp=0.5
# FORCED FIXATION TIME PLOTS
ylim_common = c(140,175)
p.ff1 = plot_posteriorpredictive(d.forcedFixtime)+xlab('Forced Fixationtime [ms]')+ylab("Choicetime [ms]")+
  coord_cartesian(xlim=c(0,1000),ylim=ylim_common)+theme(legend.position=c(.9,.75))+scale_color_discrete('')


d = ddply(data.3mad,.(subject),function(x){x$choicetime=x$choicetime-mean(x$choicetime,na.rm=T);x})
p.ff2= ggplot(d,aes(x=forcedFixtime,y=choicetime,group=subject))+
  xlab('Forced Fixationtime [ms]')+ylab('Subjectwise Choicetime [ms]')+
  geom_line(method='gam',stat='smooth',formula=y~s(x),alpha=0.3,se=F)+coord_cartesian(xlim=c(0,1000),ylim=c(-25,20))+tBE()

#d.histograms = ddply(data.3mad,.(subject),function(x){y=hist(x$forcedFixtime,breaks=seq(0,3000,by=10),plot=FALSE);return(data.frame(mids=y$mids,count=y$counts))})
#p.ff3 = ggplot(d.histograms,aes(x=mids,y=count,group=subject))+
#  geom_line(alpha=0.1)+
#  xlab('Forced Fixationtime [ms]')+ylab('Trials [#]')+
#  stat_summary(aes(group=NULL),geom='line')+
#  coord_cartesian(xlim=c(1,1000))+
#  tBE()

library(cowplot)
cowplot::plot_grid(p.ff1,p.ff2,labels = c('A','B'), rel_widths=c(2,1))


#+,fig.asp=0.5
# PLOT NUMBER OF BUBBLES
p.nob1 = plot_posteriorpredictive(d.NumOfBubblesC)+xlab('Number of Bubbles')+coord_cartesian(ylim=ylim_common)+scale_color_discrete('')+scale_shape_discrete('')+
      theme(legend.position=c(.9,.25))
p.nob2 = ggplot(d,aes(x=NumOfBubbles,y=choicetime,group=subject))+stat_summary(geom='line',alpha=0.1)+
  stat_summary(aes(group=NULL),geom='pointrange')+tBE()+xlab('Number of Bubbles')+ylab('Subjectwise Choicetime [ms]')
cowplot::plot_grid(p.nob1,p.nob2,rel_widths=c(2,1),labels=c('A','B'))  
  


# PLOT STIMULUS TYPE  
plot_posteriorpredictive(d.stimulus_type)+xlab('stimulus type')+coord_cartesian(ylim=ylim_common)


# PLOT ANGLE STUFF
cowplot::plot_grid(plot_posteriorpredictive(d.nextBubbleAngle)+xlab('angle to next bubble [°]')+ylab('choicetime [ms]')+coord_cartesian(ylim=c(153,167))+scale_x_continuous(breaks=c(-180,-90,0,90,180))+theme(legend.position=c(.9,.25)),
                   
                   plot_posteriorpredictive(d.angleDiff)+xlab('difference in angle between bubbles [°]')+ylab('')+coord_cartesian(ylim=c(153, 167))+scale_x_continuous(breaks=c(-180,-90,0,90,180))+scale_color_discrete(guide=F)+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
                   
                  plot_posteriorpredictive(d.nextBubbleDist)+xlab('distance to next bubble [°]')+ylab('')+coord_cartesian(ylim=c(135,180))+scale_color_discrete(guide=F)+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
                  
                  plot_posteriorpredictive(d.bubbleX)+xlab('X-Position [°]')+ylab('')+coord_cartesian(ylim=c(135,180))+scale_color_discrete(guide=F)+scale_x_continuous(breaks=c(-10,0,10))+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
                  plot_posteriorpredictive(d.bubbleY)+xlab('Y-Position [°]')+ylab('')+coord_cartesian(ylim=c(135,180))+scale_color_discrete(guide=F)+scale_x_continuous(breaks=c(-7.5,0,7.5))+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
                  plot_posteriorpredictive(d.centerdistance)+xlab('Center Distance [°]')+ylab('')+coord_cartesian(ylim=c(135,180))+scale_color_discrete(guide=F)+scale_x_continuous(breaks=c(0,5,10))+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
                  labels=c("A","B","C","D",'E','F')
                   )

cowplot::plot_grid(
plot_posteriorpredictive(d.trialNum)+xlab('trial number')+ylab('')+coord_cartesian(ylim=c(153,167))+scale_color_discrete(guide=F)+scale_x_continuous(breaks=c(0,32,64,96,128))+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
plot_posteriorpredictive(d.bubbleNum)+xlab('bubble number')+ylab('')+coord_cartesian(ylim=c(153,167),xlim=c(0,25))+scale_color_discrete(guide=F)+scale_x_continuous(breaks=c(0,32,64,96,128))+scale_fill_discrete(guide=F)+scale_linetype_discrete(guide=F),
labels=c("A","B"))
#plot_posteriorpredictive(d.prevBubbleAngle)+xlab('prevbubbleangle')+coord_cartesian(ylim=ylim_common)


#+ 2D x-y plot
removeNSmaller10=function(x){return(ifelse(length(x)<1,NaN,mean(x)))};

ggplot(data, aes(chosenBubbleX, chosenBubbleY, z = choicetime)) + stat_summary_hex(bins=10,fun=removeNSmaller10)+coord_fixed()+scale_fill_continuous(name="SRT")


removeNSmaller10=function(x){return(ifelse(length(x)<1,NaN,mean(x)))};

ggplot(ddply(data,.(subject),transform,choicetime=choicetime-mean(choicetime)), aes(chosenBubbleX, chosenBubbleY, z = choicetime)) + stat_summary_hex(bins=4,fun=removeNSmaller10)+coord_fixed()+scale_fill_continuous(name="SRT")+facet_wrap(~subject)


#+ misc effect sizes
mcmc = rstan::extract(stanfit)
# 11 - 14 are cos/sin nextBubble see also variable `label_dataframe`
lkup = function(x)which(label_dataframe$Label == x)

y = sapply(seq(-pi,pi,0.1),function(x)sin(x)*mcmc$beta[,lkup('sin_prevBubbleAngle')] + cos(x)*mcmc$beta[,lkup('cos_prevBubbleAngle')] + sin(2*x)*mcmc$beta[,lkup('sin2_prevBubbleAngle')] + cos(2*x)*mcmc$beta[,lkup('cos2_prevBubbleAngle')])
quantile(aaply(y,1,function(x)min(x)-max(x)),c(0.025,0.5,0.975))/2

y = sapply(seq(-pi,pi,0.1),function(x)sin(x)*mcmc$beta[,lkup('sin_nextBubbleAngle')] + cos(x)*mcmc$beta[,lkup('cos_nextBubbleAngle')] + sin(2*x)*mcmc$beta[,lkup('sin2_nextBubbleAngle')] + cos(2*x)*mcmc$beta[,lkup('cos2_nextBubbleAngle')])

quantile(aaply(y,1,function(x)min(x)-max(x)),c(0.025,0.5,0.975))/2

