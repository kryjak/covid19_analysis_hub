import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
import plotly.subplots as make_subplots
from datetime import timedelta
from analysis_tools import calculate_epi_correlation

def create_plotly_dual_axis(df1, df2, name1, name2, title, annotation_text):
    fig = make_subplots.make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces with specific colors
    fig.add_trace(
        go.Scatter(
            x=df1["time_value"],
            y=df1["value"],
            name=name1,
            line=dict(color="#1f77b4"),  # Default matplotlib blue
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df2["time_value"],
            y=df2["value"],
            name=name2,
            line=dict(color="#ff7f0e"),  # Default matplotlib orange
        ),
        secondary_y=True,
    )

    # Calculate the range for both y-axes to ensure they start at 0
    y1_max = df1["value"].max()
    y2_max = df2["value"].max()

    # Update layout
    fig.update_layout(
        title=title,
        height=600,  # Fixed height
        hovermode="x unified",
        showlegend=False,  # Remove legend
        yaxis=dict(
            title=name1,
            range=[0, y1_max * 1.1],  # Add 10% padding
            title_font=dict(color="#1f77b4"),  # Match trace color
            tickfont=dict(color="#1f77b4"),
        ),
        yaxis2=dict(
            title=name2,
            range=[0, y2_max * 1.1],  # Add 10% padding
            title_font=dict(color="#ff7f0e"),  # Match trace color
            tickfont=dict(color="#ff7f0e"),
            scaleanchor="y",
            scaleratio=y1_max / y2_max if y2_max != 0 else 1,
        ),
    )

    # Always add the lag annotation
    fig.add_annotation(
        text=annotation_text,
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.99,
        showarrow=False,
        font=dict(color="#1f77b4"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#1f77b4",
        borderwidth=1,
    )

    return fig


def update_plot_with_lag(
    df1, df2, signal_display1, signal_display2, geo_type, region_display, lag, time_type
):
    lag_days = lag if time_type == "day" else lag * 7
    # the shift in the displayed signal1 is opposite to lag_days
    # this is because a lag of dt1=-10 means that signal1 is correlated with the values of signal2 10 days into the future
    # e.g. Covid-19 cases on 1st of June are correlated with deaths on 11th of June
    # to visualise this correlation, we therefore need to shift signal1 in the opposite direction to sign(lag)
    df1_shifted = df1.copy()
    df1_shifted["time_value"] = df1_shifted["time_value"] + timedelta(days=-lag_days)

    title = f"Comparison of {signal_display1} vs {signal_display2} in {geo_type.capitalize()} {region_display}"
    annotation_text = f"Time lag of {signal_display1}: {lag} {time_type}s"

    fig = create_plotly_dual_axis(
        df1_shifted, df2, signal_display1, signal_display2, title, annotation_text
    )

    cor_df = calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=lag_days)
    return fig, cor_df.iloc[0]["cor"].round(3)


def plot_correlation_vs_lag(lags_and_correlations: dict, time_type: str) -> go.Figure:
    """
    Creates a plotly figure showing correlation vs time lag.
    
    Args:
        lags_and_correlations: Dictionary mapping lags to correlation values
        time_type: String indicating the time unit ('day' or 'week')
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(lags_and_correlations.keys()),
        y=list(lags_and_correlations.values()),
        mode='lines',
    ))
    fig.update_layout(
        title=dict(text='Correlation vs Time Lag',
                   x=0.6,
                   xanchor='center'),
        xaxis_title=f'Time Lag ({time_type}s)',
        yaxis_title='Correlation',
        showlegend=False
    )
    return fig


def plot_correlation_distribution(lags_and_correlations: dict) -> go.Figure:
    """
    Creates a plotly figure showing the distribution of correlations using KDE.
    
    Args:
        lags_and_correlations: Dictionary mapping lags to correlation values
    
    Returns:
        Plotly figure object
    """
    kde_values = list(lags_and_correlations.values())
    kde = gaussian_kde(kde_values)
    x_range = np.linspace(min(kde_values), max(kde_values), 100)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_range,
        y=kde(x_range),
        mode='lines',
        fill='tozeroy'
    ))
    fig.update_layout(
        title=dict(text='Distribution of Correlations',
                   x=0.4,
                   xanchor='center'),
        xaxis_title='Correlation',
        yaxis_title='Density',
        yaxis=dict(side='right'),  # Place the y-axis label on the right side
        showlegend=False
    )
    return fig