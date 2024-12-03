library(epidatr)
library(epiprocess)
library(dplyr)  # Add this line

fetch_covidcast_data <- function(
  geo_type, geo_value, source, signal,
  init_date, final_date, time_type
) {
  response <- pub_covidcast(
    source = source,
    signal = signal,
    geo_type = geo_type,
    geo_value = geo_value,
    time_type = time_type,
    time_values = epirange(init_date, final_date)
  )

  # Convert response to dataframe
#   df <- as.data.frame(response) %>%
#     select(geo_value, time_value, value) %>%
#     mutate(time_value = as.Date(as.numeric(time_value), origin = "1970-01-01"))

  return(response)
}

calculate_correlation <- function(epi_df1, epi_df2, cor_by) {
  epi_cor(epi_df1, epi_df2, cor_by = cor_by)
}