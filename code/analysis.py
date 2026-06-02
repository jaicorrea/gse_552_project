"""
analysis.py
-----------
Replicates Figure 3 from:
  Akhtari, Bau & Laliberte (2020), "Affirmative Action and Pre-College
  Human Capital", NBER Working Paper 27779.

Uses the authors' preferred synthetic control specification (spec10):
  Predictors: pre-treatment averages of math/verbal SAT scores and
  test-take rates for both URM and non-URM students, plus education
  spending predictors.
  Treated unit: Texas (= TX + LA + MS collapsed).
  Donor pool: 40 unaffected states (excl. ND, SD, WY, DC, FL, WA, NE, MI).

The SC weights (nonURMm10.dta, URMm10.dta) were computed by the authors
using Stata's synth command with nested optimization; we apply them here
to construct counterfactuals and reproduce the figure.

Outputs:
  output/figures/figure3.png   -- two-panel replication of Figure 3
  output/tables/sc_dd_urm.tex  -- implied SC DD estimate, URMs
  output/tables/sc_dd_non.tex  -- implied SC DD estimate, Whites

Usage:  python code/analysis.py
Inputs: temp/sc_panel.csv
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
INPUT_FILE   = os.path.join("temp",  "sc_panel.csv")
OUT_FIG      = os.path.join("output", "figures", "figure3.png")
OUT_TABLES   = os.path.join("output", "tables")

os.makedirs(os.path.join("output", "figures"), exist_ok=True)
os.makedirs(OUT_TABLES, exist_ok=True)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
sc = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------------------------------
# Compute weighted counterfactual for each year
# CF_g[t] = sum_j( w_j * math_g[j, t] )  for all donor states j
# ---------------------------------------------------------------------------
years = sorted(sc["year"].unique())
cf_non = {}
cf_urm = {}

for yr in years:
    yr_data = sc[sc["year"] == yr]
    # Include all states (Texas weight is 0 in donor pool weight files)
    cf_non[yr] = (yr_data["math_nonURM"] * yr_data["wt_nonURM"]).sum()
    cf_urm[yr]  = (yr_data["math_URM"]    * yr_data["wt_URM"]).sum()

# ---------------------------------------------------------------------------
# Extract treated unit (Texas = TX + LA + MS)
# ---------------------------------------------------------------------------
texas = sc[sc["geo_collapse"] == "Texas"].copy().sort_values("year")
texas["CF_nonURM"] = texas["year"].map(cf_non)
texas["CF_URM"]    = texas["year"].map(cf_urm)

# Gap = treated - synthetic control
texas["gap_nonURM"] = texas["math_nonURM"] - texas["CF_nonURM"]
texas["gap_URM"]    = texas["math_URM"]    - texas["CF_URM"]

# ---------------------------------------------------------------------------
# DD coefficient: mean post-gap minus mean pre-gap
# (mirrors Stata: reg gap post)
# ---------------------------------------------------------------------------
pre  = texas[texas["year"] <  2004]
post = texas[texas["year"] >= 2004]

dd_non = post["gap_nonURM"].mean() - pre["gap_nonURM"].mean()
dd_urm = post["gap_URM"].mean()    - pre["gap_URM"].mean()

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print("=" * 62)
print("Replication Result -- Figure 3 (Synthetic Control)")
print("=" * 62)
print(f"\n  Whites SC DD estimate : {dd_non:.3f}  (paper: 6.273)")
print(f"  URMs   SC DD estimate : {dd_urm:.3f}  (paper: 10.778)")
print(f"\n  Difference from paper:")
print(f"    Whites: {dd_non - 6.273:.4f}")
print(f"    URMs  : {dd_urm - 10.778:.4f}")
print("=" * 62)
print()

# ---------------------------------------------------------------------------
# Write scalar .tex files
# ---------------------------------------------------------------------------
def write_scalar(fname, val):
    with open(os.path.join(OUT_TABLES, fname), "w") as f:
        f.write(val)

write_scalar("sc_dd_urm.tex", f"{dd_urm:.3f}")
write_scalar("sc_dd_non.tex", f"{dd_non:.3f}")
write_scalar("sc_diff_urm.tex", f"{10.778 - dd_urm:.1f}")
write_scalar("sc_diff_non.tex", f"{6.273 - dd_non:.1f}")
print(f"Scalar .tex files written to: {OUT_TABLES}/")

# ---------------------------------------------------------------------------
# Figure 3
# Two panels: (a) Whites, (b) URMs
# Replicates the style of Figure 3 in Akhtari et al. (2020)
# ---------------------------------------------------------------------------
YEARS = texas["year"].values

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
fig.subplots_adjust(wspace=0.35)

PANEL_CFG = [
    dict(
        ax=axes[0],
        treated=texas["math_nonURM"].values,
        synth=texas["CF_nonURM"].values,
        dd=dd_non,
        title="(a) Whites",
    ),
    dict(
        ax=axes[1],
        treated=texas["math_URM"].values,
        synth=texas["CF_URM"].values,
        dd=dd_urm,
        title="(b) URMs",
    ),
]

xlabels = ["98","99","00","01","02","03","04","05","06","07","08","09","10"]

for cfg in PANEL_CFG:
    ax = cfg["ax"]
    ax.plot(YEARS, cfg["treated"], color="black",
            marker="o", linewidth=1.4, markersize=4, label="Treated States")
    ax.plot(YEARS, cfg["synth"],   color="gray",
            marker="D", linewidth=1.4, markersize=4, linestyle="--",
            label="Synthetic Control Group")
    ax.axvline(x=2003.5, color="red", linewidth=1.0, linestyle="-")
    ax.set_xticks(YEARS)
    ax.set_xticklabels(xlabels, fontsize=8)
    ax.set_xlabel("Year", fontsize=9)
    ax.set_ylabel("Average math SAT score", fontsize=9)
    ax.set_title(cfg["title"], fontsize=10, fontweight="bold")
    ax.legend(fontsize=7.5, loc="upper left")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
    # Annotate DD coefficient in lower right
    ax.text(0.97, 0.04, f"DD coef: {cfg['dd']:.3f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color="black")
    ax.grid(axis="y", alpha=0.25)

fig.suptitle(
    "Figure 3: Synthetic Control Estimates of the Effect of AA on SAT Math Scores\n"
    "Akhtari, Bau & Laliberté (2020) — Replication using spec10 weights",
    fontsize=9, y=1.02
)

plt.tight_layout()
plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
plt.close()
print(f"Figure saved to: {OUT_FIG}")
