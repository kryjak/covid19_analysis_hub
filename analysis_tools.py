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
    df["time_value"] = pd.to_datetime(df["time_value"], unit="D")

    return df


def calculate_epi_correlation(df1, df2, cor_by="time_value"):
    # Convert pandas DataFrames back to R objects
    with conversion.localconverter(default_converter + pandas2ri.converter):
        r.source("R_analysis_tools.r")

        # r_df = conversion.py2rpy(df1)

        # TODO: Calculate correlation
        pass
