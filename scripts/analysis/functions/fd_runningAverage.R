fd_runningAverage <-function (data,grouping=NULL,selection = NULL,windowType=c("rect","gaussian"),
                              xmin=0,xmax = 1500,nX = NULL,winsize = 50,stat=c("convFilter.mean","winsor","median","mean","std","winsor.std")){
  stat <- match.arg(stat)
  windowType <- match.arg(windowType)
  
  if ((stat=="std" | stat=="winsor.std" | stat=="median") & windowType == "gaussian"){print("No support for gaussian window and STD calculation")}
  
  library("psych")
  outDat = data.frame()
  
  groupLevels = as.numeric(levels(unique(data[grouping])[,]))
  print("Running average for following levels:")
  print(groupLevels)
  if (is.null(grouping)){
    groupLevels = 1
  }
  if(is.null(nX)){nX = xmax}
  
  for (groupVar in groupLevels){
    print(sprintf("Calculating %s:%i from %i",grouping,groupVar,length(groupLevels)))
    grid <- with(data, seq(xmin+0.5,xmax-0.5, length = nX))
    gridY <- c()
    
 
    if (!is.null(grouping)){
      sel = data[grouping]==groupVar
    }else{
      sel = !logical(length(data$forcedFixtime))
    }
    if (!is.null(selection)){
      sel = sel & selection
    }
    if(stat=='convFilter.mean'){
      #outDat = rbind(outDat,data.frame(x=,y=c(gridY,NA),grouping=groupVar))
      n = length(data[sel,]$choicetime)
      k = min(max(n/20,20),n/2)  # Window size (in datapoints...)
  #    
  #    k <- min(ceiling(n/256), n/2)  # Window size
      kernel <- c(dnorm(seq(0, 3, length.out=k)))
      kernel <- c(kernel, rep(0, n - 2*length(kernel) + 1), rev(kernel[-1]))
      kernel <- kernel / sum(kernel)
      
#      kernel = dnorm(seq(-3,3,length.out=k))
      
      #kernel =  array(1/k,dim = k)
      sI = sort(data[sel,]$forcedFixtime,index.return=TRUE)
      
        yMean = Re(convolve(data[sel,]$choicetime[sI$ix],kernel))
        outDat = rbind(outDat,data.frame(x=sI$x,y=yMean,grouping=groupVar))
      
      
    }else{
    
    for(i in seq(1,length(grid)-1)){
      #gridY[i] = mean(data$choicetime[sel&data$forcedFixtime>grid[i]&data$forcedFixtime<grid[i+1]])
      
      minG = grid[i]-winsize
      maxG = grid[i]+winsize
      
      minG[minG<0]=0
      selLoop = sel&data$forcedFixtime>minG&data$forcedFixtime<maxG
      
      switch(windowType,
             rect={
               weights = array(1/sum(selLoop),dim = sum(selLoop))
             },
             gaussian={
               weights = dnorm(data$forcedFixtime[which(selLoop)] - grid[i],sd=20)
             })
      
      weights = weights/sum(weights)
      
      dataLoop = data$choicetime[selLoop]
      infDat = dataLoop==Inf
      if(sum(infDat>0)){
        warning('Choicetimes that are infinite found')
      }
      dataLoop = dataLoop[!infDat]
      if (stat == "winsor" | stat=="winsor.std"){
        dataLoop = winsor(dataLoop,trim=0.2)
      }else{
        dataLoop = dataLoop
      }
      if (stat == "mean" | stat == "winsor"){
        gridY[i] = sum(dataLoop*weights)
      }else if(stat=="median"){ #std
        gridY[i] = median(dataLoop)
      }else{
        gridY[i] = sd(dataLoop)
      }
    
    }
    
    outDat = rbind(outDat,data.frame(x=as.numeric(filter(grid,c(0.5,0.5))),y=c(gridY,NA),grouping=as.factor(groupVar)))
    }
  }
  if(!is.null(grouping)){
    colnames(outDat) <- c('forcedFixtime','choicetime',grouping)
  
  }else{
    colnames(outDat) <- c('forcedFixtime','choicetime')
    outDat = outDat[,1:2] # prune of the unused "grouping" var
  }
  return(outDat)
}