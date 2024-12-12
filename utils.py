import pandas as pd
from datetime import date
from epiweeks import Week

covidcast_metadata = pd.read_csv("csv_data/covidcast_metadata.csv")


def load_data(source, signal):
    df = pd.read_csv(f"{source}_{signal}.csv")
    return df


def get_signal_geotypes(metadata, source_and_signal):
    source, signal = source_and_signal
    df = metadata[metadata["data_source"] == source]
    df = df[df["signal"] == signal]

    geo_types = list(df["geo_type"])

    return geo_types


def get_shared_geotypes(metadata, source_and_signal1, source_and_signal2):
    geo_types1 = get_signal_geotypes(metadata, source_and_signal1)
    geo_types2 = get_signal_geotypes(metadata, source_and_signal2)

    return list(set(geo_types1) & set(geo_types2))


def get_signal_dates(metadata, source_and_signal, geo_type, return_time_type=False):
    source, signal = source_and_signal
    df = metadata[metadata["data_source"] == source]
    df = df[df["signal"] == signal]
    df = df[df["geo_type"] == geo_type]

    init_date = pd.to_datetime(df["min_time"]).item().date()
    final_date = pd.to_datetime(df["max_time"]).item().date()

    if not return_time_type:
        return init_date, final_date

    try:
        time_type = df["time_type"].item()
    except Exception as e:
        print(
            "Currently, the code assumes that each signal has only one reporting frequency ('time_type')."
        )
        raise e

    return init_date, final_date, time_type


def get_shared_dates(metadata, source_and_signal1, source_and_signal2, geo_type):
    init_date1, final_date1, time_type1 = get_signal_dates(
        metadata, source_and_signal1, geo_type, return_time_type=True
    )
    init_date2, final_date2, time_type2 = get_signal_dates(
        metadata, source_and_signal2, geo_type, return_time_type=True
    )

    if time_type1 != time_type2:
        raise ValueError

    return max(init_date1, init_date2), min(final_date1, final_date2), time_type1


def to_epidate_range(dt1: date, dt2: date) -> tuple[int, int]:
    return int(dt1.strftime("%Y%m%d")), int(dt2.strftime("%Y%m%d"))


def to_epiweek_range(dt1: date, dt2: date) -> tuple[int, int]:
    start_week = Week.fromdate(dt1)
    end_week = Week.fromdate(dt2)
    start_year = start_week.year
    end_year = end_week.year
    return int(str(start_year) + str(start_week.week)), int(
        str(end_year) + str(end_week.week)
    )
