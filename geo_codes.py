# State and county FIPS codes from: https://github.com/ChuckConnell/articles/blob/master/fips2county.tsv

import pandas as pd

# The following geography types are supported by the COVIDcast API:
# https://cmu-delphi.github.io/delphi-epidata/api/covidcast_geography.html
geotypes_to_display = {
    "county": "County",
    "state": "State",
    "nation": "Nation",
    "hrr": "Hospital Referral Region",
    "hhs": "HHS Regional Office",
    "msa": "Metropolitan Statistical Area",
    "dma": "Designated Market Area",
}
display_to_geotypes = {v: k for k, v in geotypes_to_display.items()}

# Now read in the data for each of them
fips_df = pd.read_csv(
    "csv_data/fips2county.tsv", sep="\t", header="infer", dtype="str", encoding="latin-1"
)
hrr_df = pd.read_csv("csv_data/ZipHsaHrr19.csv", dtype="str")
msa_df = pd.read_csv("csv_data/msa_processed.csv", dtype="str")

# Nations
# Currently only US is supported
nation_to_display = {"us": "United States"}
display_to_nation = {v: k for k, v in nation_to_display.items()}

# States
state_df = fips_df[["StateName", "StateAbbr"]].drop_duplicates()
state_df["StateAbbr"] = state_df["StateAbbr"].str.lower()
state_abbrvs_to_display = {
    row["StateAbbr"]: row["StateName"] for _, row in state_df.iterrows()
}
display_to_state_abbrvs = {v: k for k, v in state_abbrvs_to_display.items()}

# Counties
county_df = fips_df[["CountyName", "CountyFIPS"]].drop_duplicates()
county_fips_to_display = {
    row["CountyFIPS"]: row["CountyName"] for _, row in county_df.iterrows()
}
display_to_county_fips = {v: k for k, v in county_fips_to_display.items()}

county_by_state = fips_df.groupby("StateName")["CountyName"].apply(list).to_dict()

# Hospital Referral Regions
hrr_df = hrr_df[["hrrnum", "hrrcity", "hrrstate"]].drop_duplicates()
hrr_to_display = {
    row["hrrnum"]: f"{row['hrrcity']}, {row['hrrstate']}"
    for _, row in hrr_df.iterrows()
}
display_to_hrr = {v: k for k, v in hrr_to_display.items()}

hrr_by_state = (
    hrr_df.groupby("hrrstate")["hrrcity"]
    .apply(
        lambda x: [
            f"{city}, {state}" for city, state in zip(x, [x.name] * len(x))
        ]
    )
    .to_dict()
)

hrr_by_state = {
    state_abbrvs_to_display[state.lower()]: hrrs for state, hrrs in hrr_by_state.items()
}

# DHHS Regional Offices
hss_region_to_display = {
    "1": "Region 1 (Boston)",
    "2": "Region 2 (New York)",
    "3": "Region 3 (Philadelphia)",
    "4": "Region 4 (Atlanta)",
    "5": "Region 5 (Chicago)",
    "6": "Region 6 (Dallas)",
    "7": "Region 7 (Kansas City)",
    "8": "Region 8 (Denver)",
    "9": "Region 9 (San Francisco)",
    "10": "Region 10 (Seattle)",
}
display_to_hss_region = {v: k for k, v in hss_region_to_display.items()}

# Metropolitan Statistical Areas
msa_to_display = {row["MSA code"]: row["MSA name"] for _, row in msa_df.iterrows()}
display_to_msa = {v: k for k, v in msa_to_display.items()}

msa_by_state = msa_df.groupby("State")["MSA name"].apply(list).to_dict()

# Designated Market Areas
# Designated Market Areas (DMAs) are proprietary information released by Nielsen. The subscription to this data costs $8000.
# So we don't include it in the app.
