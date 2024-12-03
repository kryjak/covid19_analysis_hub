import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from available_signals import names_to_sources
from datetime import date, timedelta
from epiweeks import Week
import plotly.subplots as make_subplots
import plotly.graph_objects as go
from analysis_tools import calculate_epi_correlation

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


def create_plotly_dual_axis(df1, df2, name1, name2, title, annotation_text):
    fig = make_subplots.make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces with specific colors
    fig.add_trace(
        go.Scatter(
            x=df1['time_value'], 
            y=df1['value'], 
            name=name1,
            line=dict(color='#1f77b4')  # Default matplotlib blue
        ),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(
            x=df2['time_value'], 
            y=df2['value'], 
            name=name2,
            line=dict(color='#ff7f0e')  # Default matplotlib orange
        ),
        secondary_y=True,
    )
    
    # Calculate the range for both y-axes to ensure they start at 0
    y1_max = df1['value'].max()
    y2_max = df2['value'].max()
    
    # Update layout
    fig.update_layout(
        title=title,
        height=600,  # Fixed height
        hovermode='x unified',
        showlegend=False,  # Remove legend
        yaxis=dict(
            title=name1,
            range=[0, y1_max * 1.1],  # Add 10% padding
            title_font=dict(color='#1f77b4'),  # Match trace color
            tickfont=dict(color='#1f77b4')
        ),
        yaxis2=dict(
            title=name2,
            range=[0, y2_max * 1.1],  # Add 10% padding
            title_font=dict(color='#ff7f0e'),  # Match trace color
            tickfont=dict(color='#ff7f0e'),
            scaleanchor="y",
            scaleratio=y1_max/y2_max if y2_max != 0 else 1
        )
    )
    
    # Always add the lag annotation
    fig.add_annotation(
        text=annotation_text,
        xref="paper", yref="paper",
        x=0.01, y=0.99,
        showarrow=False,
        font=dict(color='#1f77b4'),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor='#1f77b4',
        borderwidth=1
    )
    
    return fig

def update_plot_with_lag(df1, df2, signal_display1, signal_display2, geo_type, region_display, lag, time_type):
    lag_days = lag if time_type == "day" else lag * 7
    # the shift in the displayed signal1 is opposite to lag_days
    # this is because a lag of dt1=-10 means that signal1 is correlated with the values of signal2 10 days into the future
    # e.g. Covid-19 cases on 1st of June are correlated with deaths on 11th of June
    # to visualise this correlation, we therefore need to shift signal1 in the opposite direction to sign(lag)
    df1_shifted = df1.copy()
    df1_shifted['time_value'] = df1_shifted['time_value'] + timedelta(days=-lag_days)
    
    title = f"Comparison of {signal_display1} vs {signal_display2} in {geo_type.capitalize()} {region_display}"
    annotation_text = f"Time lag of {signal_display1}: {lag} {time_type}s"

    fig = create_plotly_dual_axis(
        df1_shifted, 
        df2, 
        signal_display1,
        signal_display2,
        title,
        annotation_text
    )
    
    cor_df = calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=lag_days)
    return fig, cor_df.iloc[0]["cor"].round(3)
