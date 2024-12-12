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


helper_content = """<div style="background-color: rgba(144,238,144,0.15); padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">{text}</div>"""