import pandas as pd

# data from: https://www.bls.gov/oes/current/msa_def.htm
# and converted to a csv
df = pd.read_csv("area_definitions_m2023.csv")

# if the 'May 2023 MSA code' contains the 'non-metropolitan' phrase, delete the row
df = df[~df["May 2022 MSA name"].str.contains("nonmetropolitan")]
# rename the 'May 2023 MSA code ' column to 'May 2023 MSA code'
df = df.rename(
    columns={"May 2023 MSA code ": "MSA code", "May 2022 MSA name": "MSA name"}
)
# select relevant columns
df = df[["State", "State abbreviation", "MSA code", "MSA name"]]

df = df.drop_duplicates()

df.to_csv("msa_processed.csv", index=False)
