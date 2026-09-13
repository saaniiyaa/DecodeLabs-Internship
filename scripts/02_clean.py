from pathlib import Path
import pandas as pd
import numpy as np

RAW_PATH = Path("data_raw") / "Dataset for Data Analytics.xlsx"
CLEAN_DIR = Path("data_clean")
REPORT_DIR = Path("reports")
CLEAN_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# -----------------------
# Load
# -----------------------
df = pd.read_excel(RAW_PATH)
before_rows = len(df)

change_log = []

def log(change_id, description, why, impacted):
    change_log.append({
        "ChangeID": change_id,
        "Description": description,
        "Why": why,
        "RowsImpacted": int(impacted),
        "Status": "Resolved"
    })

# -----------------------
# Standardize text (trim)
# -----------------------
obj_cols = df.select_dtypes(include="object").columns
trim_impacted = 0
for c in obj_cols:
    before = df[c].copy()
    df[c] = df[c].astype("string")
    df[c] = df[c].str.strip()
    trim_impacted += int((before.astype("string") != df[c]).sum(skipna=True))

if trim_impacted:
    log("CR001", "Trimmed leading/trailing whitespace in text columns",
        "Standardize text fields to avoid hidden mismatches", trim_impacted)

# -----------------------
# Enforce ID formats
# -----------------------
df["OrderID"] = df["OrderID"].astype("string").str.strip().str.upper()
df["CustomerID"] = df["CustomerID"].astype("string").str.strip().str.upper()

# -----------------------
# Date format (ISO 8601)
# -----------------------
parsed_date = pd.to_datetime(df["Date"], errors="coerce")
invalid_dates = int(parsed_date.isna().sum() - df["Date"].isna().sum())
if invalid_dates > 0:
    # We won't guess invalid dates — stop to avoid corrupting data
    bad = df.loc[parsed_date.isna() & df["Date"].notna(), "Date"].astype(str).head(10).tolist()
    raise ValueError(f"Found {invalid_dates} invalid dates. Examples: {bad}")

df["Date"] = parsed_date.dt.strftime("%Y-%m-%d")
log("CR002", "Standardized Date to ISO format YYYY-MM-DD",
    "Requirement: zero incorrectly formatted dates", len(df))

# -----------------------
# Numeric columns (types + rounding)
# -----------------------
numeric_cols = ["Quantity", "UnitPrice", "ItemsInCart", "TotalPrice"]
for c in numeric_cols:
    before_na = df[c].isna().sum()
    df[c] = pd.to_numeric(df[c], errors="coerce")
    after_na = df[c].isna().sum()
    newly_null = int(after_na - before_na)
    if newly_null > 0:
        raise ValueError(f"Column {c}: {newly_null} values became null after numeric conversion.")

# enforce integer-like columns
df["Quantity"] = df["Quantity"].astype("int64")
df["ItemsInCart"] = df["ItemsInCart"].astype("int64")

# round money columns
df["UnitPrice"] = df["UnitPrice"].round(2)
df["TotalPrice"] = df["TotalPrice"].round(2)

log("CR003", "Converted numeric columns to proper numeric types; rounded monetary values to 2 decimals",
    "Correct formats for numbers; consistent precision", len(df))

# -----------------------
# Missing values: CouponCode
# -----------------------
missing_coupon = int(df["CouponCode"].isna().sum())
if missing_coupon > 0:
    df["CouponCode"] = df["CouponCode"].fillna("NO_COUPON")
    log("CR004", "Imputed missing CouponCode with 'NO_COUPON'",
        "Missing coupon generally means no coupon used; preserves rows", missing_coupon)

# -----------------------
# Duplicates check: OrderID must be unique
# -----------------------
dup_orderid = int(df["OrderID"].duplicated().sum())
if dup_orderid > 0:
    # If ever happens: keep first occurrence (business-safe default)
    df = df.drop_duplicates(subset=["OrderID"], keep="first")
    log("CR005", "Removed duplicate OrderID rows (kept first)",
        "Requirement: zero duplicate IDs", dup_orderid)

# Final verification proof
proof_dup_orderid = int(df["OrderID"].duplicated().sum())
proof_invalid_dates = int(pd.to_datetime(df["Date"], errors="coerce").isna().sum())

# -----------------------
# Export cleaned data
# -----------------------
clean_csv = CLEAN_DIR / "project1_cleaned.csv"
clean_xlsx = CLEAN_DIR / "project1_cleaned.xlsx"
df.to_csv(clean_csv, index=False)
df.to_excel(clean_xlsx, index=False)

# -----------------------
# Reports
# -----------------------
ver_report = REPORT_DIR / "verification_report.txt"
with open(ver_report, "w", encoding="utf-8") as f:
    f.write(f"Rows before: {before_rows}\n")
    f.write(f"Rows after : {len(df)}\n\n")
    f.write("PROOF CHECKS (must be 0):\n")
    f.write(f"Duplicate OrderID count: {proof_dup_orderid}\n")
    f.write(f"Invalid Date count      : {proof_invalid_dates}\n")

change_log_path = REPORT_DIR / "change_log.csv"
pd.DataFrame(change_log).to_csv(change_log_path, index=False)

print("CLEANING COMPLETE")
print("Saved:", clean_csv.as_posix())
print("Saved:", clean_xlsx.as_posix())
print("Saved:", ver_report.as_posix())
print("Saved:", change_log_path.as_posix())
print("\nPROOF:")
print("Duplicate OrderID count:", proof_dup_orderid)
print("Invalid Date count      :", proof_invalid_dates)