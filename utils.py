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


def get_shared_geotypes(metadata, *source_and_signals):
    """
    Get geo_types shared across multiple signals.
    
    Args:
        metadata: COVIDcast metadata DataFrame
        *source_and_signals: Variable number of (source, signal) tuples
    """
    if len(source_and_signals) < 2:
        raise ValueError("At least two source-signal pairs are required")
        
    # Get geo_types for each source-signal pair
    all_geo_types = [
        set(get_signal_geotypes(metadata, source_signal))
        for source_signal in source_and_signals
    ]
    
    # Find intersection of all sets
    return list(set.intersection(*all_geo_types))


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


def get_shared_dates(metadata, geo_type, *source_and_signals):
    """
    Get overlapping date range and verify time_type matches across signals.
    
    Args:
        metadata: COVIDcast metadata DataFrame
        geo_type: Geographic type to check
        *source_and_signals: Variable number of (source, signal) tuples
    """
    # Get dates and time_types for all signals
    date_ranges = [
        get_signal_dates(metadata, source_signal, geo_type, return_time_type=True)
        for source_signal in source_and_signals
    ]

    if len(date_ranges) == 1:
        return date_ranges[0]

    # Verify all time_types match
    time_types = [dates[2] for dates in date_ranges]
    if not all(tt == time_types[0] for tt in time_types):
        raise ValueError("All signals must have the same time_type")
    
    # Find overlapping date range
    init_date = max(dates[0] for dates in date_ranges)
    final_date = min(dates[1] for dates in date_ranges)
    
    return init_date, final_date, time_types[0]


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
