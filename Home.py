import streamlit as st
from utils import save_the_api_key
from helper_texts import homepage_helpers
st.set_page_config(
    page_title="COVID-19 Analysis Hub",
    page_icon="🦠",
    layout="wide"
)

# Add custom CSS to style the page link
st.markdown("""
<style>
    .stPageLink {
        background-color: rgba(255,165,0,0.1);
        border-radius: 10px;
    }
    
    .custom-box {
        # border: 2px solid #ccc;
        border-radius: 10px;
        padding: 8px;
        background-color: rgba(200,200,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([6, 2.5])
with col1:
    st.title("COVID-19 Analysis Hub")
with col2:
    with st.expander("⚙️ API Settings"):
        api_key = st.text_input(
            "**(OPTIONAL)** Enter your Epidata API key:",
        help=homepage_helpers["api_settings"],
        type="password"  # This will hide the API key
        )
        if api_key:
            api_key_r = save_the_api_key(api_key)
            if api_key_r == api_key:
                st.success('API key saved.')
            else:
                st.error('API key save has failed.')

st.write("""
Welcome to the COVID-19 Analysis Hub! This application provides various tools to analyze 
COVID-19 data and signals. Choose one of the analysis tools below to get started.
""")

# st.markdown("<br>", unsafe_allow_html=True)  # Add extra space

col1, col2 = st.columns(2, gap="large")

with col1:
    st.page_link("pages/01_Signal_Correlation.py", 
                label="**Signal Correlation Analysis**", 
                use_container_width=True)
    st.markdown("""
    <div class="custom-box">
        Explore correlations between different COVID-19 signals across various geographic regions 
        and time periods. Compare trends and identify leading/lagging relationships between signals.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.page_link("pages/02_Forecasting.py", 
                label="**Forecasting**", 
                use_container_width=True)
    st.markdown("""
    <div class="custom-box">
        Explore forecasting models for COVID-19 signals.
    </div>
    """, unsafe_allow_html=True)
