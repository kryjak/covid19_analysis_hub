import streamlit as st

st.set_page_config(
    page_title="COVID-19 Analysis Hub",
    page_icon="🦠",
    layout="wide"
)

st.title("COVID-19 Analysis Hub")

st.write("""
Welcome to the COVID-19 Analysis Hub! This application provides various tools to analyze 
COVID-19 data and signals. Choose one of the analysis tools below to get started.
""")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.info("""
    ### Signal Correlation Analysis
    Explore correlations between different COVID-19 signals across various geographic regions 
    and time periods. Compare trends and identify leading/lagging relationships between signals.
    """)
    st.page_link("pages/01_correlation.py", label="Go to Correlation Analysis", use_container_width=True)

with col2:
    st.info("""
    ### Other Analysis (Coming Soon)
    Description of your second analysis tool will go here.
    """)
    # Disabled button for the upcoming feature
    st.button("Coming Soon", disabled=True, use_container_width=True) 