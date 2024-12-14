library(epidatr)
library(epiprocess)
library(dplyr)  # Add this line

fetch_covidcast_data <- function(
  geo_type, geo_value, source, signal,
  init_date, final_date, time_type, as_of = NULL
) {
  response <- pub_covidcast(
    source = source,
    signal = signal,
    geo_type = geo_type,
    geo_value = geo_value,
    time_type = time_type,
    time_values = epirange(init_date, final_date),
    as_of = as_of
  )

  return(response)
}

calculate_correlation <- function(df, value1_name, value2_name, cor_by="geo_value", lag=0, method="pearson") {
  df <- as_epi_df(df)
  cor_value <- epi_cor(df,
                    !!sym(value1_name),
                    !!sym(value2_name),
                    cor_by = cor_by,
                    dt1 = lag,
                    method = method)

  return(cor_value)
}
