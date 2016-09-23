fd_loaddata <- function(dataOrPath = 'cache/data/all_res.RData',clean=TRUE,returnOutlier=FALSE){
# Load and generate the data
#----
#mres = glmer(formula = y ~ tl+tr +ia + ia:tl  +  ia:tr+(1|sub),data=dat.raw,family=binomial)
read_dat_raw = function(dataOrPath){
  if(is.character(dataOrPath)){
    load(dataOrPath)
    dat <- data
    #dat <- read.csv('../all_res.csv')
  }else{
    if(is.data.frame(dataOrPath)){
      dat <- dataOrPath
    }else{
      stop('cannot recognize what to load')
    }
  }
  
  dat$orgOrdering = 1:length(dat$choicetime)
  add_lagged_timings <- function(dat){
    
    library('plyr')
    
    dat$lag1_choicetime = rep(NA,length(dat$choicetime))
    dat$lag1_forcedFixtime = rep(NA,length(dat$choicetime))
    dat$prevBubbleDist = rep(NA,length(dat$choicetime))
    dat$prevBubbleAngle = rep(NA,length(dat$choicetime))
    dat$nextBubbleDist = rep(NA,length(dat$choicetime))
    dat$nextBubbleAngle = rep(NA,length(dat$choicetime))
    dat$prevFixDist = rep(NA,length(dat$choicetime))
    dat$prevFixAngle = rep(NA,length(dat$choicetime))
    dat$nextFixDist = rep(NA,length(dat$choicetime))
    dat$nextFixAngle = rep(NA,length(dat$choicetime))
    dat2 = ddply(dat,"subject",function(x){
      b = ddply(x,"trialNum",function(y){
        #browser()
        
        #for (tr in dat[dat$subject,]$trialNum){
        #sel = dat$subject == s & dat$trialNum == tr
        vecLength = length(y$choicetime)
        CT = y$choicetime[1:vecLength-1]
        FF = y$forcedFixtime[1:vecLength-1]
        
       # browser()
        chosenBubbleX = c(y$bubbleX[1:vecLength])
        chosenBubbleY = c(y$bubbleY[1:vecLength])
        
        currentBubbleX = c(NA,y$bubbleX[1:(vecLength-1)])
        currentBubbleY = c(NA,y$bubbleY[1:(vecLength-1)])
          
        prevBubbleX = c(NA,NA,y$bubbleX[1:(vecLength-2)])
        prevBubbleY = c(NA,NA,y$bubbleY[1:(vecLength-2)])
          
        bubbleAfterChosenX = c(y$bubbleX[2:vecLength],NA)
        bubbleAfterChosenY = c(y$bubbleY[2:vecLength],NA)
          
        #chosenBubbleX = c(y$bubbleX[2:vecLength],NA)
        #chosenBubbleY = c(y$bubbleY[2:vecLength],NA)
        #prevBubbleX = c(NA,y$bubbleX[1:vecLength-1])
        #prevBubbleY = c(NA,y$bubbleY[1:vecLength-1])
        #currBubbleX = c(y$bubbleX[1:vecLength])
        #currBubbleY = c(y$bubbleY[1:vecLength])
        
        # Fixations are tricky and we removed them for now
        #chosenFixX = y$nextFixX[1:vecLength]
        #chosenFixY = y$nextFixY[1:vecLength]
        
        #prevFixX = c(NA,y$prevFixX[1:vecLength-1])
        #prevFixY = c(NA,y$prevFixY[1:vecLength-1])
        #nextFixX = c(y$nextFixX[2:vecLength],NA)
        #nextFixY = c(y$nextFixY[2:vecLength],NA)
        
        
        prevBubbleDist = sqrt((prevBubbleX-currentBubbleX)**2+(prevBubbleY-currentBubbleY)**2)
        nexBubbleDist = sqrt((chosenBubbleX-currentBubbleX)**2+(chosenBubbleY-currentBubbleY)**2)
        #prevFixDist = sqrt((prevFixX-currentBubbleX)**2+(prevFixY-currentBubbleY)**2)
        #nextFixDist = sqrt((nextFixX-currentBubbleX)**2+(nextFixY-currentBubbleY)**2)
        
        prevBubbleAngle = atan2((currentBubbleY-prevBubbleY),(currentBubbleX-prevBubbleX))*180/pi
        nexBubbleAngle  = atan2((chosenBubbleY-currentBubbleY),(chosenBubbleX-currentBubbleX))*180/pi
        
        prev_prevBubbleAngle = c(NA,prevBubbleAngle[1:(length(prevBubbleAngle)-1)])
        next_nexBubbleAngle =  c(nexBubbleAngle[2:length(nexBubbleAngle)],NA)
        #prevFixAngle    = atan2((currentBubbleY-prevFixY),(currentBubbleX-prevFixX))*180/pi
        #nextFixAngle    = atan2((nextFixY-currentBubbleY),(nextFixX-currentBubbleX))*180/pi        
        
        #sum(diff(dat[sel,"bubbleNum"]) != 1)
        outY = data.frame(lag1_choicetime = c(NA,CT),
                          lag1_forcedFixtime = c(NA,FF),
                          prevBubbleDist = prevBubbleDist,
                          nextBubbleDist = nexBubbleDist,
                          prevBubbleAngle = prevBubbleAngle,
                          nextBubbleAngle = nexBubbleAngle,
                          #prevFixDist = prevFixDist,
                          #prevFixAngle = prevFixAngle,
                          #nextFixDist = nextFixDist,
                          #nextFixAngle = nextFixAngle,
                          choicetimeOrg = y$choicetime,
                          chosenBubbleX = chosenBubbleX,
                          chosenBubbleY = chosenBubbleY,
                          currBubbleX = currentBubbleX,
                          currBubbleY = currentBubbleY,
                          prevBubbleX = prevBubbleX,
                          prevBubbleY = prevBubbleY,
                          prev_prevBubbleAngle =   prev_prevBubbleAngle,
                          next_nextBubbleAngle = next_nexBubbleAngle,
                          
                          next_chosenBubbleX = bubbleAfterChosenX,
                          next_chosenBubbleY = bubbleAfterChosenY,
                          forcedfixtimeOrg = y$forcedFixtime,
                          orgOrdering = y$orgOrdering)
      })
    })
    
    dat2 = dat2[with(dat2,order(dat2$orgOrdering)),]
    if (sum(dat2$choicetimeOrg != dat$choicetime)!=0){
      error('problem with sorting!')
    }
    listofvars = c('lag1_choicetime','lag1_forcedFixtime',
                   'prevBubbleDist','nextBubbleDist','prevBubbleAngle','nextBubbleAngle',
                   #'prevFixDist','prevFixAngle','nextFixDist','nextFixAngle',
                   'chosenBubbleX','chosenBubbleY',
                   'currBubbleX','currBubbleY',
                   'prev_prevBubbleAngle',
                   'next_nextBubbleAngle',
                   'prevBubbleX','prevBubbleY','next_chosenBubbleX','next_chosenBubbleY')
    dat[,listofvars] = dat2[,listofvars]
    return(dat)
  }
  
  dat = add_lagged_timings(dat)
  dat$prevHorizSacc = (abs(dat$prevBubbleAngle)<45)|(abs(dat$prevBubbleAngle)>135)
  dat$nextHorizSacc = (abs(dat$nextBubbleAngle)<45)|(abs(dat$nextBubbleAngle)>135)
  a = (dat$prevBubbleAngle - dat$nextBubbleAngle )%%360 # Calculate the difference of consecutive angles and modulo 360 it 
  a[a>180&!is.na(a)]=360-a[a>180&!is.na(a)] # Here we compensate for the +-180deg, e.g. -130 (=310 now because of modulo) is the same as 130
 
  #We currently don't support the fixation 
    #  b = (dat$prevFixAngle - dat$nextFixAngle )%%360 # Calculate the difference of consecutive angles and modulo 360 it 
    #  b[b>180&!is.na(b)]=360-b[b>180&!is.na(b)] # Here we compensate for the +-180deg, e.g. -130 (=310 now because of modulo) is the same as 130
    #dat$angleDiffFix = b
  dat$angleDiff = a
  

  # This is the anglediff without abs
  dat$angleDiff_signed = ((dat$prevBubbleAngle - dat$nextBubbleAngle ) - 180)%%360-180
  
  
  dat$prev_angleDiff = ((dat$prev_prevBubbleAngle - dat$prevBubbleAngle ) - 180)%%360-180
  dat$next_angleDiff = ((dat$nextBubbleAngle - dat$next_nextBubbleAngle ) - 180)%%360-180
  dat$angle180 = a>170
  
  
  # Fix the dispX / dispY thing to have lists instead of factors
  # This takes quite a while because I need to regexp it -.0
  print('converting dispX/dispY')
  dispX = NULL
  dispY = NULL
  for(i in 1:dim(dat)[1]){
    if(i%%1000==0) print(i)
    dispX[i] = list(sapply(regmatches(as.character(dat[i,'dispX']),gregexpr(pattern = "[\\d]+",as.character(dat[i,'dispX']),perl=T)),
                           1,FUN=as.numeric))
    dispY[i] = list(sapply(regmatches(as.character(dat[i,'dispY']),gregexpr(pattern = "[\\d]+",as.character(dat[i,'dispY']),perl=T)),
                           1,FUN=as.numeric))
  }
  dat$dispX = dispX
  dat$dispY = dispY
  #dat = ddply(dat,.(subject,trialNum),transform,c(dispX(1:(length(dispX)-1)),na))
  #dat = ddply(dat,.(subject,trialNum),transform,c(dispY(1:(length(dispY)-1)),na))
  
  idx = which(dat$bubbleNum==0)-1 #could possibly be problematic if there exist a 1-trial subject. but the ddply version is superslow!
  idx = idx[idx>0] #very first trial woukld be negative
  print(length(idx))
  dat$dispX[idx] = NA
  dat$dispY[idx] = NA
  #dat$(sqrt(dat$bubbleX**2+dat$bubbleY**2)
  return(dat)
}


process_dat_raw = function(dat){
  
  data.clean = subset(dat,dat["goodFix"]==1)#&dat["choicetime"]<400)
  data.clean = subset(data.clean,data.clean["forcedFixtime"]>0)#&dat["choicetime"]<400)
  data.clean = subset(data.clean,abs(data.clean$forcedFixtime - data.clean$plannedForcedFix)<=40)#&dat["choicetime"]<400)
  larger4= data.clean$choicetime>4
  data.clean = data.clean[larger4,] #we don't want so small choicetimes
  #cleanDat = subset(cleanDat,as.numeric(cleanDat["subject"][,1])<5)#&dat["choicetime"]<400)
  data.clean$subject = as.factor(data.clean$subject)
  data.clean$NumOfBubbles = as.factor(data.clean$NumOfBubbles)
  data.clean$stimulus_type = as.factor(data.clean$stimulus_type)
  return(data.clean)
}


dat = read_dat_raw(dataOrPath)
if(!clean){
 return(dat) 
}
 #browser() 
#return(dat)
data.clean = process_dat_raw(dat)

# will not output anything if not called manually
#ggplot(dat[1:20,],aes(x=bubbleX,y=bubbleY))+geom_point()+geom_path(color='gray')+geom_text(aes(label=1:20),hjust=2,vjust=0.3)+
#                  geom_text(aes(label=round(prevBubbleAngle)),vjust=-1,hjust=0,color='darkgreen')+
#                  geom_text(aes(label=round(nextBubbleAngle)),vjust=1,hjust=0,color='blue')+
#                 geom_text(aes(label=round(angleDiff)),vjust=0.3,hjust=-2,color='darkred')+
#                 coord_fixed()


#Winsorized Data
# Helpful to select the trimming thingy
#data.winsor =data.clean
#ddply(data.clean,"NumOfBubbles",function(x){q<-quantile(x$choicetime,c(.01,.03,.05,.10,.20,.80,.90,.95,.97,.99))})
#quantile(data.clean$choicetime,c(.01,.03,.05,.10,.20,.80,.90,.95,.97,.99))
#data.winsor$choicetime = winsor(data.winsor$choicetime,trim = 0.1)


#Cook Outlier Data
#load(file="~/Documents/fixdur/analysis/R/grid/infl_obs.RData")
#co = cooks.distance(infl);
#data.cook =data.clean

#load(file="grid/infl_co.RData")
#co = co[larger4]
#outlier.cook = co<4/37177
#data.cook = data.cook[outlier.cook,]

#Trimmed Data
#data.trim =data.clean
outlier.trim = data.clean$choicetime>quantile(data.clean$choicetime,probs=0.1) &
  data.clean$choicetime<quantile(data.clean$choicetime,probs=0.9)
#data.trim = data.trim[outlier.trim,]

#<3 SD Data
data.3sd =data.clean

#
outlier.3sd = ddply(data.clean,'subject',function(x){
  data.frame(bad = x$choicetime>mean(x$choicetime)-3*sd(x$choicetime) &
                   x$choicetime<mean(x$choicetime)+3*sd(x$choicetime),
  orgOrder = x$orgOrdering)
})
outlier.3sd = outlier.3sd[with(outlier.3sd,order(outlier.3sd$orgOrder)),]
#qplot(data=data.clean,x=1:length(choicetime),y=choicetime,colour=outlier.3sd$bad)
sum(!outlier.3sd$bad)/length(outlier.3sd$bad)

data.3sd = data.3sd[outlier.3sd$bad,]

data.3mad =data.clean
# file:///home/student/b/behinger/Downloads/Leys_MAD_final-libre.pdf
# also ratcliff 1993 Page 517 states that we should eliminate between 10% and 15%
outlier.3mad = ddply(data.clean,'subject',function(x){
  data.frame(bad = x$choicetime>median(x$choicetime)-3*mad(x$choicetime) &
                   x$choicetime<median(x$choicetime)+3*mad(x$choicetime),
             orgOrder = x$orgOrdering)
})
outlier.3mad = outlier.3mad[with(outlier.3mad,order(outlier.3mad$orgOrder)),]

outlier.3mad$choicetime = data.3mad$choicetime

#qplot(data=data.clean,x=1:length(choicetime),y=choicetime,colour=outlier.3mad$bad)
sum(!outlier.3mad$bad)/length(outlier.3mad$bad)


data.3mad = data.3mad[outlier.3mad$bad,]

data.400 = data.clean
outlier.400 = data.clean$choicetime<400
data.400 = data.400[outlier.400,]




clean_previousBubbles = function(data){
  dat3 = ddply(data,"subject",function(x){
    ddply(x,"trialNum",function(y){
      data.frame(nextB = c(diff(y$orgOrdering)==1,FALSE),
                 prevB = c(FALSE,diff(y$orgOrdering)==1),
                 orgOrdering = y$orgOrdering)})})
  
  dat3 = dat3[with(dat3,order(dat3$orgOrdering)),]
  
  data$prevBubbleExists= dat3$prevB
  data$nextBubbleExists= dat3$nextB
  
  
  
  data$prevBubbleDist_c = data$prevBubbleDist
  data$prevBubbleAngle_c = data$prevBubbleAngle
  data$prevHorizSacc_c = data$prevHorizSacc
  data$angleDiff_c = data$angleDiff
  
  
  data$prevBubbleDist_c[!data$prevBubbleExists] = NA
  data$prevBubbleAngle_c[!data$prevBubbleExists] = NA
  data$prevHorizSacc_c[!data$prevBubbleExists] = NA
  data$angleDiff_c[!data$prevBubbleExists|!data$nextBubbleExists] = NA  
  return(data)
}

data.clean = clean_previousBubbles(data.clean)
data.400 = clean_previousBubbles(data.400)
data.3sdFF500 = data.3sd
data.3sdFF500 = data.3sdFF500[data.3sdFF500$forcedFixtime<500,]
data.3sdFF500 = clean_previousBubbles(data.3sdFF500)
data.3mad = clean_previousBubbles(data.3mad)
data.3sd = clean_previousBubbles(data.3sd)


data.3mad$log_forcedFixtime = log(data.3mad$forcedFixtime)
data.3mad$log_NumOfBubbles = log(as.numeric(data.3mad$NumOfBubbles))
data.3mad$log_nextBubbleDist = log(data.3mad$nextBubbleDist)
data.3mad$log_prevBubbleDist = log(data.3mad$prevBubbleDist)
data.3mad$sin_nextBubbleAngle = sin(data.3mad$nextBubbleAngle/180*pi)
data.3mad$cos_nextBubbleAngle = cos(data.3mad$nextBubbleAngle/180*pi)
data.3mad$sin_prevBubbleAngle = sin(data.3mad$prevBubbleAngle/180*pi)
data.3mad$cos_prevBubbleAngle = cos(data.3mad$prevBubbleAngle/180*pi)
data.3mad$sin2_nextBubbleAngle = sin(2*data.3mad$nextBubbleAngle/180*pi)
data.3mad$cos2_nextBubbleAngle = cos(2*data.3mad$nextBubbleAngle/180*pi)
data.3mad$sin2_prevBubbleAngle = sin(2*data.3mad$prevBubbleAngle/180*pi)
data.3mad$cos2_prevBubbleAngle = cos(2*data.3mad$prevBubbleAngle/180*pi)

#.s = function(x){scale(x,center = TRUE,scale = TRUE}
#lmer(formula = choicetime~.s(log(forcedFixtime))+forcedFixtime
#data.3mad.transformed = data.3mad
#ith(data.3mad.transformed,forcedFixtime = .s(ForcedFixtime))

#data.3mad.transformed.forcedFixtime = .s(data.3mad.transformed.forcedFixtime)

#data.3mad$CT_log = log(data.3mad$choicetime)
#data.3mad$CT_root = sqrt(data.3mad$choicetime)
#data.3mad$CT_1_x = -1 / data.3mad$choicetime
#data.3mad$CT_1_x_square = -1 / data.3mad$choicetime^2
if (returnOutlier){
  
 return(outlier.3mad) 
}
return(data.3mad)
}