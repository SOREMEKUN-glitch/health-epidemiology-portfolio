from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent
tb = pd.read_csv(ROOT / "data" / "tb_clean.csv")
FIG = ROOT / "Figures"
FIG.mkdir(exist_ok=True)

order = ["South Africa", "Nigeria", "India", "Brazil", "Canada"]

def panels():
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    axes = axes.flatten()
    axes[5].axis("off")           # spare panel
    return fig, axes

# ---------- Figure 1: incidence trends with uncertainty band ----------
fig, axes = panels()
for ax, c in zip(axes, order):
    d = tb[tb["country"] == c]
    ax.fill_between(d["year"], d["incidence_lo"], d["incidence_hi"], alpha=0.25)
    ax.plot(d["year"], d["incidence_per_100k"], linewidth=2)
    ax.set_title(c)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cases per 100,000")
axes[1].text(0.5, 0.08, "Constant WHO estimate:\ntrend cannot be assessed",
             transform=axes[1].transAxes, ha="center", fontsize=9)
fig.suptitle("Estimated TB incidence, 2000-2024 (shaded band = uncertainty range)")
fig.tight_layout()
fig.savefig(FIG / "fig1_incidence_trends.png", dpi=200)

# ---------- Figure 2: estimated vs reported cases ----------
fig, axes = panels()
for ax, c in zip(axes, order):
    d = tb[tb["country"] == c]
    ax.plot(d["year"], d["incidence_per_100k"], linewidth=2, label="Estimated (WHO)")
    ax.plot(d["year"], d["notification_per_100k"], linewidth=2, linestyle="--", label="Reported")
    ax.set_title(c)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cases per 100,000")
axes[0].legend(fontsize=8)
fig.suptitle("Estimated vs reported TB cases (gap = cases not detected or reported)")
fig.tight_layout()
fig.savefig(FIG / "fig2_estimated_vs_reported.png", dpi=200)

# ---------- Figure 3: South Africa, TB incidence and HIV share ----------
sa = tb[tb["country"] == "South Africa"]
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(sa["year"], sa["incidence_per_100k"], linewidth=2, label="TB incidence")
ax1.set_xlabel("Year")
ax1.set_ylabel("TB incidence per 100,000")
ax2 = ax1.twinx()
ax2.plot(sa["year"], sa["tb_hiv_pct"], linewidth=2, linestyle="--", color="tab:red", label="HIV+ share of TB")
ax2.set_ylabel("% of TB cases HIV-positive")
ax1.set_title("South Africa: TB incidence and HIV share of TB cases")
fig.tight_layout()
fig.savefig(FIG / "fig3_south_africa_hiv.png", dpi=200)

print("Saved 3 figures to", FIG)