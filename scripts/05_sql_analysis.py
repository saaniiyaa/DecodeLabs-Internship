import sqlite3
import pandas as pd
from pathlib import Path

# Paths setup
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data_raw" / "week3" / "Dataset for Data Analytics (2).xlsx"
REPORTS_DIR = BASE_DIR / "reports" / "week3"
SQL_DIR = BASE_DIR / "sql"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)

print("Reading Excel dataset into memory...")
df = pd.read_excel(RAW_DATA_PATH)

# Ingest into in-memory SQLite database
conn = sqlite3.connect(":memory:")
df.to_sql("orders", conn, index=False, if_exists="replace")

# Query 1: Product Performance (COUNT, SUM, AVG, GROUP BY, ORDER BY)
query_products = """-- Query 1: Product Performance Analysis
SELECT 
    Product,
    COUNT(OrderID) AS total_orders,
    SUM(Quantity) AS total_quantity_sold,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(TotalPrice), 2) AS avg_order_value
FROM orders
GROUP BY Product
ORDER BY total_revenue DESC;"""

# Query 2: Payment Methods Analysis (WHERE filter for completed orders)
query_payments = """-- Query 2: Valid Payment Methods Analysis (Excluding Cancelled)
SELECT 
    PaymentMethod,
    COUNT(OrderID) AS valid_orders,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(UnitPrice), 2) AS avg_unit_price
FROM orders
WHERE OrderStatus != 'Cancelled'
GROUP BY PaymentMethod
ORDER BY total_revenue DESC;"""

# Query 3: High-Performing Referral Channels (HAVING clause filter)
query_referrals = """-- Query 3: High-Value Referral Channels (Threshold > 200,000)
SELECT 
    ReferralSource,
    COUNT(OrderID) AS total_orders,
    ROUND(SUM(TotalPrice), 2) AS total_revenue,
    ROUND(AVG(TotalPrice), 2) AS avg_revenue_per_order
FROM orders
GROUP BY ReferralSource
HAVING total_revenue > 200000
ORDER BY total_revenue DESC;"""

# Save standalone SQL queries to sql/ directory
with open(SQL_DIR / "project3_queries.sql", "w", encoding="utf-8") as f:
    f.write(query_products + "\n\n" + query_payments + "\n\n" + query_referrals)

print("Executing SQL queries...")
df_prod = pd.read_sql(query_products, conn)
df_pay = pd.read_sql(query_payments, conn)
df_ref = pd.read_sql(query_referrals, conn)

# Export results to CSV reports
df_prod.to_csv(REPORTS_DIR / "product_performance.csv", index=False)
df_pay.to_csv(REPORTS_DIR / "payment_analysis.csv", index=False)
df_ref.to_csv(REPORTS_DIR / "referral_insights.csv", index=False)

conn.close()

print("\n--- QUERY 1 RESULTS: Product Performance ---")
print(df_prod.to_string(index=False))

print("\n--- QUERY 2 RESULTS: Payment Methods (Non-Cancelled) ---")
print(df_pay.to_string(index=False))

print("\n--- QUERY 3 RESULTS: Referral Sources (HAVING Revenue > 200k) ---")
print(df_ref.to_string(index=False))

print(f"\nAll reports and SQL script successfully saved to {REPORTS_DIR} and {SQL_DIR}.")