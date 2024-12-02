library(epidatr)

metadata <- pub_covidcast_meta()
write.csv(metadata, "covidcast_metadata.csv", row.names = FALSE)
