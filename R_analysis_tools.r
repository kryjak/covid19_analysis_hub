library(epidatr)
library(epiprocess)
library(epipredict)
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

epi_predict <- function(df, predictor_col_names, predicted_col_names, forecaster_type, prediction_length) {
  # df$time_value <- as.Date(df$time_value) # this line is crucial to ensure dates get passed
  df <- as_epi_df(df)
  predictors <- unlist(predictor_col_names)

  if (forecaster_type == "arx_forecaster") {
    forecast <- arx_forecaster(df,
                    outcome = predicted_col_names,
                    predictors = predictors,
                    trainer = linear_reg(),
                    arx_args_list(ahead = 1))
  } else if (forecaster_type == "arx_classifier") {
    forecast <- arx_classifier(df,
                    outcome = predicted_col_names,
                    predictors = predictors,
                    trainer = logistic_reg(),
                    arx_class_args_list(ahead = 1))
  } else if (forecaster_type == "flatline_forecaster") {
    forecast <- flatline_forecaster(df,
                    outcome = predicted_col_names,
                    flatline_args_list(ahead = 1))
  } else if (forecaster_type == "cdc_baseline_forecaster") {
    forecast <- cdc_baseline_forecaster(df,
                    outcome = predicted_col_names,
                    cdc_baseline_args_list(aheads = 1:prediction_length))
  } else {
    stop("Invalid forecaster type")
  }

  forecast_df <- forecast$predictions %>%
    mutate(
      .pred_lower = sapply(.pred_distn, function(x) quantile(x, 0.05)),
      .pred_upper = sapply(.pred_distn, function(x) quantile(x, 0.95)),
    ) %>%
    select(-`.pred_distn`)

  return(forecast_df)
}
