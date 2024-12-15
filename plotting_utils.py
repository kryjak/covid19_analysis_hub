import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
import plotly.subplots as make_subplots
from datetime import datetime, timedelta, date
from analysis_tools import calculate_epi_correlation
from available_signals import sources_to_names
import pandas as pd

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
    df1, df2, signal_display1, signal_display2, geo_type, region_display, lag, time_type, correlation_method
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

    cor_df = calculate_epi_correlation(df1, df2, cor_by="geo_value", lag=lag_days, method=correlation_method)
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

def create_forecast_plot(df_merged, df_merged_as_of, df_forecast, df_forecast_as_of, df_actual, 
                        prediction_date, predicted_source_signal):
    """
    Create an interactive forecast plot using Plotly.
    
    Parameters:
    -----------
    df_merged : pd.DataFrame
        Historical data using latest available estimates
    df_merged_as_of : pd.DataFrame
        Historical data as available at prediction time
    df_forecast : pd.DataFrame
        Predictions using latest available data
    df_forecast_as_of : pd.DataFrame
        Predictions using data available at prediction time
    df_actual : pd.DataFrame
        Actual observed values during the forecast period
    prediction_date : datetime.date
        The date when the prediction was made
    predicted_source_signal : tuple of str
        Source and signal of the predicted quantity
    
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    predicted_name = sources_to_names[predicted_source_signal]
    predicted_col_name = "value_" + "_".join(predicted_source_signal)

    forecast_length = (df_forecast['target_date'].max() - df_forecast['target_date'].min()).days
    # Calculate the historical window (3 times the forecast length)
    historical_length = forecast_length * 3
    if historical_length < 7:
        historical_length = 7
    historical_start = prediction_date - timedelta(days=historical_length)

    # Filter historical data to show only the calculated window
    df_merged_filtered = df_merged[df_merged['time_value'] >= historical_start]
    df_merged_as_of_filtered = df_merged_as_of[df_merged_as_of['time_value'] >= historical_start]

    # Get the last historical values at prediction_date
    last_historical_value = df_merged[df_merged['time_value'] <= prediction_date][predicted_col_name].iloc[-1]
    last_historical_value_as_of = df_merged_as_of[df_merged_as_of['time_value'] <= prediction_date][predicted_col_name].iloc[-1]

    # Add the prediction_date point to the forecast DataFrames
    forecast_start = pd.DataFrame({
        'target_date': [prediction_date],
        '.pred': [last_historical_value],
        '.pred_upper': [last_historical_value],
        '.pred_lower': [last_historical_value]
    })
    forecast_as_of_start = pd.DataFrame({
        'target_date': [prediction_date],
        '.pred': [last_historical_value_as_of],
        '.pred_upper': [last_historical_value_as_of],
        '.pred_lower': [last_historical_value_as_of]
    })

    # Concatenate with the original forecast DataFrames
    df_forecast = pd.concat([forecast_start, df_forecast], ignore_index=True)
    df_forecast_as_of = pd.concat([forecast_as_of_start, df_forecast_as_of], ignore_index=True)

    fig = go.Figure()

    # Historical data (now using filtered data)
    fig.add_trace(
        go.Scatter(
            x=df_merged_filtered['time_value'],
            y=df_merged_filtered[predicted_col_name],
            name='Historical (Latest)',
            line=dict(color='blue'),
            mode='lines',
            hovertemplate='%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_merged_as_of_filtered['time_value'],
            y=df_merged_as_of_filtered[predicted_col_name],
            name='Historical (As of prediction)',
            line=dict(color='lightblue'),
            mode='lines',
            hovertemplate='%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
        )
    )

    # Forecasts
    fig.add_trace(
        go.Scatter(
            x=df_forecast['target_date'],
            y=df_forecast['.pred'],
            name='Forecast (Latest)',
            line=dict(color='blue', dash='dash'),
            mode='lines',
            hovertemplate='%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
        )
    )

    # Confidence intervals for latest forecast
    fig.add_trace(
        go.Scatter(
            x=df_forecast['target_date'].tolist() + df_forecast['target_date'].tolist()[::-1],
            y=df_forecast['.pred_upper'].tolist() + df_forecast['.pred_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0,0,255,0.2)',
            line=dict(color='rgba(0,0,255,0)'),
            name='90% CI (Latest)',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_forecast_as_of['target_date'],
            y=df_forecast_as_of['.pred'],
            name='Forecast (As of prediction)',
            line=dict(color='lightblue', dash='dash'),
            mode='lines',
            hovertemplate='%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
        )
    )

    # Confidence intervals for as-of forecast
    fig.add_trace(
        go.Scatter(
            x=df_forecast_as_of['target_date'].tolist() + df_forecast_as_of['target_date'].tolist()[::-1],
            y=df_forecast_as_of['.pred_upper'].tolist() + df_forecast_as_of['.pred_lower'].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(173,216,230,0.2)',
            line=dict(color='rgba(173,216,230,0)'),
            name='90% CI (As of prediction)',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            mode='lines'
        )
    )

    # Actual values
    fig.add_trace(
        go.Scatter(
            x=df_actual['time_value'],
            y=df_actual['value'],
            name='Actual values',
            line=dict(color='green'),
            mode='lines',
            hovertemplate='%{y:.2f}<br>%{x|%Y-%m-%d}<extra></extra>'
        )
    )

    # Convert prediction_date to datetime if it's a date object
    if isinstance(prediction_date, date):
        prediction_date = datetime.combine(prediction_date, datetime.min.time())

    # Add vertical line at prediction date
    fig.add_shape(
        type='line',
        x0=prediction_date,
        x1=prediction_date,
        y0=0,
        y1=1,
        yref='paper',
        line=dict(
            color='gray',
        )
    )

    # Add annotation for the prediction date
    fig.add_annotation(
        x=prediction_date,
        y=1,
        yref='paper',
        text="Prediction date",
        showarrow=False,
        yshift=10
    )

    # Update layout
    fig.update_layout(
        title=f"Forecast for {predicted_name}",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    return fig