calc_boot_ci = function(dat){
  mean.fun <- function(dat, idx) mean(dat[idx], na.rm = TRUE)
  
  b = boot::boot(data=dat,statistic = mean.fun,R=1000)
  boot::boot.ci(b,type='bca')$bca[c(4,5)]
}

fd_helper_ddply_MeanCIoverSubjects = function(df,name){
  library(plyr)
  #browser()
  subjectMean = ddply(df,"subject",function(x){mean(x$choicetime,na.rm=TRUE)})
  df = ddply(df,"subject",function(x){
    ddply(x,name,function(y){meanChoice = mean(y$choicetime,na.rm = TRUE)})
  })

  colnames(df)[length(df)]<-'choicetime'
  #http://drsmorey.org/bibtex/upload/Morey:2008.pdf
  print("Calculating Cousineau Corrected CI (subject intercept normalized)")
  x = ddply(df,name,function(x,sMeans){
    if(length(x[,1])<1) return(data.frame(meanChoice = NA,conf.low=NA,conf.high=NA))
    if(length(x[,1]) <2){
      
      warning('sorry cant calculate the CI, not enough subjects,filling NA')
      ci = c(NA,NA)
      
    }else{
      
      # why the hell the matching? I don't understand... but it also does not hurt
      match = sMeans$subject%in%x$subject
      ci = calc_boot_ci(x$choicetime-sMeans$V1[match]+mean(sMeans$V1[match]))# cousineau correction (normalize e.g. get rid of subject intercept)
    }
    data.frame(meanChoice = mean(x$choicetime,na.rm = TRUE),
               conf.low   = ci[1],
               conf.high  = ci[2])},
    subjectMean)
}


