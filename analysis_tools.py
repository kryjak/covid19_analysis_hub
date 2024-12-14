import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
import streamlit as st


def fetch_covidcast_data(
    geo_type, geo_value, source_and_signal, init_date, final_date, time_type
):
    source, signal = source_and_signal
    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        try:
            df = r.fetch_covidcast_data(
                geo_type=geo_type,
                geo_value=geo_value,
                source=source,
                signal=signal,
                init_date=init_date,
                final_date=final_date,
                time_type=time_type,
            )

        except Exception as e:
            raise e

    # Convert Unix timestamps to datetime
    df["time_value"] = pd.to_datetime(df["time_value"], unit="D").dt.date

    return df


def merge_dataframes(*dfs):
    """
    Merge multiple dataframes containing COVIDcast data.
    
    Args:
        *dfs: Variable number of pandas DataFrames to merge
        
    Returns:
        pandas DataFrame: Merged dataframe with data from all input dataframes
    """
    if len(dfs) < 2:
        result = dfs[0].rename(columns={
            "source": "source0",
            "signal": "signal0",
            "value": "value0"
        })
        return result

    # Verify that geo_type, geo_value, and time_type match across all dataframes
    base_df = dfs[0]
    for key in ["geo_type", "geo_value", "time_type"]:
        base_value = base_df[key].unique()[0]
        if not all(df[key].unique()[0] == base_value for df in dfs[1:]):
            raise ValueError(
                f"{key} must match across all datasets"
            )

    # Start with the first dataframe
    result = dfs[0][[
        "source",
        "signal",
        "geo_type",
        "geo_value",
        "time_type",
        "time_value",
        "value"
    ]].copy()

    # Merge with remaining dataframes
    for i, df in enumerate(dfs[1:], 1):
        result = pd.merge(
            result,
            df[["source", "signal", "time_value", "value"]],
            on="time_value",
            suffixes=(str(i-1) if i > 1 else "", str(i))
        )

    # Rename columns for the first dataframe (which didn't get a suffix)
    result = result.rename(columns={
        "source": "source0",
        "signal": "signal0",
        "value": "value0"
    })

    # Create final column order
    source_signal_columns = []
    value_columns = []
    for i in range(len(dfs)):
        source_signal_columns.extend([f"source{i}", f"signal{i}"])
        value_columns.append(f"value{i}")

    final_columns = (
        source_signal_columns +
        ["geo_type", "geo_value", "time_type", "time_value"] +
        value_columns
    )

    return result[final_columns]


def calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=0, method="pearson"):
    df = merge_dataframes(df1, df2)

    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        corr_df = r.calculate_correlation(df, cor_by, lag, method)

    return corr_df


def get_lags_and_correlations(df1, df2, cor_by="geo_value", max_lag=14, method="pearson"):
    # Merge once at the beginning
    merged_df = merge_dataframes(df1, df2)

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
                corr = r.calculate_correlation(r_df, cor_by, lag, method)
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
