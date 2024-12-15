import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
from rpy2.robjects import NULL
from datetime import date
import streamlit as st


def fetch_covidcast_data(
    geo_type, geo_value, source_and_signal, init_date, final_date, time_type, as_of=None
):
    source, signal = source_and_signal
    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        r_as_of = NULL if as_of is None else as_of

        try:
            df = r.fetch_covidcast_data(
                geo_type=geo_type,
                geo_value=geo_value,
                source=source,
                signal=signal,
                init_date=init_date,
                final_date=final_date,
                time_type=time_type,
                as_of=r_as_of
            )

        except Exception as e:
            raise e

    # Convert Unix timestamps to datetime
    df["time_value"] = pd.to_datetime(df["time_value"], unit="D").dt.date

    return df

def fetch_covidcast_data_multi(geo_type, geo_value, source_and_signal, init_date, final_date, time_type, as_of=None):
    dataframes = []
    for source_and_signal in source_and_signal:
        df = fetch_covidcast_data(
            geo_type, geo_value, source_and_signal, init_date, final_date, time_type, as_of=None
        )
        dataframes.append(df)

    return merge_dataframes(*dataframes)

def merge_dataframes(*dfs):
    """
    Merge multiple dataframes containing COVIDcast data.
    
    Args:
        *dfs: Variable number of pandas DataFrames to merge
        
    Returns:
        pandas DataFrame: Merged dataframe with data from all input dataframes
    """

    # Verify that geo_type, geo_value, and time_type match across all dataframes
    base_df = dfs[0]
    for key in ["geo_type", "geo_value", "time_type"]:
        base_value = base_df[key].unique()[0]
        if not all(df[key].unique()[0] == base_value for df in dfs[1:]):
            raise ValueError(
                f"{key} must match across all datasets"
            )

    # Start with the first dataframe
    first_df = dfs[0]
    result = first_df[[
        "geo_type",
        "geo_value",
        "time_type",
        "time_value",
        "value"
    ]].copy()
    
    # Rename the value column for the first dataframe
    first_source = first_df["source"].iloc[0]
    first_signal = first_df["signal"].iloc[0]
    result = result.rename(columns={
        "value": f"value_{first_source}_{first_signal}"
    })

    # Merge with remaining dataframes
    for df in dfs[1:]:
        source = df["source"].iloc[0]
        signal = df["signal"].iloc[0]
        value_col_name = f"value_{source}_{signal}"
        
        temp_df = df[["time_value", "value"]].copy()
        temp_df = temp_df.rename(columns={"value": value_col_name})
        
        result = pd.merge(
            result,
            temp_df,
            on="time_value"
        )

    # Create final column order
    value_columns = [f"value_{df['source'].iloc[0]}_{df['signal'].iloc[0]}" for df in dfs]
    final_columns = (
        ["geo_type", "geo_value", "time_type", "time_value"] +
        value_columns
    )

    return result[final_columns]


def calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=0, method="pearson"):
    df = merge_dataframes(df1, df2)
    
    # Extract column names based on source and signal from original dataframes
    value1_name = f"value_{df1['source'].iloc[0]}_{df1['signal'].iloc[0]}"
    value2_name = f"value_{df2['source'].iloc[0]}_{df2['signal'].iloc[0]}"

    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        corr_df = r.calculate_correlation(
            df, 
            value1_name=value1_name,
            value2_name=value2_name,
            cor_by=cor_by, 
            lag=lag, 
            method=method,
        )

    return corr_df


def get_lags_and_correlations(df1, df2, cor_by="geo_value", max_lag=14, method="pearson"):
    # Merge once at the beginning
    merged_df = merge_dataframes(df1, df2)

    value1_name = f"value_{df1['source'].iloc[0]}_{df1['signal'].iloc[0]}"
    value2_name = f"value_{df2['source'].iloc[0]}_{df2['signal'].iloc[0]}"

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Calculating correlations...")
        # Calculate correlations with progress updates
        lags_and_correlations = {}
        total_lags = 2 * max_lag + 1
        
        with conversion.localconverter(default_converter + pandas2ri.converter):
            r_df = pandas2ri.py2rpy(merged_df)
            r.source("R_analysis_tools.r")
            
            for i, lag in enumerate(range(-max_lag, max_lag + 1)):
                corr = r.calculate_correlation(
                    r_df, 
                    value1_name, 
                    value2_name, 
                    cor_by, 
                    lag, 
                    method
                )
                lags_and_correlations[lag] = corr.iloc[0]["cor"]
                
                # Update progress
                progress = (i + 1) / total_lags
                progress_bar.progress(progress)
                status_text.text(f"Calculating correlations... ({i + 1}/{total_lags})")

        return lags_and_correlations
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()

def epi_predict(df, predictors, predicted, forecaster_type, prediction_length):
    predictor_col_names = [f"value_{source}_{signal}" for source, signal in predictors]
    source, signal = predicted
    predicted_col_names = f"value_{source}_{signal}"

    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")
        forecast = r.epi_predict(df, predictor_col_names, predicted_col_names, forecaster_type, prediction_length)

        forecast['target_date'] = forecast['target_date'].apply(lambda x: date.fromordinal(x))
        forecast['forecast_date'] = forecast['forecast_date'].apply(lambda x: date.fromordinal(x))
        
    return forecast