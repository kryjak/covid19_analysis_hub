# Displayed name -> (source, signal)

names_to_sources = {
    "Cases (7-day avg., per 100k)": ("jhu-csse", "confirmed_7dav_incidence_prop"),
    "Deaths (7-day avg., per 100k)": ("jhu-csse", "deaths_7dav_incidence_prop"),
    "Confirmed Covid-19 Hospitalizations (7-day avg., per 100k)": (
        "hhs",
        "confirmed_admissions_covid_1d_prop_7dav",
    ),
    "Confirmed + Suspected Covid-19 Hospitalizations (7-day avg., per 100k)": (
        "hhs",
        "sum_confirmed_suspected_admissions_covid_1d_prop_7dav",
    ),
    "Confirmed Influenza Hospitalizations (7-day avg., per 100k)": (
        "hhs",
        "confirmed_admissions_influenza_1d_prop_7dav",
    ),
    "Percentage of Positive PCR Tests (7-day avg.)": (
        "covid-act-now",
        "pcr_specimen_positivity_rate",
    ),
    "Total PCR Tests (7-day avg.)": ("covid-act-now", "pcr_specimen_total_tests"),
}
