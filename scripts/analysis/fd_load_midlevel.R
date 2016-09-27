#+ initialize everything ,include = F}
# add paths and library 


#+ load data
# We load the data and all variations (winsor, 3SD, trim, cook)


#+ load stan_fit
mres.complexStandard.3mad = fd_formula_and_lm(data.3mad,gist = cfg$gist)
if (cfg$gist){
  #out = fd_stan_grid_collect(name='2015-12-11_gist_unstandardized')
  out = fd_stan_grid_collect(name='2016-09-27_gist_unstandardized_')
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
normaliseArray = list(angleDiff = 180/1, # original: 1 degree-difference, now: maximal difference
                      trialNum  = 128/1, # original: 1 trial, now: all trials
                      bubbleNum  = 17.5/1, # original: 1 bubble, now: average number of bubbles
                      chosenBubbleY =
                      forcedFixtime =246/1, # original: 1 ms, now: theoretical mean over distribution (300ms) 
                      lag1_forcedFixtime =246/1, # original: 1 ms, now: theoretical mean over distribution (300ms) 
                      lag1_choicetime    =246/1, # original: 1 ms, now: theoretical mean over distribution (300ms) 
                      `log_forcedFixtime:log_NumOfBubbles` = 1,#log(246)*log(5),#,is this correct?
                      log_nextBubbleDist = log(1600), # the parameter estimate now is the maximal possible effekt
                      log_prevBubbleDist = log(1600), # dito
                      log_NumOfBubbles = log(5),# dito
                      log_forcedFixtime = log(246))# dito
hdiDataFrameNorm = hdiDataFrame            
for (k in 1:length(normaliseArray)){
  hdiIDX = grep(paste0('^', names(normaliseArray[k])),hdiDataFrameNorm$Parameter)
  hdiDataFrameNorm[hdiIDX,2:6] =             hdiDataFrameNorm[hdiIDX,2:6]*normaliseArray[[k]]
}

