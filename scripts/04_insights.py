from pathlib import Path
import pandas as pd

OUT_TXT = Path("reports/project2/insights_output.txt")

m = pd.read_csv("reports/project2/monthly_trend.csv")
o = pd.read_csv("reports/project2/iqr_outliers_summary.csv")
p = pd.read_csv("reports/project2/top_products.csv")
corr = pd.read_csv("reports/project2/correlation_matrix.csv", index_col=0)

lines = []

lines.append("TOP 5 MONTHS BY REVENUE:")
lines.append(m.sort_values("Revenue", ascending=False).head(5).to_string(index=False))
lines.append("")

lines.append("TOP 5 MONTHS BY ORDERS:")
lines.append(m.sort_values("Orders", ascending=False).head(5).to_string(index=False))
lines.append("")

lines.append("OUTLIER COUNTS (IQR):")
lines.append(o.sort_values("outlier_count", ascending=False).to_string(index=False))
lines.append("")

lines.append("TOP 10 PRODUCTS BY REVENUE:")
lines.append(p.head(10).to_string(index=False))
lines.append("")

lines.append("CORRELATION MATRIX (numeric):")
lines.append(corr.round(2).to_string())
lines.append("")

text = "\n".join(lines)

print(text)

OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
OUT_TXT.write_text(text, encoding="utf-8")
print("\nSaved:", OUT_TXT.as_posix())