"""
preprocess.py
-------------
Reads the SC_workingfile.dta (state-year panel already collapsed by
the authors with TX+LA+MS merged into a single "Texas" treated unit)
and the two SCweights files for spec10 (the preferred specification
used to produce Figure 3 of Akhtari, Bau & Laliberte 2020).

Merges the SC weights onto the panel and writes temp/sc_panel.csv.

Usage:  python code/preprocess.py
Inputs: input/SC_workingfile.dta
        input/SCweights/nonURMm10.dta
        input/SCweights/URMm10.dta
Output: temp/sc_panel.csv
"""

import os
import pandas as pd
import pyreadstat

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SC_FILE       = os.path.join("input", "SC_workingfile.dta")
WT_NONURM     = os.path.join("input", "SCweights", "nonURMm10.dta")
WT_URM        = os.path.join("input", "SCweights", "URMm10.dta")
OUTPUT_FILE   = os.path.join("temp",  "sc_panel.csv")

os.makedirs("temp", exist_ok=True)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
sc, _      = pyreadstat.read_dta(SC_FILE)
wt_non, _  = pyreadstat.read_dta(WT_NONURM)
wt_urm, _  = pyreadstat.read_dta(WT_URM)

# ---------------------------------------------------------------------------
# Build state-ID map from the panel (geo_temp is group(geo_collapse))
# ---------------------------------------------------------------------------
state_map = (sc[["geo_collapse", "geo_temp"]]
             .drop_duplicates()
             .rename(columns={"geo_temp": "_Co_Number"}))

# ---------------------------------------------------------------------------
# Attach state names to weights
# ---------------------------------------------------------------------------
wt_non = wt_non.merge(state_map, on="_Co_Number", how="left")
wt_urm = wt_urm.merge(state_map, on="_Co_Number", how="left")

# Keep only weight columns
wt_non = wt_non[["geo_collapse", "_W_Weight"]].rename(columns={"_W_Weight": "wt_nonURM"})
wt_urm = wt_urm[["geo_collapse", "_W_Weight"]].rename(columns={"_W_Weight": "wt_URM"})

# ---------------------------------------------------------------------------
# Merge weights onto panel
# ---------------------------------------------------------------------------
sc = sc.merge(wt_non, on="geo_collapse", how="left")
sc = sc.merge(wt_urm, on="geo_collapse", how="left")
sc["wt_nonURM"] = sc["wt_nonURM"].fillna(0)
sc["wt_URM"]    = sc["wt_URM"].fillna(0)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
sc.to_csv(OUTPUT_FILE, index=False)

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
texas = sc[sc["geo_collapse"] == "Texas"]
n_states = sc["geo_collapse"].nunique()
donor_non = wt_non[wt_non["wt_nonURM"] > 0.001]
donor_urm = wt_urm[wt_urm["wt_URM"]    > 0.001]

print("=" * 55)
print("Preprocessing complete")
print("=" * 55)
print(f"  Input SC panel  : {SC_FILE}")
print(f"  Output file     : {OUTPUT_FILE}")
print(f"  Total rows      : {len(sc):,}")
print(f"  States in panel : {n_states}  (incl. treated Texas=TX+LA+MS)")
print(f"  Year range      : {int(sc['year'].min())}--{int(sc['year'].max())}")
print(f"  Texas math_nonURM (2003): "
      f"{texas.loc[texas['year']==2003,'math_nonURM'].values[0]:.1f}")
print(f"  Texas math_URM    (2003): "
      f"{texas.loc[texas['year']==2003,'math_URM'].values[0]:.1f}")
print(f"  Non-zero SC weights (Whites): "
      f"{len(donor_non)} states")
print(f"  Non-zero SC weights (URMs)  : "
      f"{len(donor_urm)} states")
print("=" * 55)
