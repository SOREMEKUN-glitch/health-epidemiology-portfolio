from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent

# Step 1: load the MAIN burden file
df = pd.read_csv(DATA_DIR / "TB_burden_countries_2026-10-07.csv")
print("Rows, columns:", df.shape)

# Step 2: time span and coverage
print("Years:", df["year"].min(), "to", df["year"].max())
print("Number of countries:", df["country"].nunique())

# Step 3: your five countries
countries = ["Nigeria", "South Africa", "India", "Brazil", "Canada"]
tb = df[df["country"].isin(countries)].copy()
print("\nRows per country:")
print(tb["country"].value_counts())

# Step 4: keep only the columns we need
cols = ["country", "iso3", "g_whoregion", "year",
        "e_pop_num", "e_inc_100k", "e_inc_100k_lo", "e_inc_100k_hi",
        "e_inc_num", "e_mort_100k", "e_tbhiv_prct",
        "c_newinc_100k", "c_cdr"]
tb = tb[cols]

# Step 5: missing values and duplicates
print("\nMissing values per column:")
print(tb.isna().sum())
print("\nDuplicate country-year rows:", tb.duplicated(subset=["country", "year"]).sum())

# Step 6: sanity check
print("\nSummary statistics:")
print(tb.describe().round(1))