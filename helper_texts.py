homepage_helpers = {
    "api_settings": "The app should work fine without an API key. However, if you make too many requests per hour, you will be temporarily rate limited. If you have an API key from Delphi's Epidata API, enter it here to avoid that. The key can be obtained at: https://docs.google.com/forms/d/e/1FAIpQLSe5i-lgb9hcMVepntMIeEo8LUZUMTUnQD3hbrQI3vSteGsl4w/viewform. It should arrive in your inbox within a few minutes.",
    "welcome_message": """Welcome to the COVID-19 Analysis Hub! This application provides two tools to explore 
    COVID-19 data and signals. Choose one of the analysis tools below to get started or scroll down for more information.""",
    "signal_correlation_help": """<div class="custom-box">
    Explore correlations between different COVID-19 signals. Compare trends and identify leading/lagging relationships between signals.
    </div>""",
    "forecasting_help": """<div class="custom-box">
    Use different forecasting models to predict future values of COVID-19 signals. How does data quality affect the accuracy of the forecasts?
    </div>""",
    "intro_text": """### Introduction
During emerging pandemics and public health crises, authorities are faced with making difficult decisions based on a multitude of factors. Their actions need to strike a delicate balance between minimizing the number of cases or deaths on one hand and reducing the economic impact of lockdowns or travel restrictions on the other. The task is further complicated by factors such as the availability of PPE supplies and vaccines, as well as public adherence to health policies.
    
In this app, you can explore two aspects relevant to decision making during pandemics. Below, you will find a general overview of these two tools. Detailed step-by-step instructions are given within individual pages.
    """,
    "sig_cor_text": """### Signal Correlation Analysis
This tool allows you to select two 'signals' relevant to Covid-19, for example the number of cases and the number of deaths, and explore how correlated they are with each other over time. In simple terms, it answers the question 'how does a change in the number of cases affect the number of deaths?'. Importantly, this tool also allows you to calculate *lagged* correlations. Put simply, we shouldn't expect an increase in cases to lead to an instant increase in deaths - this trend will be delayed based on the average disease duration (time between symptom onset and death/recovery). But by how much? Knowing the precise number of days can help decision makers better anticipate incoming waves of patients or deaths and therefore improve their policies, allocation of PPE equipment, and similar public health measures. In this tool, you can manually adjust the time delay between your selected signals and see how it affects their correlation strength. You can also use a button that performs this calculation automatically - it will calculate all lagged correlations and return the best one. Give it a try and see if you can predict what delay works best!""",
    "forecast_text": """### Forecasting
This tool allows you to make predictions of a given Covid-19 quantity based on one or more existing signals. For example, you could try to predict the number of deaths based on the number of past cases, deaths, and PCR tests. One important factor to keep in mind is that predictions are always done using data available at the time of the prediction, yet this data is often later updated as revised estimates come in. This raises the question - how does the quality of the forecast change as we feed updated information into the forecasting model? In this tool, you will see two types of predictions: one obtained using data that was available at the time of making the prediction, and one using the latest revision of this data. Is the latter prediction closer to the actual observed values? You will also see their 90% confidence intervals - is one of them narrower than the other and if so, does this always indicate that the prediction was made with more accurate data?""",
    "closing_text": """### Takeaway
Collectively, these two tools illustrate the difficulties that policy makers and public health professionals face when interpreting data about ongoing pandemics, especially as this data is continuously revised. You will be able to appreciate that it is hard to extract useful information from the time-lagged correlations when the time interval chosen is too short. Thus, when dealing with data scarcity, it will be hard to understand how one epidemiologic quantity is connected with another one (if at all), and what the time delay is before these effects kick in.

Likewise, you will see that data quality can significantly impact forecasting accuracy and the spread of the confidence intervals. Unfortunately, decision makers are of course unable to use more accurate data that will only arrive in the future - they must use what is available *now*, without knowing if this data is far from accurate. This highlights the challenges with accurate forecasting and interpretation of epidemiological signals.
""",
    "technical_text": """#### Technical info
This is a Streamlit app which uses epidemiological data from the Epidata project by the Delphi Group at Carnegie Mellon University. Because the app uses code in R (in addition to Python), I was not able to deploy it on Streamlit Cloud. Instead, I built a Docker container and deployed it on Google Cloud.

Relevant documentation:
- [Delphi Epidata Api](https://cmu-delphi.github.io/delphi-epidata/)
- [epidatr](https://cmu-delphi.github.io/epidatr/) and [epidatpy](https://cmu-delphi.github.io/epidatpy/) - R and Python packages for accessing Epidata
- [epiprocess](https://cmu-delphi.github.io/epiprocess/) - R package for processing Epidata data. Designed to work with `epipredict`:
- [epipredict](https://cmu-delphi.github.io/epipredict/) - R package for forecasting
- [Introduction to Epidemiological Forecasting](https://cmu-delphi.github.io/delphi-tooling-book/) - a detailed guide to the `epiprocess` and `epipredict` packages. It explains how to get data into the desired format, access historical versions of records, calculate correlations across regions and time, create forecasts, and more.
""",
    "errors_text": """#### Errors
The app is not perfect. I am sure there are some bugs lurking around. First, you might find that when trying to fetch the data, nothing will happen or you will get errors talking about rate limits and API keys. If that is the case, please see the 'API settings' field at the top of the Home page. You have probably exceeded the number of hourly requests allowed by the Epidata API.

If this doesn't help or you are confident it's not a rate limit issue, please copy the error message and/or take a screenshot and let me know by filling in this [feedback form](https://kryjak.notion.site/160beaf7b6f1815387f9ea9685b7bbee?pvs=105).


"""
}

correlation_method_info = {
    "pearson": """**Pearson correlation** measures linear relationships between signals. Best used when you expect a proportional relationship between signals (e.g., cases and deaths) and your data is normally distributed. Most common choice for COVID-19 analysis when signals follow similar patterns of increase and decrease.""",

    "kendall": """**Kendall correlation** measures the ordinal association (ranking agreement) between signals. More robust to outliers than Pearson and useful when you care about whether signals move in the same direction, regardless of magnitude. Good for COVID-19 data with extreme spikes or when comparing signals with different scales.""",

    "spearman": """**Spearman correlation** measures monotonic relationships, whether linear or not. 
    Like Kendall, it's based on ranks and resistant to outliers. Useful for COVID-19 analysis when 
    signals might be related but not in a strictly linear way, such as comparing cases to hospital 
    admissions during different variant waves."""
}

correlation_page_helpers = {
    "help_1": """<h3 style="margin: 0;">How to use this tool</h3>
    <ol>
        <li>Select two different COVID-19 signals to compare</li>
        <li>Choose a geographic level (nation, state, county, etc.)</li>
        <li>Select your region of interest</li>
        <li>Choose a date range for analysis</li>
        <li>Click 'Fetch Data' to load and visualize the signals</li>
        <li>Adjust the time lag slider to explore temporal relationships</li>
        <li>Use 'Calculate best time lag' to find the optimal correlation</li>
    </ol>
    <p style="margin: 0;">The tool supports different correlation methods (Pearson, Kendall, Spearman) and allows you to explore how signals relate to each other across time.</p>""",

    "help_2": """
    <p style="margin-bottom: 0;">Calculating the best time lag is a complex process that involves finding the optimal 
    time shift between two signals that maximizes their correlation. This is typically done 
    using statistical methods such as cross-correlation or dynamic time warping.</p>"""
}

forecasting_page_helpers = {
    "help_1": """<h3 style="margin: 0;">How to use this tool</h3>""",
    "help_2": """BLABLA"""
}

helper_content = """<div style="background-color: rgba(144,238,144,0.15); padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">{text}</div>"""

forecasters_info = {
    "arx_forecaster": """**ARX Forecaster** (AutoRegressive with eXogenous inputs) combines historical patterns with external factors to make predictions. It creates separate models for each future time point, making it particularly good at capturing both short-term trends and the influence of related signals (like how cases might affect future hospitalizations).""",
    
    "flatline_forecaster": """**Flatline Forecaster** is a simple but often effective model that assumes the future will match the most recent observation. It creates uncertainty intervals based on how wrong this assumption has been in the past. While basic, it can be surprisingly accurate for stable metrics and serves as a good baseline for comparison.""",
    
    "cdc_baseline_forecaster": """**CDC Baseline Forecaster** is an enhanced version of the flatline approach used by the CDC. It takes the latest value as its prediction but creates more sophisticated uncertainty ranges by analyzing historical patterns of change. This helps capture the natural variability seen in epidemic data while remaining computationally simple."""
}

forecasters_to_display = {
    "arx_forecaster": "ARX Forecaster",
    "flatline_forecaster": "Flatline Forecaster",
    "cdc_baseline_forecaster": "CDC Baseline Forecaster"
}