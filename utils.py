import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from available_signals import names_to_sources
from datetime import date
from epiweeks import Week

covidcast_metadata = pd.read_csv("covidcast_metadata.csv")


def load_data(source, signal):
    df = pd.read_csv(f"{source}_{signal}.csv")
    return df


def get_signal_geotypes(metadata, displayed_name):
    source, signal = names_to_sources[displayed_name]
    df = metadata[metadata["data_source"] == source]
    df = df[df["signal"] == signal]

    geo_types = list(df["geo_type"])

    return geo_types


def get_shared_geotypes(metadata, displayed_name1, displayed_name2):
    geo_types1 = get_signal_geotypes(metadata, displayed_name1)
    geo_types2 = get_signal_geotypes(metadata, displayed_name2)

    return list(set(geo_types1) & set(geo_types2))


def get_signal_dates(metadata, displayed_name, geo_type, return_time_type=False):
    source, signal = names_to_sources[displayed_name]
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


def get_shared_dates(metadata, displayed_name1, displayed_name2, geo_type):
    init_date1, final_date1, time_type1 = get_signal_dates(
        metadata, displayed_name1, geo_type, return_time_type=True
    )
    init_date2, final_date2, time_type2 = get_signal_dates(
        metadata, displayed_name2, geo_type, return_time_type=True
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


def create_dual_axis_plot(df1, df2, signal_display1, signal_display2):
    """
    Create a dual-axis plot with two y-axes based on the DataFrames from two signals.
    Args:
        df1: DataFrame with the first signal
        df2: DataFrame with the second signal
        signal_display1: Displayed name of the first signal
        signal_display2: Displayed name of the second signal
    Returns:
        fig: The figure object containing the plot

    Notes:
        - The x-axis is formatted based on the date range of the data.
        - Converts Unix timestamps to pandas datetime objects
        - For ranges ≤ 90 days: Show individual days with weekly intervals
        - For ranges ≤ 1 year: Show monthly intervals
        - For ranges > 1 year: Show quarterly intervals
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot first signal on primary y-axis
    color1 = "#1f77b4"  # Blue
    ax1.set_xlabel("Date", fontsize=14)
    ax1.set_ylabel(signal_display1, color=color1, fontsize=14)
    line1 = ax1.plot(
        df1["time_value"], df1["value"], color=color1, label=signal_display1
    )
    ax1.tick_params(axis="y", labelcolor=color1)

    # Create secondary y-axis and plot second signal
    ax2 = ax1.twinx()
    color2 = "#ff7f0e"  # Orange
    ax2.set_ylabel(signal_display2, color=color2, fontsize=14)
    line2 = ax2.plot(
        df2["time_value"], df2["value"], color=color2, label=signal_display2
    )
    ax2.tick_params(axis="y", labelcolor=color2)

    # Combine legends
    lines = line1 + line2
    labels = [line.get_label() for line in lines]
    ax1.legend(lines, labels, loc="upper left")

    # Format x-axis based on date range
    date_range = (df1["time_value"].max() - df1["time_value"].min()).days
    if date_range <= 90:  # For ranges up to 3 months
        ax1.xaxis.set_major_locator(
            mdates.DayLocator(interval=7)
        )  # Show weekly intervals
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    elif date_range <= 365:  # For ranges up to 1 year
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    else:  # For ranges over 1 year
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Quarterly
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    # Rotate and align the tick labels so they look better
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    return fig
