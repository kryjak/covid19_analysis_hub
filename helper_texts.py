homepage_helpers = {
    "api_settings": "The app should work fine without an API key. However, if you make too many requests per hour, you will be temporarily rate limited. If you have an API key from Delphi's Epidata API, enter it here to avoid that. The key can be obtained at: https://docs.google.com/forms/d/e/1FAIpQLSe5i-lgb9hcMVepntMIeEo8LUZUMTUnQD3hbrQI3vSteGsl4w/viewform. It should arrive in your inbox within a few minutes."
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
    "help_1": """<h3 style="margin: 0;">How to use this tool</h3>"""
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