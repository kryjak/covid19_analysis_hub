import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter


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


def calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=0):
    df = merge_dataframes(df1, df2)

    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        corr_df = r.calculate_correlation(df, cor_by, lag)

    return corr_df

def get_lags_and_correlations(df1, df2, cor_by="geo_value", max_lag=14):
    lags_and_correlations = {}

    for lag in range(-max_lag, max_lag + 1):
        corr_df = calculate_epi_correlation(df1, df2, cor_by, lag)
        lags_and_correlations[lag] = corr_df.iloc[0]["cor"]

    return lags_and_correlations