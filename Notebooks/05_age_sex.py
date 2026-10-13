from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent
TABLES = ROOT / "Tables"
FIG = ROOT / "Figures"
TABLES.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

df = pd.read_csv(ROOT / "data" / "TB_burden_age_sex_2026-10-07.csv")

order = ["South Africa", "Nigeria", "India", "Brazil", "Canada"]
bands = ["0-4", "5-14", "15-24", "25-34", "35-44", "45-54", "55-64", "65plus"]

# Overall TB only (not risk-factor-attributable rows), incidence only
d = df[(df["country"].isin(order)) &
       (df["risk_factor"] == "all") &
       (df["measure"] == "inc")]

# ---------- Validation: do the bands add up to the total? ----------
total = d[(d["age_group"] == "all") & (d["sex"] == "a")].set_index("country")["best"]
age = d[d["age_group"].isin(bands) & (d["sex"] == "a")]
sum_bands = age.groupby("country")["best"].sum()

check = pd.DataFrame({"total_all_ages": total, "sum_of_age_bands": sum_bands})
check["difference_pct"] = ((check["sum_of_age_bands"] - check["total_all_ages"])
                           / check["total_all_ages"] * 100).round(1)
print("Validation (age bands vs total):")
print(check.loc[order])

# ---------- Table 2: share of cases by age group (%) ----------
counts = age.pivot(index="country", columns="age_group", values="best")[bands]
share = counts.div(counts.sum(axis=1), axis=0) * 100
print("\nShare of estimated TB cases by age group (%):")
print(share.loc[order].round(1))
share.loc[order].round(1).to_csv(TABLES / "table2_age_share_pct.csv")

# ---------- Table 3: male-to-female ratio ----------
sx = d[(d["age_group"] == "all") & (d["sex"].isin(["f", "m"]))]
sx = sx.pivot(index="country", columns="sex", values="best")
sx["male_to_female_ratio"] = (sx["m"] / sx["f"]).round(2)
sx["male_pct"] = (sx["m"] / (sx["m"] + sx["f"]) * 100).round(1)
print("\nSex distribution (all ages):")
print(sx.loc[order])
sx.loc[order].to_csv(TABLES / "table3_sex_ratio.csv")

# ---------- Figure 4: age and sex, as % of each country's cases ----------
sex_age = d[d["age_group"].isin(bands) & d["sex"].isin(["f", "m"])]
x = np.arange(len(bands))
w = 0.4

fig, axes = plt.subplots(2, 3, figsize=(13, 7))
axes = axes.flatten()
axes[5].axis("off")
for ax, c in zip(axes, order):
    s = (sex_age[sex_age["country"] == c]
         .pivot(index="age_group", columns="sex", values="best")
         .reindex(bands))
    tot_c = s.sum().sum()
    ax.bar(x - w/2, s["f"] / tot_c * 100, w, label="Female")
    ax.bar(x + w/2, s["m"] / tot_c * 100, w, label="Male")
    ax.set_xticks(x)
    ax.set_xticklabels(bands, rotation=45)
    ax.set_title(c)
    ax.set_ylabel("% of country's estimated cases")
    ax.set_xlabel("Age group (years)")
axes[0].legend(fontsize=8)
fig.suptitle("Estimated TB cases by age group and sex, 2024 (modelled estimates)")
fig.tight_layout()
fig.savefig(FIG / "fig4_age_sex.png", dpi=200)
print("\nSaved figure and tables.")