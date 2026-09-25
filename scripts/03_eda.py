from pathlib import Path
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = Path("data_clean") / "project1_cleaned.xlsx"
OUT_DIR = Path("reports") / "project2"
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    raise SystemExit(f"Cleaned file not found: {DATA_PATH}. Run Project 1 cleaning first.")

df = pd.read_excel(DATA_PATH)

# ---- Basic overview ----
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

basic = {
    "rows": int(len(df)),
    "cols": int(df.shape[1]),
    "full_row_duplicates": int(df.duplicated().sum()),
    "total_missing_cells": int(df.isna().sum().sum()),
    "invalid_dates_after_parse": int(df["Date"].isna().sum()),
}
print("BASIC:", basic)

# ---- Numeric + Categorical columns ----
numeric_cols = ["Quantity", "UnitPrice", "ItemsInCart", "TotalPrice"]
cat_cols = [c for c in df.columns if c not in numeric_cols + ["Date"]]

# ---- Descriptive stats ----
num_summary = df[numeric_cols].describe().T
num_summary["median"] = df[numeric_cols].median()
num_summary.to_csv(OUT_DIR / "numeric_summary.csv")
print("Saved: reports/project2/numeric_summary.csv")

# ---- Top categories ----
with open(OUT_DIR / "top_categories.txt", "w", encoding="utf-8") as f:
    for c in cat_cols:
        f.write(f"\n=== {c} (top 10) ===\n")
        vc = df[c].astype("string").fillna("MISSING").value_counts().head(10)
        f.write(vc.to_string())
        f.write("\n")
print("Saved: reports/project2/top_categories.txt")

# ---- Monthly trends ----
monthly = (
    df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
      .groupby("Month")
      .agg(Orders=("OrderID", "count"), Revenue=("TotalPrice", "sum"))
      .reset_index()
)
monthly.to_csv(OUT_DIR / "monthly_trend.csv", index=False)
print("Saved: reports/project2/monthly_trend.csv")

plt.figure(figsize=(10,5))
sns.lineplot(data=monthly, x="Month", y="Revenue", marker="o")
plt.title("Monthly Revenue Trend")
plt.tight_layout()
plt.savefig(FIG_DIR / "monthly_revenue_trend.png", dpi=200)
plt.close()

plt.figure(figsize=(10,5))
sns.lineplot(data=monthly, x="Month", y="Orders", marker="o", color="orange")
plt.title("Monthly Orders Trend")
plt.tight_layout()
plt.savefig(FIG_DIR / "monthly_orders_trend.png", dpi=200)
plt.close()

# ---- Top products by revenue ----
top_products = (df.groupby("Product", as_index=False)
                  .agg(Revenue=("TotalPrice", "sum"), Orders=("OrderID", "count"))
                  .sort_values("Revenue", ascending=False)
                  .head(10))
top_products.to_csv(OUT_DIR / "top_products.csv", index=False)

plt.figure(figsize=(10,5))
sns.barplot(data=top_products, x="Revenue", y="Product")
plt.title("Top 10 Products by Revenue")
plt.tight_layout()
plt.savefig(FIG_DIR / "top_products_by_revenue.png", dpi=200)
plt.close()

# ---- Distributions + boxplots ----
for c in numeric_cols:
    plt.figure(figsize=(8,4))
    sns.histplot(df[c], kde=True, bins=30)
    plt.title(f"Distribution: {c}")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"dist_{c}.png", dpi=200)
    plt.close()

    plt.figure(figsize=(6,3))
    sns.boxplot(x=df[c])
    plt.title(f"Boxplot: {c}")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"box_{c}.png", dpi=200)
    plt.close()

# ---- IQR outliers ----
iqr_rows = []
for c in numeric_cols:
    q1 = df[c].quantile(0.25)
    q3 = df[c].quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    out_cnt = int(((df[c] < low) | (df[c] > high)).sum())
    iqr_rows.append([c, float(low), float(high), out_cnt])

iqr_df = pd.DataFrame(iqr_rows, columns=["column", "low_bound", "high_bound", "outlier_count"])
iqr_df.to_csv(OUT_DIR / "iqr_outliers_summary.csv", index=False)
print("Saved: reports/project2/iqr_outliers_summary.csv")

# ---- Correlation ----
corr = df[numeric_cols].corr(numeric_only=True)
corr.to_csv(OUT_DIR / "correlation_matrix.csv")

plt.figure(figsize=(6,5))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Heatmap (Numeric)")
plt.tight_layout()
plt.savefig(FIG_DIR / "correlation_heatmap.png", dpi=200)
plt.close()

# ---- Simple consistency check ----
calc = df["Quantity"] * df["UnitPrice"]
diff = (df["TotalPrice"] - calc).abs()
check = {
    "max_abs_diff_TotalPrice_vs_QtyxUnitPrice": float(diff.max()),
    "mean_abs_diff": float(diff.mean()),
}
with open(OUT_DIR / "consistency_checks.txt", "w", encoding="utf-8") as f:
    f.write(str(check))
print("CHECK:", check)

# ---- Summary markdown ----
md = OUT_DIR / "eda_summary.md"
with open(md, "w", encoding="utf-8") as f:
    f.write("# Project 2: Exploratory Data Analysis (EDA)\n\n")
    f.write("## Dataset Overview\n")
    for k, v in basic.items():
        f.write(f"- {k}: {v}\n")
    f.write("\n## Files Generated\n")
    f.write("- numeric_summary.csv\n- top_categories.txt\n- monthly_trend.csv\n- top_products.csv\n")
    f.write("- iqr_outliers_summary.csv\n- correlation_matrix.csv\n- consistency_checks.txt\n")
    f.write("- figures/*.png\n")

print("EDA COMPLETE -> reports/project2/")