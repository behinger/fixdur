# Load data and perform last preprocessing steps (outlier detection, only take goodFix)
d = fd_loaddata('/home/student/j/jschepers/thesis/fixdur_git/scripts/preprocessing/all_res_exp2.RData',clean = T)

# Plots for result section
library(ggplot2)
library(dplyr)
d$NumOfBubbles = as.numeric(as.character(d$NumOfBubbles))
#data_w = data[data$goodFix,]
ggplot(d,aes(x=forcedFixtime,y=choicetime,color=whitecondition))+geom_smooth(method='loess')+coord_cartesian(xlim = c(0,1000),ylim = c(150,200)) + tBE(base_size = 20) +xlab('Forced fixation time [ms]') + ylab('Choice time [ms]')

ggplot(d,aes(x=NumOfBubbles,y=choicetime,color=whitecondition))+stat_summary()+xlab('Number of bubbles')+ylab('Choice time [ms]')+tBE(base_size = 20) 

# Model fitting: Linear mixed model
library(lme4)

# Plot: distribution of CTs (saccade latencies) for each subject
subject_means = aggregate(d['choicetime'],list(d$subject),mean)
condition_means = aggregate(d['choicetime'],list(d$whitecondition),mean)
mean_ct = mean(subject_means$choicetime)

ggplot(subject_means,aes(x=choicetime))+geom_histogram(color='black',fill='blue',alpha=0.5)
ggplot(d,aes(x=choicetime,color=subjects))+geom_density() + geom_vline(xintercept=mean_ct,alpha=0.6)+tBE()+scale_color_discrete(guide=F)+xlab('Choice time [ms]')+ylab('Probability density')
ggplot(d,aes(x=choicetime,color=whitecondition))+geom_density() + tBE()+xlab('Choice time [ms]')+ylab('Probability density')

# Model fitting
d_WF = d%>%subset(whitecondition == FALSE & NumOfBubbles>0)
model = lmer(data=d_WF,formula=choicetime ~ 1 + log(forcedFixtime) + log(NumOfBubbles) + (1 + log(forcedFixtime)+ log(NumOfBubbles)|subject))
d_WF$predict_CT = predict(model)

# Plots: Model fit (FFT and NoB)
ggplot(d_WF,aes(x=forcedFixtime,y=choicetime))+geom_smooth(color='black')+geom_smooth(aes(y=predict_CT),color='red')+coord_cartesian(xlim = c(0,1000),ylim = c(150,200)) + tBE(base_size = 20) +xlab('Forced fixation time [ms]') + ylab('(Predicted) choice time [ms]')
ggplot(d_WF,aes(x=NumOfBubbles,y=choicetime))+stat_summary(color='black')+stat_summary(aes(x=NumOfBubbles+0.5,y=predict_CT),color='red')+xlab('Number of bubbles')+ylab('(Predicted) choice time [ms]')+tBE(base_size = 20) 

# Information about model parameter
# summary(model)
confint(model,method='Wald') # compute confidence intervals

# Model comparison
model2 = lmer(data=d%>%subset(whitecondition == FALSE & NumOfBubbles>0),formula=choicetime ~ 1 + log(forcedFixtime) + log(NumOfBubbles) + (1 + log(NumOfBubbles)|subject))

model0 = lmer(data=d%>%subset(whitecondition == FALSE & NumOfBubbles>0),formula=choicetime ~ 1 + log(forcedFixtime) + (1 + log(forcedFixtime)+ log(NumOfBubbles)|subject))

# Compute p-values (bootstrapping)
# summary(pbkrtest::PBmodcomp(model,model0,nsim=1000))

# Plot correlation between intercept, FFT and NoB
m1 = model
ix=c(1,2)
gaus2d.mean  <- fixef(m1)[ix]#[c(2,4)]
gaus2d.cov   <- VarCorr(m1)$subject[ix,ix]#[c(2,4),c(2,4)] 

data.grid <- expand.grid(s.1 = seq(gaus2d.mean[1]-5*sqrt(gaus2d.cov)[1,1], gaus2d.mean[1]+5*sqrt(gaus2d.cov)[1,1], length.out=200), s.2 = seq(gaus2d.mean[2]-5*sqrt(gaus2d.cov)[2,2], gaus2d.mean[2]+5*sqrt(gaus2d.cov)[2,2], length.out=200))
#data.grid <- expand.grid(s.1 = seq(-40,150, length.out=200), s.2 = seq(-40, 20, length.out=200))

q.samp <- cbind(data.grid, prob = mvtnorm::dmvnorm(data.grid, mean = gaus2d.mean, sigma = gaus2d.cov))
subjectDat = data.frame(coef(m1)$subject[,ix])
ggplot() + 
  geom_tile(data=q.samp,aes(x=s.1, y=s.2, fill=prob))+
  geom_point(data=subjectDat,aes_string(x=colnames(subjectDat)[1],y=colnames(subjectDat)[2]),color="red")