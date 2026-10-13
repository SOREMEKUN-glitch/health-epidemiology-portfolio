from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent        # main project folder
DATA_DIR = ROOT / "data"
TABLES_DIR = ROOT / "Tables"

# ---------- Load and filter ----------
df = pd.read_csv(DATA_DIR / "TB_burden_countries_2026-10-07.csv")

countries = ["Nigeria", "South Africa", "India", "Brazil", "Canada"]
cols = ["country", "iso3", "g_whoregion", "year",
        "e_pop_num", "e_inc_100k", "e_inc_100k_lo", "e_inc_100k_hi",
        "e_inc_num", "e_mort_100k", "e_tbhiv_prct",
        "c_newinc_100k", "c_cdr"]
tb = df[df["country"].isin(countries)][cols].copy()

# ---------- Stage 3: logic checks ----------
ok_bounds = ((tb["e_inc_100k_lo"] <= tb["e_inc_100k"]) &
             (tb["e_inc_100k"] <= tb["e_inc_100k_hi"])).all()
print("Low <= estimate <= high for every row:", ok_bounds)
print("Negative values:", (tb.select_dtypes("number") < 0).sum().sum())
print(tb.groupby("country")["year"].agg(["min", "max", "count"]))

# ---------- Readable column names ----------
tb = tb.rename(columns={
    "g_whoregion": "who_region",
    "e_pop_num": "population",
    "e_inc_100k": "incidence_per_100k",
    "e_inc_100k_lo": "incidence_lo",
    "e_inc_100k_hi": "incidence_hi",
    "e_inc_num": "incident_cases",
    "e_mort_100k": "mortality_per_100k",
    "e_tbhiv_prct": "tb_hiv_pct",
    "c_newinc_100k": "notification_per_100k",
    "c_cdr": "case_detection_pct",
})
tb.to_csv(DATA_DIR / "tb_clean.csv", index=False)

# ---------- Stage 4: incidence change table ----------
wide = tb.pivot(index="country", columns="year", values="incidence_per_100k")

summary = pd.DataFrame({
    "incidence_2000": wide[2000],
    "incidence_2024": wide[2024],
})
summary["abs_change"] = summary["incidence_2024"] - summary["incidence_2000"]
summary["pct_change"] = (summary["abs_change"] / summary["incidence_2000"] * 100).round(1)

peak = tb.loc[tb.groupby("country")["incidence_per_100k"].idxmax()]
summary["peak_year"] = peak.set_index("country")["year"]
summary["peak_incidence"] = peak.set_index("country")["incidence_per_100k"]

# ---------- Estimated vs reported, 2024 ----------
latest = tb[tb["year"] == 2024].set_index("country")
summary["notified_2024"] = latest["notification_per_100k"]
summary["missing_per_100k"] = (latest["incidence_per_100k"] - latest["notification_per_100k"]).round(1)
summary["detection_pct_2024"] = latest["case_detection_pct"]

summary = summary.sort_values("incidence_2024", ascending=False)
print("\n", summary.round(1).to_string())

TABLES_DIR.mkdir(exist_ok=True)
summary.round(1).to_csv(TABLES_DIR / "table1_incidence_change.csv")

# 1. Nigeria and Brazil: look at the whole series
for c in ["Nigeria", "Brazil"]:
    print("\n", c)
    print(tb[tb["country"] == c][["year", "incidence_per_100k", "incidence_lo", "incidence_hi"]].to_string(index=False))

# 2. South Africa: change from peak to 2024
sa = summary.loc["South Africa"]
print("\nSA change, peak to 2024 (%):",
      round((sa["incidence_2024"] - sa["peak_incidence"]) / sa["peak_incidence"] * 100, 1))

# 3. South Africa: HIV share of TB cases (every 4th year)
print(tb[tb["country"] == "South Africa"][["year", "tb_hiv_pct"]].iloc[::4].to_string(index=False))

# 4. Missing cases in absolute numbers, 2024
latest = latest.copy()
latest["missing_cases"] = ((latest["incidence_per_100k"] - latest["notification_per_100k"])
                           * latest["population"] / 100000).round(-3)
print("\n", latest[["population", "missing_cases"]])