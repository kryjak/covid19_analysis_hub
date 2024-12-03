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

  return(response)
}

calculate_correlation <- function(df, cor_by="geo_value", lag=0) {
  df <- as_epi_df(df)
  cor_value <- epi_cor(df,
                    value1,
                    value2,
                    cor_by = cor_by,
                    dt1 = lag)

  return(cor_value)

}
