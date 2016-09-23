fd_posteriorpredictive_hdi = function(predDat,columns=c(1,2)){
 #browser() 
  predDat.ci = ddply(predDat,columns,function(a){
    data.frame(quantile=c('low','median','high'),
               sapply(a[,-columns],function(x){
                 quantile(x,c(0.025,0.5,0.975))
               }
               )
    )},.inform=T)
  
  # We reshape it to be usable for plotting
  predDat.ci = reshape2::melt(predDat.ci,
                              measure.vars=c(grep('mean',colnames(predDat.ci)),grep('Q[1-9]',colnames(predDat.ci))))%>%
               reshape2::dcast(.,list(c(colnames(predDat.ci)[columns[-1]],"type","variable"),.(quantile)))
  return(predDat.ci)
}