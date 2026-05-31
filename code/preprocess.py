"""
preprocess.py
-------------
Reads the raw SAT working file from input/, performs type coercions and
variable selection, and writes a clean analysis-ready CSV to temp/.

Usage:  python code/preprocess.py
Inputs: input/SAT_workfingfile.dta
Output: temp/clean_data.csv
"""

import os
import pandas as pd
import pyreadstat

# ---------------------------------------------------------------------------
# Paths (relative to repository root)
# ---------------------------------------------------------------------------
INPUT_FILE  = os.path.join("input", "SAT_workfingfile.dta")
OUTPUT_FILE = os.path.join("temp",  "clean_data.csv")

os.makedirs("temp", exist_ok=True)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
df, meta = pyreadstat.read_dta(INPUT_FILE)

# ---------------------------------------------------------------------------
# Coerce score / count columns stored as object to numeric
# ---------------------------------------------------------------------------
numeric_cols = [
    "mathscoretotalN", "verbalscoretotalN",
    "takesattotalN", "regsattotalN",
    "mathscoremaleN", "mathscorefemaleN",
    "verbalscoremaleN", "verbalscorefemaleN",
    "regsatmaleN", "regsatfemaleN",
    "takesatmaleN", "takesatfemaleN",
    "math_detrend", "verbal_detrend", "fixed_weights",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------------------------------------------------------------------
# Select columns needed for Table 1 (Panels A & B) and print summary
# ---------------------------------------------------------------------------
keep = [
    "year", "geography", "ethnicity", "geo_id", "ethn_id",
    "mathscoretotalN", "verbalscoretotalN",
    "takesattotalN", "fixed_weights",
    "treat", "post", "ban",
    "BH", "W", "A", "B", "H",
    "noban_sample", "math_detrend", "verbal_detrend",
]
df = df[keep].copy()

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
df.to_csv(OUTPUT_FILE, index=False)

# ---------------------------------------------------------------------------
# Console summary (mirrors Assignment 4 Task 6 style)
# ---------------------------------------------------------------------------
print("=" * 50)
print("Preprocessing complete")
print("=" * 50)
print(f"  Input file   : {INPUT_FILE}")
print(f"  Output file  : {OUTPUT_FILE}")
print(f"  Total rows   : {len(df):,}")
print(f"  Year range   : {int(df['year'].min())}–{int(df['year'].max())}")
print(f"  Treated states (treat==1): {df.loc[df['treat']==1,'geography'].nunique()}")
print(f"  Control states            : {df.loc[df['treat']==0,'geography'].nunique()}")
print(f"  Rows BH==1   : {int((df['BH']==1).sum()):,}")
print(f"  Rows W==1    : {int((df['W']==1).sum()):,}")
print(f"  Mean math SAT (BH, pre-2004) : "
      f"{df.loc[(df['BH']==1)&(df['year']<=2003),'mathscoretotalN'].mean():.1f}")
print(f"  Mean math SAT (W,  pre-2004) : "
      f"{df.loc[(df['W']==1) &(df['year']<=2003),'mathscoretotalN'].mean():.1f}")
print("=" * 50)
