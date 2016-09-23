naModelFillin = function(mres,dataToBeFilledIn){
  naRemoved = as.numeric((attr(mres@frame,'na.action')))
  tmp <- numeric(length(dataToBeFilledIn)+length(naRemoved))
  tmp[naRemoved] = NA
  tmp[!is.na(tmp)] = dataToBeFilledIn
  return(tmp)
}