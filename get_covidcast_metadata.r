library(epidatr)

metadata <- pub_covidcast_meta()
write.csv(metadata, "csv_data/covidcast_metadata.csv", row.names = FALSE)
