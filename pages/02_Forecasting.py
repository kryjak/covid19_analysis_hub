import streamlit as st
import pandas as pd
from available_signals import names_to_sources, sources_to_names
from helper_texts import helper_content, forecasting_page_helpers
from utils import get_shared_dates, to_epidate_range, to_epiweek_range
from datetime import timedelta
from analysis_tools import fetch_covidcast_data, merge_dataframes

covidcast_metadata = pd.read_csv("csv_data/covidcast_metadata.csv")

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")

col1, col2, col3 = st.columns([1, 6, 1.2])
with col1:
    st.page_link("Home.py", label="← Back to Home")
with col3:
    # Store the help button state in session state
    if 'show_help_forecast_1' not in st.session_state:
        st.session_state.show_help_forecast_1 = False
    
    if st.button("🛈\nHelp", type="secondary", key="help_button_1"):
        st.session_state.show_help_forecast_1 = not st.session_state.show_help_forecast_1   

st.markdown("""
    <div style="background-color: rgba(255,165,0,0.1); padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <h2 style="margin: 0;">COVID-19 Forecasting</h2>
    </div>
""", unsafe_allow_html=True)

if st.session_state.show_help_forecast_1:
    st.markdown(helper_content.format(text=forecasting_page_helpers["help_1"]), unsafe_allow_html=True)

all_sources_and_signals = list(names_to_sources.values())
st.markdown("📊 **Select the predictors and the predicted quantity:**")
predictors = st.multiselect("Predictors", all_sources_and_signals, default=[names_to_sources[x] for x in ["Cases (7-day avg., per 100k)", "Deaths (7-day avg., per 100k)"]], help="All the predictors you want to use to train the forecasting model.", format_func=lambda x: sources_to_names[x])

if len(predictors) == 0:
    st.error("Please select at least one predictor to proceed with the forecasting.", icon="⚠️")
    st.stop()

predicted = st.selectbox("Predicted quantity", all_sources_and_signals, index=1, help="The quantity you want to predict (suggested: # of deaths).", format_func=lambda x: sources_to_names[x])

### HARDCODED TO THE UNITED STATES ONLY FOR NOW
geo_type = "nation"
region = 'us'

try:
    shared_init_date, shared_final_date, time_type = get_shared_dates(
        covidcast_metadata, geo_type, *predictors
    )
except ValueError:
    st.error(
        "Signals must have the same reporting frequency ('time_type') to be compared. Try changing the signal or at least one of the regions.",
        icon="🚨",
    )
    st.stop()

mid_date = shared_init_date + (shared_final_date - shared_init_date) / 2
delta = (shared_final_date - shared_init_date).days // 10
init_date, final_date = st.slider(
    "📅 **Select the forecasting interval:**",
    min_value=shared_init_date,
    max_value=shared_final_date,
    value=(mid_date - timedelta(days=delta), mid_date),
    help="The prediction will be made for the selected interval using all data available up until the start of this interval. An interval range of <30 days is recommended.",
)

date_range = to_epidate_range(shared_init_date, final_date)

if st.button(
    "Fetch Data",
    type="primary",
    help="Click to fetch data and get predictions",
):
    with st.spinner("Fetching data..."):
        # Fetch data for all predictors and store in a list
        dataframes = []
        for predictor in predictors:
            df = fetch_covidcast_data(
                geo_type, region, predictor, date_range[0], date_range[-1], time_type
            )
            dataframes.append(df)
            # Store in session state with dynamic keys
            st.session_state[f"df_{predictor}"] = df
        
        # Merge all dataframes sequentially
        df_merged = merge_dataframes(*dataframes)
        st.write(df_merged)
    st.divider()