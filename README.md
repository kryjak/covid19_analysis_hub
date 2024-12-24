# COVID-19 Analysis Hub

A web application providing interactive tools for exploring COVID-19 data and signals. The app offers two main features:
- Signal Correlation Analysis
- Forecasting

**Live app**: [COVID-19 Analysis Hub](https://covid19-analysis-hub-852638696160.europe-central2.run.app/)

## Overview

The COVID-19 Analysis Hub is designed to help public health professionals, epidemiologists, and researchers explore relationships between different COVID-19 signals and create forecasts. The application uses data from the [Delphi Epidata API](https://cmu-delphi.github.io/delphi-epidata/), maintained by Carnegie Mellon University.

## Features

### 1. Signal Correlation Analysis

This tool allows users to:
- Compare any two COVID-19 signals (e.g., cases vs. deaths, hospitalizations vs. cases)
- Explore correlations at different geographic levels (nation, state, county, etc.)
- Calculate time-lagged correlations to identify leading/lagging relationships
- Choose between different correlation methods (Pearson, Kendall, Spearman)

The correlation analysis can help answer questions such as:
- How long after a rise in cases do we typically see a rise in hospitalizations?
- Which signals might serve as early warning indicators?
- How do relationships between signals vary across different regions?

### 2. Forecasting

The forecasting tool enables users to:
- Select multiple signals as predictors
- Choose the target signal to forecast
- Set the prediction date and forecast horizon
- Compare forecasts using different models:
  - ARX (AutoRegressive with eXogenous inputs)
  - Flatline
  - CDC Baseline

Key features include:
- Comparison between forecasts using real-time vs. revised data
- Confidence intervals for predictions
- Visual assessment of forecast accuracy
- Ability to experiment with different predictor combinations

## Getting Started

1. Visit the [live application](https://covid19-analysis-hub-852638696160.europe-central2.run.app/)
2. Choose either "Signal Correlation Analysis" or "Forecasting" from the home page
3. Follow the step-by-step instructions provided within each tool
4. Experiment with different signals, regions, and parameters

### API Key (Optional)

The app works without an API key, but you may encounter rate limits. To avoid this:
1. Request a free API key from Delphi's Epidata [here](https://docs.google.com/forms/d/e/1FAIpQLSe5i-lgb9hcMVepntMIeEo8LUZUMTUnQD3hbrQI3vSteGsl4w/viewform)
2. Enter the key in the API Settings section on the home page

## Feedback and Issues

Found a bug or have suggestions? Please let me know through our [feedback form](https://kryjak.notion.site/160beaf7b6f1815387f9ea9685b7bbee).

## Technical Information

The application is built using:
- Streamlit for the web interface
- Python and R for data analysis
- Docker for containerization
- Google Cloud Run for hosting

The source code is available at [GitHub](https://github.com/kryjak/covid19_analysis_hub).

## Acknowledgments

All data is sourced from the [Delphi Research Group](https://delphi.cmu.edu/) at Carnegie Mellon University through their Epidata API. Signals integrated into the app include:
- Cases and deaths (from JHU CSSE)
- Hospitalizations (from HHS)
- Test positivity rates (from COVID Act Now)
- And others 

Feel free to request more through the feedback form above. A full list of available signals can be found [here](https://delphi.cmu.edu/signals/signals/).
