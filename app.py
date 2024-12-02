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
from utils import get_shared_geotypes, get_shared_dates
# import covidcast as cc
# import delphi_epidata as de

covidcast_metadata = pd.read_csv("covidcast_metadata.csv")

st.title("COVID-19 Signal Correlation and Forecast Analysis")
st.write("This app allows you to explore the correlation between two COVID-19 signals.")

signals = list(names_to_sources.keys())

col1, col2 = st.columns(2)
with col1:
    signal1 = st.selectbox("Choose signal 1:", signals)
with col2:
    signal2 = st.selectbox(
        "Choose signal 2:", [signal for signal in signals if signal != signal1]
    )

shared_geo_types = get_shared_geotypes(covidcast_metadata, signal1, signal2)
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

try:
    shared_init_date, shared_final_date, time_type = get_shared_dates(
        covidcast_metadata, signal1, signal2, geo_type
    )
except ValueError:
    st.error(
        "Signals must have the same reporting frequency ('time_type') to be compared. Try changing the signal or at least one of the regions.",
        icon="🚨",
    )
    st.stop()

chosen_init_date, chosen_final_date = st.slider(
    "Date range:",
    min_value=shared_init_date,
    max_value=shared_final_date,
    value=(shared_init_date, shared_final_date),
)
