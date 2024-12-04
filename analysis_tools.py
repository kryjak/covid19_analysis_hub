import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
import streamlit as st


def fetch_covidcast_data(
    geo_type, geo_value, source, signal, init_date, final_date, time_type
):
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


def merge_dataframes(df1, df2):
    # Verify that geo_type, geo_value, and time_type match
    if not all(
        df1[key].unique()[0] == df2[key].unique()[0]
        for key in ["geo_type", "geo_value", "time_type"]
    ):
        raise ValueError(
            "geo_type, geo_value and time_type must match between datasets"
        )

    # Create merged dataframe with selected columns
    merged_df = pd.merge(
        df1[
            [
                "source",
                "signal",
                "geo_type",
                "geo_value",
                "time_type",
                "time_value",
                "value",
            ]
        ],
        df2[["source", "signal", "time_value", "value"]],
        on="time_value",
        suffixes=("1", "2"),
    )

    # Reorder columns as specified
    final_columns = [
        "source1",
        "signal1",
        "source2",
        "signal2",
        "geo_type",
        "geo_value",
        "time_type",
        "time_value",
        "value1",
        "value2",
    ]

    return merged_df[final_columns]


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
