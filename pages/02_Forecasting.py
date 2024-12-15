import streamlit as st
import pandas as pd
from available_signals import names_to_sources, sources_to_names
from helper_texts import helper_content, forecasting_page_helpers, forecasters_info
from utils import get_shared_dates, to_epidate_range, to_epiweek_range
from datetime import timedelta
from analysis_tools import fetch_covidcast_data, epi_predict, fetch_covidcast_data_multi
from plotting_utils import create_forecast_plot

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

# if the user doesn't select the predicted quantity as a predictor, add it manually
# this is so that the forecasting model can learn the relationship between the predictors and the predicted quantity
if predicted not in predictors:
    predictors_and_predicted = predictors + [predicted]
else:
    predictors_and_predicted = predictors

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
col_date, col_horizon = st.columns([3, 2])  # 3:2 ratio for the columns

with col_date:
    init_date = st.slider(
        "📅 **When is the prediction made?**",
        min_value=shared_init_date,
        max_value=shared_final_date,
        value=mid_date,
        help="The prediction will be made for the selected interval using all data available up until the start of this interval. An interval range of <30 days is recommended.",
    )

with col_horizon:
    prediction_length = st.slider(
        "📈 **Forecast horizon (days)**",
        min_value=1,
        max_value=45,
        value=7,
        help="Number of days ahead to forecast. Longer horizons may result in less accurate predictions."
    )

col1, col2, col3 = st.columns([5, 3, 1.4])
with col1:
    forecaster_type = st.radio("Forecaster type", forecasters_info.keys(), index=0, help="The type of forecaster to use.", key="forecaster_type", format_func=lambda x: x.capitalize().replace("_", " "))
with col3:
    if 'show_help_forecast_2' not in st.session_state:
        st.session_state.show_help_forecast_2 = False

    if st.button("🛈\nHelp", type="secondary", key="help_button_2"):
        st.session_state.show_help_forecast_2 = not st.session_state.show_help_forecast_2

if st.session_state.show_help_forecast_2:
    st.markdown(helper_content.format(text=forecasting_page_helpers["help_2"]), unsafe_allow_html=True)

st.info(forecasters_info[forecaster_type])

# Calculate final_date based on init_date and prediction_length
final_date = init_date + timedelta(days=prediction_length)

date_range_train = to_epidate_range(shared_init_date, init_date)
date_range_predict = to_epidate_range(init_date, final_date)

if st.button(
    "Fetch data and get predictions",
    type="primary",
    help="Click to fetch data and get predictions",
):
    with st.spinner("Fetching data..."):
        # Fetch data for all predictors - use latest available version
        df_merged = fetch_covidcast_data_multi(geo_type, region, predictors_and_predicted, date_range_train[0], date_range_train[-1], time_type, as_of=None)

        # Fetch data for all predictors - use version available *at the time of making the prediction*
        df_merged_as_of = fetch_covidcast_data_multi(geo_type, region, predictors_and_predicted, date_range_train[0], date_range_train[-1], time_type, as_of=final_date.strftime("%Y-%m-%d"))

        # Now get data for the predicted quantity - use latest available version again
        df_actual = fetch_covidcast_data(
            geo_type, region, predicted, date_range_predict[0], date_range_predict[-1], time_type, as_of=None
        )

    df_forecast = epi_predict(df_merged, predictors, predicted, forecaster_type, prediction_length, is_as_of=False)
    df_forecast_as_of = epi_predict(df_merged_as_of, predictors, predicted, forecaster_type, prediction_length, is_as_of=True)

    fig = create_forecast_plot(
        df_merged,
        df_merged_as_of,
        df_forecast,
        df_forecast_as_of,
        df_actual,
        init_date,
        predicted
    )
    st.plotly_chart(fig, use_container_width=True)    

    st.divider()