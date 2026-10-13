from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
df = pd.read_csv(ROOT / "data" / "TB_burden_age_sex_2026-10-07.csv")

# What categories does this file contain?
for col in ["measure", "unit", "age_group", "sex", "risk_factor"]:
    print(col, "->", sorted(df[col].unique()))

# Look at one country: all-risk-factor rows only
countries = ["Nigeria", "South Africa", "India", "Brazil", "Canada"]
nig = df[(df["country"] == "Nigeria") & (df["risk_factor"] == "all")]
print("\nNigeria, risk_factor = all:")
print(nig[["measure", "unit", "age_group", "sex", "best", "lo", "hi"]].to_string(index=False))