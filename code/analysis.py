"""
analysis.py
-----------
Replicates Table 1 Panels A (URMs) and B (Whites) from:
  Akhtari, Bau & Laliberte (2020), "Affirmative Action and Pre-College
  Human Capital", NBER Working Paper 27779.

Identification strategy: Difference-in-Differences (DiD).
  y_ket = beta_DD (TreatedState_k x Post2003_t) + gamma*ban_kt
          + alpha_k + alpha_t + alpha_e + epsilon_ket

  where alpha_k = state FE, alpha_t = year FE, alpha_e = ethnicity FE.
  Weighted by number of SAT test-takers (takesattotalN).
  Standard errors clustered at the state level.

Outputs (written to output/tables/):
  table1_panels_ab.tex  -- LaTeX table fragment (input-able from paper.tex)

Usage:  python code/analysis.py
Inputs: temp/clean_data.csv
"""

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
INPUT_FILE   = os.path.join("temp",  "clean_data.csv")
OUTPUT_TABLE = os.path.join("output", "tables", "table1_panels_ab.tex")

os.makedirs(os.path.join("output", "tables"), exist_ok=True)

# ---------------------------------------------------------------------------
# Load preprocessed data
# ---------------------------------------------------------------------------
df = pd.read_csv(INPUT_FILE)

# ---------------------------------------------------------------------------
# DiD regression helper
# ---------------------------------------------------------------------------
PAPER = {
    ("BH", "mathscoretotalN"):   dict(coef=8.009,  se=1.544),
    ("W",  "mathscoretotalN"):   dict(coef=4.048,  se=0.984),
    ("BH", "verbalscoretotalN"): dict(coef=-0.634, se=1.784),
    ("W",  "verbalscoretotalN"): dict(coef=0.034,  se=0.888),
}


def run_did(data, group_col, outcome, weight_col="takesattotalN"):
    """
    DiD: outcome ~ treat*post + ban + state_FE + year_FE + ethn_FE
    Weights: analytical (aweight equivalent via WLS).
    Clustered SE: state (geo_id).
    Returns dict with coef, se, pval, n_obs, r2.
    """
    sub = data[data[group_col] == 1].copy()
    sub = sub.dropna(subset=[outcome, weight_col,
                              "treat", "post", "ban",
                              "geo_id", "year", "ethn_id"])
    sub = sub[sub[weight_col] > 0].copy()

    sub["treat_post"] = sub["treat"].astype(float) * sub["post"].astype(float)

    # Fixed-effect dummies
    state_d = pd.get_dummies(sub["geo_id"].astype(int),
                              prefix="st", drop_first=True).astype(float)
    year_d  = pd.get_dummies(sub["year"].astype(int),
                              prefix="yr", drop_first=True).astype(float)
    parts   = [sub[["treat_post", "ban"]].astype(float), state_d, year_d]

    # Ethnicity FE only if there is within-group variation
    if sub["ethn_id"].nunique() > 1:
        ethn_d = pd.get_dummies(sub["ethn_id"].astype(int),
                                 prefix="et", drop_first=True).astype(float)
        parts.append(ethn_d)

    X      = sm.add_constant(pd.concat(parts, axis=1))
    y      = sub[outcome].astype(float)
    w      = sub[weight_col].astype(float)
    groups = sub["geo_id"].astype(int).values

    res = sm.WLS(y, X, weights=w).fit(
        cov_type="cluster",
        cov_kwds={"groups": groups},
    )

    return {
        "coef":  res.params["treat_post"],
        "se":    res.bse["treat_post"],
        "pval":  res.pvalues["treat_post"],
        "n_obs": len(sub),
        "r2":    res.rsquared,
    }


# ---------------------------------------------------------------------------
# Run all four regressions (Panel A & B x Math & Verbal)
# ---------------------------------------------------------------------------
outcomes = [
    ("mathscoretotalN",   "Math"),
    ("verbalscoretotalN", "Verbal"),
]
panels = [
    ("BH", "Panel A: URMs"),
    ("W",  "Panel B: Whites"),
]

results = {}
for grp, _ in panels:
    for outcome, _ in outcomes:
        results[(grp, outcome)] = run_did(df, grp, outcome)

# ---------------------------------------------------------------------------
# Stars helper
# ---------------------------------------------------------------------------
def stars(pval):
    if pval < 0.01:  return "***"
    if pval < 0.05:  return "**"
    if pval < 0.10:  return "*"
    return ""


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print("=" * 60)
print("Replication Result")
print("=" * 60)
for grp, panel_label in panels:
    r = results[(grp, "mathscoretotalN")]
    p = PAPER[(grp, "mathscoretotalN")]
    print(f"\n{panel_label} — Math SAT")
    print(f"  Paper reports : beta = {p['coef']:.3f}  (s.e. {p['se']:.3f})")
    print(f"  We obtain     : beta = {r['coef']:.3f}{stars(r['pval'])}"
          f"  (s.e. {r['se']:.3f})")
    print(f"  Difference    : {r['coef'] - p['coef']:.4f}")
print("=" * 60)
print()


# ---------------------------------------------------------------------------
# Write LaTeX table fragment
# ---------------------------------------------------------------------------
def fmt_coef(r):
    """Format coefficient with stars."""
    return f"{r['coef']:.3f}{stars(r['pval'])}"

def fmt_se(r):
    return f"({r['se']:.3f})"

def fmt_n(r):
    return f"{r['n_obs']:,}"

def fmt_r2(r):
    return f"{r['r2']:.3f}"


latex = r"""\begin{table}[h]
\centering
\caption{Replication of Table 1, Panels A \& B: Effect of AA on SAT Scores}
\label{tab:table1_ab}
\small
\begin{tabular}{lcc}
\toprule
 & Math & Verbal \\
 & (1)  & (2)    \\
\midrule
\multicolumn{3}{l}{\textit{Panel A: URMs (Black and Hispanic)}} \\[4pt]
""" + \
f"DD coefficient & {fmt_coef(results[('BH','mathscoretotalN')])} & {fmt_coef(results[('BH','verbalscoretotalN')])} \\\\\n" + \
f"               & {fmt_se(results[('BH','mathscoretotalN')])}   & {fmt_se(results[('BH','verbalscoretotalN')])}   \\\\\n" + \
r"\\[-2pt]" + "\n" + \
f"Observations   & {fmt_n(results[('BH','mathscoretotalN')])} & {fmt_n(results[('BH','verbalscoretotalN')])} \\\\\n" + \
f"$R^2$          & {fmt_r2(results[('BH','mathscoretotalN')])} & {fmt_r2(results[('BH','verbalscoretotalN')])} \\\\\n" + \
r"State, Year, Race FE & X & X \\" + "\n" + \
r"\midrule" + "\n" + \
r"\multicolumn{3}{l}{\textit{Panel B: Whites}} \\[4pt]" + "\n" + \
f"DD coefficient & {fmt_coef(results[('W','mathscoretotalN')])} & {fmt_coef(results[('W','verbalscoretotalN')])} \\\\\n" + \
f"               & {fmt_se(results[('W','mathscoretotalN')])}   & {fmt_se(results[('W','verbalscoretotalN')])}   \\\\\n" + \
r"\\[-2pt]" + "\n" + \
f"Observations   & {fmt_n(results[('W','mathscoretotalN')])} & {fmt_n(results[('W','verbalscoretotalN')])} \\\\\n" + \
f"$R^2$          & {fmt_r2(results[('W','mathscoretotalN')])} & {fmt_r2(results[('W','verbalscoretotalN')])} \\\\\n" + \
r"State, Year, Race FE & X & X \\" + "\n" + \
r"""\bottomrule
\end{tabular}
\begin{minipage}{\linewidth}
\smallskip
\footnotesize
\textit{Notes}: Difference-in-differences estimates of the effect of reinstating
affirmative action (AA) on mean SAT scores at the state--race--year level.
The DD coefficient is the interaction of an indicator for a treated state
(Texas, Louisiana, Mississippi) and an indicator for post-2003 (post-\textit{Grutter v.\
Bollinger}). Regressions include controls for AA-ban policy changes in
control states. Cells are weighted by the number of test-takers.
Standard errors (in parentheses) are clustered at the state level.
$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$.
\end{minipage}
\end{table}
"""

with open(OUTPUT_TABLE, "w") as f:
    f.write(latex)

print(f"LaTeX table written to: {OUTPUT_TABLE}")

# ---------------------------------------------------------------------------
# Write individual scalar .tex files so paper.tex can \input every number
# ---------------------------------------------------------------------------
SCALARS_DIR = os.path.join("output", "tables")

def write_scalar(filename, value):
    """Write a bare value (no newline) to output/tables/<filename>.tex."""
    path = os.path.join(SCALARS_DIR, filename)
    with open(path, "w") as f:
        f.write(value)

rPA_math   = results[("BH", "mathscoretotalN")]
rPA_verbal = results[("BH", "verbalscoretotalN")]
rPB_math   = results[("W",  "mathscoretotalN")]
rPB_verbal = results[("W",  "verbalscoretotalN")]

# Panel A math
write_scalar("pa_math_coef.tex",  f"{rPA_math['coef']:.3f}")
write_scalar("pa_math_se.tex",    f"{rPA_math['se']:.3f}")
write_scalar("pa_math_stars.tex", stars(rPA_math["pval"]))
write_scalar("pa_math_n.tex",     f"{rPA_math['n_obs']:,}")
write_scalar("pa_math_r2.tex",    f"{rPA_math['r2']:.3f}")

# Panel B math
write_scalar("pb_math_coef.tex",  f"{rPB_math['coef']:.3f}")
write_scalar("pb_math_se.tex",    f"{rPB_math['se']:.3f}")
write_scalar("pb_math_stars.tex", stars(rPB_math["pval"]))
write_scalar("pb_math_n.tex",     f"{rPB_math['n_obs']:,}")
write_scalar("pb_math_r2.tex",    f"{rPB_math['r2']:.3f}")

# SE difference from paper (for discussion paragraph)
paper_pa_se = 1.544
paper_pb_se = 0.984
write_scalar("pa_math_se_paper.tex", f"{paper_pa_se:.3f}")
write_scalar("pb_math_se_paper.tex", f"{paper_pb_se:.3f}")

print(f"Scalar .tex files written to: {SCALARS_DIR}/")
