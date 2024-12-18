import streamlit as st
import pandas as pd
from available_signals import names_to_sources, sources_to_names
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
)

from analysis_tools import (
    fetch_covidcast_data,
    get_lags_and_correlations,
)

from plotting_utils import (
    update_plot_with_lag,
    plot_correlation_vs_lag,
    plot_correlation_distribution,
)

from helper_texts import correlation_method_info, correlation_page_helpers, helper_content

st.set_page_config(page_title="Signal Correlation Analysis", page_icon="🦠", layout="wide")

covidcast_metadata = pd.read_csv("csv_data/covidcast_metadata.csv")

# Create header with better spacing and right-aligned help button
col1, _, col3 = st.columns([1, 7, 3])
with col1:
    st.page_link("Home.py", label="← Back to Home")
with col3:
    # Store the help button state in session state
    if 'show_help_corr_1' not in st.session_state:
        st.session_state.show_help_corr_1 = False
    
    if st.button("🛈\nHow to use this tool", type="secondary", key="help_button_1"):
        st.session_state.show_help_corr_1 = not st.session_state.show_help_corr_1

st.markdown("""
    <div style="background-color: rgba(255,165,0,0.1); padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h2 style="margin: 0;">COVID-19 Signal Correlation Analysis</h2>
    </div>
""", unsafe_allow_html=True)

if st.session_state.show_help_corr_1:
    st.markdown(helper_content.format(text=correlation_page_helpers["help_1"]), unsafe_allow_html=True)

all_sources_and_signals = list(names_to_sources.values())

st.markdown("📊 **Select two signals:**")
col1, col2 = st.columns(2)
with col1:
    source_and_signal1 = st.selectbox("Choose signal 1:", all_sources_and_signals, label_visibility="collapsed", format_func=lambda x: sources_to_names[x], index=0)
    # label_visibility="collapsed" might be disallowed in the future
    # https://docs.streamlit.io/develop/api-reference/widgets/st.selectbox
with col2:
    source_and_signal2 = st.selectbox(
        "Choose signal 2:",
        [signal for signal in all_sources_and_signals if signal != source_and_signal1],
        label_visibility="collapsed",
        format_func=lambda x: sources_to_names[x], index=1
    )

shared_geo_types = get_shared_geotypes(
    covidcast_metadata, source_and_signal1, source_and_signal2
)
shared_geo_types_display = [
    geotypes_to_display[geo_type] for geo_type in shared_geo_types
]

st.markdown("🌍 **Select a region of interest:**")
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
        covidcast_metadata, geo_type, source_and_signal1, source_and_signal2
    )
except ValueError:
    st.error(
        "Signals must have the same reporting frequency ('time_type') to be compared. Try changing the signal or at least one of the regions.",
        icon="🚨",
    )
    st.stop()

init_date, final_date = st.slider(
    "📅 **Select the date range:**",
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

button_enabled = source_and_signal1 != source_and_signal2 and geo_type != "dma" and "region" in locals()

if st.button(
    "Fetch data and calculate correlation",
    type="primary",
    disabled=not button_enabled,
    help="Click to fetch and analyze the selected signals",
):
    with st.spinner("Fetching data..."):
        # Store the fetched data in session state
        st.session_state.df1 = fetch_covidcast_data(
            geo_type, region, source_and_signal1, date_range[0], date_range[-1], time_type
        )
        st.session_state.df2 = fetch_covidcast_data(
            geo_type, region, source_and_signal2, date_range[0], date_range[-1], time_type
        )

    st.divider()

# Only show the lag slider and plot if we have data
if "df1" in st.session_state and "df2" in st.session_state:
    plot_container = st.empty()

    selected_lag = st.slider(
        f"📅 **Time lag ({time_type}s):**",
        min_value=-max_lag,
        max_value=max_lag,
        value=0,
        help=f"Shift signal 1 ({sources_to_names[source_and_signal1]}) forwards or backwards in time",
    )

    col1, _, col3 = st.columns([5, 4, 1.4])
    with col1:
        # Add the correlation method selection here
        correlation_method = st.radio(
            "📈 **Select correlation method:**",
            ["Pearson", "Kendall", "Spearman"],
            help="Choose the statistical method for calculating correlation between signals.",
            key="correlation_method"
        ).lower()
    with col3:
        # Store the help button state in session state
        if 'show_help_corr_2' not in st.session_state:
            st.session_state.show_help_corr_2 = False

        if st.button("🛈\nHelp", type="secondary", key="help_button_2"):
            st.session_state.show_help_corr_2 = not st.session_state.show_help_corr_2

    st.info(correlation_method_info[correlation_method])

    if st.session_state.show_help_corr_2:
        st.markdown(helper_content.format(text=correlation_page_helpers["help_2"]), unsafe_allow_html=True)

    # Update plot based on current lag and selected correlation method
    new_fig, new_correlation = update_plot_with_lag(
        st.session_state.df1,
        st.session_state.df2,
        sources_to_names[source_and_signal1],
        sources_to_names[source_and_signal2],
        geo_type,
        region_display,
        selected_lag,
        time_type,
        correlation_method  # Pass the selected method
    )

    with plot_container:
        st.plotly_chart(new_fig, use_container_width=True)

    st.write(
        f"Signal correlation at lag of {selected_lag} {time_type}s: **{new_correlation}**"
    )

    st.divider()

    if st.button(
        "Calculate best time lag",
        type="primary",
        help="Calculate the time lag that maximises the correlation between the two signals",
    ):
        with st.spinner(
            "This might take a while (up to ~5mins for the full data range)..."
        ):
            lags_and_correlations = get_lags_and_correlations(
                st.session_state.df1,
                st.session_state.df2,
                cor_by="geo_value",
                max_lag=max_lag,
                method=correlation_method  # Pass the selected method
            )
        best_lag = max(lags_and_correlations, key=lags_and_correlations.get)
        best_correlation = lags_and_correlations[best_lag]
        st.write(f"Best time lag: **{best_lag} {time_type}s**")
        st.write(f"Best correlation: **{best_correlation:.3f}**")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            fig1 = plot_correlation_vs_lag(lags_and_correlations, time_type)
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            fig2 = plot_correlation_distribution(lags_and_correlations)
            st.plotly_chart(fig2, use_container_width=True)
