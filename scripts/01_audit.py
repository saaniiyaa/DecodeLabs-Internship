from pathlib import Path
import pandas as pd
import re

RAW_DIR = Path("data_raw")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

files = [p for p in RAW_DIR.iterdir() if p.suffix.lower() in [".csv", ".xlsx", ".xls"]]
if not files:
    raise SystemExit("No CSV/XLSX found in data_raw/. Put the raw file there and rerun.")

path = sorted(files)[0]
print("Using file:", path.name)

if path.suffix.lower() == ".csv":
    df = pd.read_csv(path)
else:
    df = pd.read_excel(path)

print("\nShape:", df.shape)
print("\nColumns:", list(df.columns))

# Basic sample
print("\nHead (first 5 rows):")
print(df.head(5))

# Nulls
nulls = df.isna().sum().sort_values(ascending=False)
nulls = nulls[nulls > 0]
print("\nNull counts (only >0):")
print(nulls if len(nulls) else "No nulls detected.")

# Duplicate full rows
dup_rows = df.duplicated().sum()
print("\nDuplicate FULL rows:", int(dup_rows))

# Candidate ID columns
def looks_like_id(col):
    c = str(col).strip().lower()
    return bool(re.search(r"(^id$)|(_id$)|(id$)|(\bid\b)", c))

id_candidates = [c for c in df.columns if looks_like_id(c)]
print("\nID candidates:", id_candidates if id_candidates else "None detected by name.")

for c in id_candidates:
    s = df[c]
    n = len(s)
    n_null = int(s.isna().sum())
    n_unique = int(s.nunique(dropna=True))
    n_dups = int(s.duplicated().sum())
    print(f" - {c}: rows={n}, nulls={n_null}, unique(non-null)={n_unique}, duplicated={n_dups}")

# Candidate date columns (by name)
def looks_like_date(col):
    c = str(col).strip().lower()
    return any(k in c for k in ["date", "time", "timestamp", "dob"])

date_candidates = [c for c in df.columns if looks_like_date(c)]
print("\nDate candidates:", date_candidates if date_candidates else "None detected by name.")

for c in date_candidates:
    parsed = pd.to_datetime(df[c], errors="coerce")
    invalid = int(parsed.isna().sum() - df[c].isna().sum())
    print(f" - {c}: invalid_dates={invalid} (excluding blanks)")
    if invalid > 0:
        bad_examples = df.loc[parsed.isna() & df[c].notna(), c].astype(str).head(5).tolist()
        print("   examples:", bad_examples)

# Whitespace issues in text columns
obj_cols = [c for c in df.columns if df[c].dtype == "object"]
ws_issues = {}
for c in obj_cols:
    s = df[c].dropna().astype(str)
    if len(s) == 0:
        continue
    ws = (s != s.str.strip()).sum()
    if ws:
        ws_issues[c] = int(ws)

print("\nText columns with leading/trailing spaces (count):")
print(ws_issues if ws_issues else "No obvious trim issues detected.")

# Save a quick report
report_path = REPORT_DIR / "audit_summary.txt"
with open(report_path, "w", encoding="utf-8") as f:
    f.write(f"File: {path.name}\n")
    f.write(f"Shape: {df.shape}\n\n")
    f.write("Null counts (>0):\n")
    f.write((nulls.to_string() if len(nulls) else "No nulls detected.") + "\n\n")
    f.write(f"Duplicate FULL rows: {dup_rows}\n\n")
    f.write(f"ID candidates: {id_candidates}\n")
    f.write(f"Date candidates: {date_candidates}\n")
print("\nSaved:", report_path.as_posix())