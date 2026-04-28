"""
combine_periods.py
------------------
Combines the three per-period spectral edge-list CSVs into a single file
with a leading 'period' column.  Use this if you want all three periods
in Power BI so you can slice/filter by period with a native Power BI slicer.

Run from anywhere inside the repo:
    python powerbi_visual/combine_periods.py

Output:
    powerbi_visual/spectral_all_periods.csv

The three source CSVs are NOT modified.
"""

from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO_ROOT / "plots" / "input"
OUT_PATH  = Path(__file__).resolve().parent / "spectral_all_periods.csv"

PERIODS = {
    "2010_2014": "2010-2014",
    "2015_2019": "2015-2019",
    "2020_2024": "2020-2024",
}

dfs = []
for key, label in PERIODS.items():
    csv = INPUT_DIR / f"spectral_graph_data_{key}.csv"
    df  = pd.read_csv(csv)
    df.insert(0, "period", label)
    dfs.append(df)
    print(f"  read {len(df):>3} rows from {csv.name}")

combined = pd.concat(dfs, ignore_index=True)
combined.to_csv(OUT_PATH, index=False)
print(f"\nSaved {len(combined)} total rows -> {OUT_PATH.relative_to(REPO_ROOT)}")
print("\nIn Power BI: load this file, add a Slicer on the 'period' column,")
print("and add all other columns to the visual's Edge List Columns bucket.")
