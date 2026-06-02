"""
analysis.py
-----------
Replicates Table 1 Panels A (URMs) and B (Whites) from:
  Akhtari, Bau & Laliberte (2020), "Affirmative Action and Pre-College
  Human Capital", NBER Working Paper 27779.

Identification strategy: Difference-in-Differences (DiD).
  y_ket = beta_DD (TreatedState_k x Post2003_t) + gamma*ban_kt
          + alpha_k + alpha_t + alpha_e + epsilon_ket

Uses pyfixest.feols(), a Python port of Stata's reghdfe, which applies
the same degrees-of-freedom correction for clustered SEs, giving
coefficients and standard errors that match the .do file exactly.

Outputs written to output/tables/:
  table1_panels_ab.tex  -- main LaTeX table fragment
  pa_math_coef.tex, pa_math_se.tex, ...  -- scalar fragments for prose

Usage:  python code/analysis.py
Inputs: temp/clean_data.csv
"""

import os
import pandas as pd
import pyfixest as pf

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
INPUT_FILE   = os.path.join("temp",  "clean_data.csv")
OUTPUT_TABLE = os.path.join("output", "tables", "table1_panels_ab.tex")
SCALARS_DIR  = os.path.join("output", "tables")

os.makedirs(SCALARS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Load preprocessed data
# ---------------------------------------------------------------------------
df = pd.read_csv(INPUT_FILE)
for col in ["mathscoretotalN", "verbalscoretotalN", "takesattotalN", "ban"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["treat_post"] = df["treat"] * df["post"]

# ---------------------------------------------------------------------------
# Paper's reported values (for console comparison only -- not used in output)
# ---------------------------------------------------------------------------
PAPER = {
    ("BH", "mathscoretotalN"):   dict(coef=8.009,  se=1.544),
    ("W",  "mathscoretotalN"):   dict(coef=4.048,  se=0.984),
    ("BH", "verbalscoretotalN"): dict(coef=-0.634, se=1.784),
    ("W",  "verbalscoretotalN"): dict(coef=0.034,  se=0.888),
}

# ---------------------------------------------------------------------------
# DiD regression using pyfixest.feols (Python port of Stata's reghdfe)
# Matches Stata's reghdfe DOF correction for clustered SEs exactly.
# ---------------------------------------------------------------------------
def run_did(data, group_col, outcome, weight_col="takesattotalN"):
    """
    Estimates:
      outcome ~ treat_post + ban | geo_id + year + ethn_id
    Weights: takesattotalN (aweight equivalent)
    Clustered SE: geo_id (state)
    """
    sub = data[data[group_col] == 1].copy()
    sub = sub.dropna(subset=[outcome, weight_col,
                              "treat_post", "ban",
                              "geo_id", "year", "ethn_id"])
    sub = sub[sub[weight_col] > 0].copy()

    # ethn_id FE only contributes if there is within-group variation
    if sub["ethn_id"].nunique() > 1:
        fe_spec = "geo_id + year + ethn_id"
    else:
        fe_spec = "geo_id + year"

    fit = pf.feols(
        fml=f"{outcome} ~ treat_post + ban | {fe_spec}",
        data=sub,
        weights=weight_col,
        vcov={"CRV1": "geo_id"},
    )

    coef  = fit.coef()["treat_post"]
    se    = fit.se()["treat_post"]
    pval  = fit.pvalue()["treat_post"]
    n_obs = fit._N
    r2    = fit._r2

    return {"coef": coef, "se": se, "pval": pval, "n_obs": n_obs, "r2": r2}


# ---------------------------------------------------------------------------
# Run all four regressions
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
    if pval < 0.01: return "***"
    if pval < 0.05: return "**"
    if pval < 0.10: return "*"
    return ""

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
print("=" * 62)
print("Replication Result")
print("=" * 62)
for grp, panel_label in panels:
    r = results[(grp, "mathscoretotalN")]
    p = PAPER[(grp, "mathscoretotalN")]
    print(f"\n{panel_label} -- Math SAT")
    print(f"  Paper reports : beta = {p['coef']:.3f}  (s.e. {p['se']:.3f})")
    print(f"  We obtain     : beta = {r['coef']:.3f}{stars(r['pval'])}"
          f"  (s.e. {r['se']:.3f})")
    print(f"  Difference    : {r['coef'] - p['coef']:.4f}  "
          f"(SE diff: {r['se'] - p['se']:.4f})")
print("=" * 62)
print()

# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------
def fmt_coef(r): return f"{r['coef']:.3f}{stars(r['pval'])}"
def fmt_se(r):   return f"({r['se']:.3f})"
def fmt_n(r):    return f"{r['n_obs']:,}"
def fmt_r2(r):   return f"{r['r2']:.3f}"

# ---------------------------------------------------------------------------
# Write LaTeX table fragment
# ---------------------------------------------------------------------------
latex = (
    r"\begin{table}[h]" + "\n"
    r"\centering" + "\n"
    r"\caption{Replication of Table 1, Panels A \& B: Effect of AA on SAT Scores}" + "\n"
    r"\label{tab:table1_ab}" + "\n"
    r"\small" + "\n"
    r"\begin{tabular}{lcc}" + "\n"
    r"\toprule" + "\n"
    r" & Math & Verbal \\" + "\n"
    r" & (1)  & (2)    \\" + "\n"
    r"\midrule" + "\n"
    r"\multicolumn{3}{l}{\textit{Panel A: URMs (Black and Hispanic)}} \\[4pt]" + "\n"
    f"DD coefficient & {fmt_coef(results[('BH','mathscoretotalN')])} & {fmt_coef(results[('BH','verbalscoretotalN')])} \\\\\n"
    f"               & {fmt_se(results[('BH','mathscoretotalN')])}   & {fmt_se(results[('BH','verbalscoretotalN')])}   \\\\\n"
    r"\\[-2pt]" + "\n"
    f"Observations   & {fmt_n(results[('BH','mathscoretotalN')])} & {fmt_n(results[('BH','verbalscoretotalN')])} \\\\\n"
    f"$R^2$          & {fmt_r2(results[('BH','mathscoretotalN')])} & {fmt_r2(results[('BH','verbalscoretotalN')])} \\\\\n"
    r"State, Year, Race FE & X & X \\" + "\n"
    r"\midrule" + "\n"
    r"\multicolumn{3}{l}{\textit{Panel B: Whites}} \\[4pt]" + "\n"
    f"DD coefficient & {fmt_coef(results[('W','mathscoretotalN')])} & {fmt_coef(results[('W','verbalscoretotalN')])} \\\\\n"
    f"               & {fmt_se(results[('W','mathscoretotalN')])}   & {fmt_se(results[('W','verbalscoretotalN')])}   \\\\\n"
    r"\\[-2pt]" + "\n"
    f"Observations   & {fmt_n(results[('W','mathscoretotalN')])} & {fmt_n(results[('W','verbalscoretotalN')])} \\\\\n"
    f"$R^2$          & {fmt_r2(results[('W','mathscoretotalN')])} & {fmt_r2(results[('W','verbalscoretotalN')])} \\\\\n"
    r"State, Year, Race FE & X & X \\" + "\n"
    r"\bottomrule" + "\n"
    r"\end{tabular}" + "\n"
    r"\begin{minipage}{\linewidth}" + "\n"
    r"\smallskip" + "\n"
    r"\footnotesize" + "\n"
    r"\textit{Notes}: Difference-in-differences estimates of the effect of reinstating" + "\n"
    r"affirmative action (AA) on mean SAT scores at the state--race--year level." + "\n"
    r"The DD coefficient is the interaction of an indicator for a treated state" + "\n"
    r"(Texas, Louisiana, Mississippi) and an indicator for post-2003" + "\n"
    r"(post-\textit{Grutter v.\ Bollinger}). Regressions include controls for" + "\n"
    r"AA-ban policy changes in control states. Cells are weighted by the number" + "\n"
    r"of test-takers. Standard errors (in parentheses) are clustered at the" + "\n"
    r"state level. $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$." + "\n"
    r"\end{minipage}" + "\n"
    r"\end{table}" + "\n"
)

with open(OUTPUT_TABLE, "w") as f:
    f.write(latex)
print(f"LaTeX table written to: {OUTPUT_TABLE}")

# ---------------------------------------------------------------------------
# Write scalar .tex files for every number used in paper.tex prose
# ---------------------------------------------------------------------------
def write_scalar(filename, value):
    with open(os.path.join(SCALARS_DIR, filename), "w") as f:
        f.write(value)

rPA_math   = results[("BH", "mathscoretotalN")]
rPA_verbal = results[("BH", "verbalscoretotalN")]
rPB_math   = results[("W",  "mathscoretotalN")]
rPB_verbal = results[("W",  "verbalscoretotalN")]

write_scalar("pa_math_coef.tex",   f"{rPA_math['coef']:.3f}")
write_scalar("pa_math_se.tex",     f"{rPA_math['se']:.3f}")
write_scalar("pa_math_stars.tex",  stars(rPA_math["pval"]))
write_scalar("pa_math_n.tex",      f"{rPA_math['n_obs']:,}")
write_scalar("pa_math_r2.tex",     f"{rPA_math['r2']:.3f}")

write_scalar("pb_math_coef.tex",   f"{rPB_math['coef']:.3f}")
write_scalar("pb_math_se.tex",     f"{rPB_math['se']:.3f}")
write_scalar("pb_math_stars.tex",  stars(rPB_math["pval"]))
write_scalar("pb_math_n.tex",      f"{rPB_math['n_obs']:,}")
write_scalar("pb_math_r2.tex",     f"{rPB_math['r2']:.3f}")

# Paper's reported SEs (for the comparison sentence in paper.tex)
write_scalar("pa_math_se_paper.tex", f"{PAPER[('BH','mathscoretotalN')]['se']:.3f}")
write_scalar("pb_math_se_paper.tex", f"{PAPER[('W', 'mathscoretotalN')]['se']:.3f}")

print(f"Scalar .tex files written to: {SCALARS_DIR}/")
