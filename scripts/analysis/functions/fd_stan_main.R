fd_stan_main <- function(mres,name,nchains=6,niter=500,rerun=F,is_on_grid=F){
  if(is_on_grid){
    rerun=T
    nchains=1
    name = paste0(name, 'grid_',paste0(sample(c(0:9, letters, LETTERS),10,replace=TRUE),collapse=''))
  }
  name = paste0(name,'.RData')
  library(rstan)
  dir = 'cache/stanfit/'
  dir.create(file.path(dir), showWarnings = F)
  if (file.exists(file.path(dir,name)) & !rerun){
    load(file.path(dir,name))
    # and then go all the way down to the return statement ;)
  }else{
    modelMatrix = model.matrix(mres)
    betaNames = colnames(modelMatrix)
    X <- unname(modelMatrix)
    attr(X,"assign") <- NULL
    
    label_dataframe = data.frame(Parameter=sprintf('beta.%i.',1:length(betaNames)),Label=betaNames)
    
  
    stanDat <- within(list(),
                      {
                        N<-nrow(X)
                        P <- n_u <- n_w <- ncol(X)
                        X <- Z_u <- Z_w <- X
                        
                        J <- length(levels(as.factor(mres@frame$subject)))
                        answer <- mres@frame$choicetime   # We don't want to standardized rating!
                        subj <- as.integer(as.factor(mres@frame$subject))
                      }
    )
    # 5. Fit the model.
    fd_model = stan_model(file='scripts/analysis/stan/fd_model_1.stan')
  #   init.f = function(chain_id){
  #     numP = 20
  #     list(beta=c(200,rep(0,numP-1))+rnorm(numP,0,1))
  #   }
    fit <- sampling(fd_model,data=stanDat,iter=niter, chains=nchains,cores = nchains,refresh=1,init=0)#,init=init.f)
    save(modelMatrix,fit,label_dataframe,file= file.path(dir,name))
  }
  return(list(fit=fit,label_dataframe=label_dataframe,modelMatrix=modelMatrix))
}