
fd_load_midlevel = function(data.3mad,cfg){
  #+ load stan_fit
  mres.complexStandard.3mad = fd_formula_and_lm(data.3mad,gist = cfg$gist)
  if (cfg$gist){
    #out = fd_stan_grid_collect(name='2015-12-11_gist_unstandardized')
    out = fd_stan_grid_collect(name='2016-09-27_gist_unstandardized')
  }else{
    #out = fd_stan_grid_collect(name='2015-12-11_unstandardized')
    out = fd_stan_grid_collect(name='2016-09-27_unstandardized_')
  }
  stanfit = out$fit
  modelMatrix = out$modelMatrix
  label_dataframe = out$label_dataframe
  
  
  #+ load STAN
  S_custom = fd_stan_to_ggmcmc(stanfit,label_dataframe)
  
  # Input is a ggmcmc-object and a LME4 object
  
  if (cfg$gist){
    gistidx = grep('gist',S_custom$Parameter);
    
    nogistidx = seq(1,length(S_custom$Parameter))
    nogistidx = nogistidx[!(nogistidx %in% gistidx)]
    
    intercept = which(S_custom$Parameter == '(Intercept)')
    nogistidx = nogistidx[!(nogistidx%in%intercept)]
    
    
    mainGist = which(S_custom$Parameter == 'gist')
    gistidx = gistidx[!(gistidx%in%mainGist)]
    
    assertthat::are_equal(length(gistidx),length(nogistidx))
    
    S_custom$value[gistidx] = S_custom$value[gistidx]+S_custom$value[nogistidx]
    
  }
  
  
  hdiDataFrame = ggmcmc::ci(subset(S_custom,S_custom$Parameter!="(Intercept)"))
  colnames(hdiDataFrame)[4] = 'Estimate'
  
  #with what value should the parameter be multiplied for display purposes?
  normaliseArray = list(angleDiff = c(180/1, '180~`°`~max'),## original: 1 degree-difference, now: maximal difference'
                        trialNum  = c(128/1,'128~max'), # original: 1 trial, now: all trials
                        bubbleNum  = c(17.5/1,'17.5~avg'), # original: 1 bubble, now: average number of bubbles
                        chosenBubbleX =c(12.65,'12.7~`°`~max'), #px2deg(1280/2)
                        chosenBubbleY =c(9.49,'9.5~`°`~max'), #px2deg(960/2)
                        sq_chosenBubbleX =c(12.65^2,'12.7^2~max'), #px2deg(1280/2)
                        sq_chosenBubbleY =c(9.49^2,'9.5^2~max'), #px2deg(960/2)
                        forcedFixtime =c(246/1,'246~ms~avg'), # original: 1 ms, now: theoretical mean over distribution (300ms) 
                        lag1_forcedFixtime =c(246/1,'246~ms~avg'), # original: 1 ms, now: theoretical mean over distribution (300ms) 
                        lag1_choicetime    =c(246/1,'246~ms~avg'), # original: 1 ms, now: theoretical mean over distribution (300ms) 
                        `log_forcedFixtime:log_NumOfBubbles` = c(log(246)*log(5),'c.f.~FF/NoB'),#,is this correct?
                        log_nextBubbleDist = c(log(20),'20~`°`~max'), # the parameter estimate now is the maximal possible effekt
                        log_prevBubbleDist = c(log(20),'20~`°`~max'), # dito
                        centerDistance = c(6.5,'6.5~`°`~max'), # average centerDistance
                        log_NumOfBubbles = c(log(5),'5~max'),# dito
                        log_forcedFixtime = c(log(246),'246~ms~avg'))# dito
  hdiDataFrameNorm = hdiDataFrame            
  hdiDataFrameNormLabels = {}
  for (k in 1:length(normaliseArray)){
    
    if (names(normaliseArray[k]) == 'log_forcedFixtime'){
      hdiIDX = which(hdiDataFrameNorm$Parameter %in% c('log_forcedFixtime:gist','log_forcedFixtime'))
    } else{
    hdiIDX = grep(paste0('^', names(normaliseArray[k])),hdiDataFrameNorm$Parameter)
    }
    hdiDataFrameNorm[hdiIDX,2:6] =             hdiDataFrameNorm[hdiIDX,2:6]*as.numeric(normaliseArray[[k]][1])
    hdiDataFrameNormLabels[hdiIDX] = paste0(normaliseArray[[k]][2])
  }
  #hdiDataFrameNormLabels[is.na(hdiDataFrameNormLabels)] = ' '
  
  return(c(out,hdiDataFrame = list(hdiDataFrame),hdiDataFrameNorm = list(hdiDataFrameNorm),hdiDataFrameNormLabels=list(hdiDataFrameNormLabels),S_custom = list(S_custom),mres.complexStandard.3mad = mres.complexStandard.3mad))
}