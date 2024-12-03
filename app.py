import streamlit as st
import pandas as pd
from available_signals import names_to_sources
from geo_codes import (
    geotypes_to_display,
    display_to_geotypes,
    nation_to_display,
    display_to_nation,
    state_abbrvs_to_display,
    display_to_state_abbrvs,
    county_by_state,
    display_to_county_fips,
    display_to_hrr,
    hrr_by_state,
    hss_region_to_display,
    display_to_hss_region,
    msa_by_state,
    display_to_msa,
)
from utils import (
    get_shared_geotypes,
    get_shared_dates,
    to_epidate_range,
    to_epiweek_range,
    create_dual_axis_plot,
)
from analysis_tools import fetch_covidcast_data, calculate_epi_correlation
from datetime import timedelta
import plotly.subplots as make_subplots
import plotly.graph_objects as go


covidcast_metadata = pd.read_csv("covidcast_metadata.csv")

st.title("COVID-19 Signal Correlation and Forecast Analysis")
st.write("This app allows you to explore the correlation between two COVID-19 signals.")

signals_display = list(names_to_sources.keys())

col1, col2 = st.columns(2)
with col1:
    signal_display1 = st.selectbox("Choose signal 1:", signals_display)
    source1, signal1 = names_to_sources[signal_display1]
with col2:
    signal_display2 = st.selectbox(
        "Choose signal 2:",
        [signal for signal in signals_display if signal != signal_display1],
    )
    source2, signal2 = names_to_sources[signal_display2]

shared_geo_types = get_shared_geotypes(
    covidcast_metadata, signal_display1, signal_display2
)
shared_geo_types_display = [
    geotypes_to_display[geo_type] for geo_type in shared_geo_types
]

col1, col2 = st.columns(2)
with col1:
    geo_type_display = st.selectbox("Browse by:", shared_geo_types_display)
    geo_type = display_to_geotypes[geo_type_display]
with col2:
    if geo_type == "nation":
        region_display = st.selectbox("Choose a nation:", nation_to_display.values())
        region = display_to_nation[region_display]
    elif geo_type == "state":
        region_display = st.selectbox(
            "Choose a state:", state_abbrvs_to_display.values()
        )
        region = display_to_state_abbrvs[region_display]
    elif geo_type == "county":
        state_display = st.selectbox(
            "Choose a state:", state_abbrvs_to_display.values()
        )
        region_display = st.selectbox(
            "Choose a county:", county_by_state[state_display]
        )
        region = display_to_county_fips[region_display]
    elif geo_type == "hrr":
        state_display = st.selectbox(
            "Choose a state:", state_abbrvs_to_display.values()
        )
        region_display = st.selectbox(
            "Choose an Hospital Referral Region:", hrr_by_state[state_display]
        )
        region = display_to_hrr[region_display]
    elif geo_type == "hhs":
        region_display = st.selectbox(
            "Choose an HHS Region:", hss_region_to_display.values()
        )
        region = display_to_hss_region[region_display]
    elif geo_type == "msa":
        state_display = st.selectbox(
            "Choose a state:", state_abbrvs_to_display.values()
        )
        region_display = st.selectbox(
            "Choose a Metropolitan Statistical Area:", msa_by_state[state_display]
        )
        region = display_to_msa[region_display]
    elif geo_type == "dma":
        st.error(
            "Designated Market Areas (DMAs) are proprietary information released by Nielsen. The subscription to this data costs $8000. Sorry.",
            icon="🚨",
        )
    else:
        st.error(f"Invalid geo_type: {geo_type}", icon="🚨")
        st.stop()

try:
    shared_init_date, shared_final_date, time_type = get_shared_dates(
        covidcast_metadata, signal_display1, signal_display2, geo_type
    )
except ValueError:
    st.error(
        "Signals must have the same reporting frequency ('time_type') to be compared. Try changing the signal or at least one of the regions.",
        icon="🚨",
    )
    st.stop()

init_date, final_date = st.slider(
    "Date range:",
    min_value=shared_init_date,
    max_value=shared_final_date,
    value=(shared_init_date, shared_final_date),
)

if time_type == "day":
    date_range = to_epidate_range(init_date, final_date)
    max_lag = (final_date - init_date).days // 2
elif time_type == "week":
    date_range = to_epiweek_range(init_date, final_date)
    max_lag = ((final_date - init_date).days // 7) // 2
else:
    st.error(f"Invalid time_type: {time_type}", icon="🚨")
    st.stop()

button_enabled = signal1 != signal2 and geo_type != "dma" and "region" in locals()

if st.button(
    "Fetch Data",
    type="primary",
    disabled=not button_enabled,
    help="Click to fetch and analyze the selected signals",
):
    st.divider()
    with st.spinner("Fetching data..."):
        # Store the fetched data in session state
        st.session_state.df1 = fetch_covidcast_data(
            geo_type, region, source1, signal1, date_range[0], date_range[-1], time_type
        )
        st.session_state.df2 = fetch_covidcast_data(
            geo_type, region, source2, signal2, date_range[0], date_range[-1], time_type
        )

st.divider()

# Only show the lag slider and plot if we have data
if 'df1' in st.session_state and 'df2' in st.session_state:
    plot_container = st.empty()
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        selected_lag = st.slider(
            f"Time lag ({time_type}s)",
            min_value=-max_lag,
            max_value=max_lag,
            value=0,  # Always start at 0
            help=f"Shift signal 1 ({signal_display1}) forwards or backwards in time"
        )
    
    with col2:
        if st.button("Reset to 0"):
            selected_lag = 0
            st.rerun()
    
    def create_plotly_dual_axis(df1, df2, name1, name2):
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
        
        # Update layout
        fig.update_layout(
            title=f"Comparison of {signal_display1} vs {signal_display2} in {geo_type.capitalize()} {region_display}",
            height=600,  # Fixed height
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            yaxis=dict(title=signal_display1),  # Add left y-axis title
            yaxis2=dict(title=signal_display2)  # Add right y-axis title
        )

        # Set both y-axes to start at 0 with matching grid
        fig.update_yaxes(rangemode="tozero", secondary_y=False, zeroline=True, zerolinewidth=2)
        fig.update_yaxes(rangemode="tozero", secondary_y=True, zeroline=True, zerolinewidth=2)
        
        return fig
    
    def update_plot(lag):
        shift_days = lag if time_type == "day" else lag * 7
        df1_shifted = st.session_state.df1.copy()
        df1_shifted['time_value'] = df1_shifted['time_value'] + timedelta(days=shift_days)
        
        fig = create_plotly_dual_axis(
            df1_shifted, 
            st.session_state.df2, 
            f"{signal_display1} (lag: {lag} {time_type}s)", 
            signal_display2
        )
        
        cor_df = calculate_epi_correlation(df1_shifted, st.session_state.df2, cor_by="geo_value")
        return fig, cor_df.iloc[0]["cor"].round(3)
    
    # Update plot based on current lag
    new_fig, new_correlation = update_plot(selected_lag)
    
    with plot_container:
        st.plotly_chart(new_fig, use_container_width=True)
    
    st.write(f'Signal correlation at lag {selected_lag} {time_type}s: **{new_correlation}**')

st.divider()
