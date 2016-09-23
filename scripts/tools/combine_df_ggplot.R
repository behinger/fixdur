combine_df_ggplot<- function(..., groupNames = NULL){
                  library('plyr')
                  
                inp = list(...)
                if (length(inp) == 1){
                  inp = unlist(inp,recursive=F)
                }
                
                add_grouping <- function(df,g){
                  gName = 'ggplotGrouping'
                  i = 0
                  if(any(colnames(df)==gName)){
                    gNameOrg = gName
                  }
                  while(any(colnames(df)==gName)){
                    gName = paste0(gNameOrg,i)
                    i+1}
                  
                  df[,gName]=as.factor(rep(g,length(df[,1])))
                  return(df)
                }
                if (is.null(groupNames)){
                 groupNames = 1:length(inp) 
                }
                
                for (dIdx in 1:length(inp)){
                  
                  if (typeof(inp[[dIdx]]) == "logical"){
                   inp[[dIdx]] = data.frame(autoColumn = inp[[dIdx]]) 
                  }
                 inp[[dIdx]] = add_grouping(inp[[dIdx]],groupNames[dIdx] )
                  
                }
                #return(rbind.fill(lapply(inp,function(y){as.data.frame(y,stringsAsFactors=FALSE)})))
                
                return(do.call("rbind.fill",inp))
                
}
