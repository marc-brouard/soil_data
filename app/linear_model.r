soil_model <- function(df){
    model <- lm(cbind(clay, sand, silt) ~ ocs, data = df)
    return(summary(model))
}