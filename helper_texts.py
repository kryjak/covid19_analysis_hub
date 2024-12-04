from typing import Literal

def get_correlation_method_info(method: Literal["pearson", "kendall", "spearman"]) -> str:
    """Returns help text for each correlation method."""
    info = {
        "pearson": """Pearson correlation measures linear relationships between signals. 
        Best used when you expect a proportional relationship between signals (e.g., cases and deaths) 
        and your data is normally distributed. Most common choice for COVID-19 analysis when signals 
        follow similar patterns of increase and decrease.""",
        
        "kendall": """Kendall correlation measures the ordinal association (ranking agreement) between signals. 
        More robust to outliers than Pearson and useful when you care about whether signals move in the 
        same direction, regardless of magnitude. Good for COVID-19 data with extreme spikes or when 
        comparing signals with different scales.""",
        
        "spearman": """Spearman correlation measures monotonic relationships, whether linear or not. 
        Like Kendall, it's based on ranks and resistant to outliers. Useful for COVID-19 analysis when 
        signals might be related but not in a strictly linear way, such as comparing cases to hospital admissions 
        during different variant waves."""
    }
    return info[method]