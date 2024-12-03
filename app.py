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
elif time_type == "week":
    date_range = to_epiweek_range(init_date, final_date)
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
        # Load the R script containing your function
        df1 = fetch_covidcast_data(
            geo_type, region, source1, signal1, date_range[0], date_range[1], time_type
        )
        df2 = fetch_covidcast_data(
            geo_type, region, source2, signal2, date_range[0], date_range[1], time_type
        )
        fig = create_dual_axis_plot(df1, df2, signal_display1, signal_display2)
        fig.suptitle(
            f"Comparison of {signal_display1} vs {signal_display2} in {geo_type.capitalize()} {region_display}",
            fontsize=16,
            fontweight="bold",
            y=1.05,
        )
        st.pyplot(fig)

    with st.spinner("Calculating correlation..."):
        cor_df = calculate_epi_correlation(df1, df2, cor_by="geo_value")
        st.write(f'Signal correlation: **{cor_df.iloc[0]["cor"].round(3)}**')

st.divider()
