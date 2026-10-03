# DecodeLabs Data Analytics Internship

This repository contains the end-to-end implementation of foundational data analytics workflows developed during the DecodeLabs Internship. The project encompasses automated data auditing, data cleaning and normalization, exploratory data analysis (EDA), and relational SQL analytics.

---

## Repository Structure

```text
├── scripts/
│   ├── 01_audit.py        # Validates schema, integrity, duplicate IDs, missing values
│   ├── 02_clean.py        # Cleans formatting, normalizes columns, outputs audit log
│   ├── 03_eda.py          # Summary statistics, monthly trends, correlation matrices
│   ├── 04_insights.py     # Outlier analysis (IQR), monthly revenue drivers, correlations
│   └── 05_sql_analysis.py # SQLite pipeline executing relational queries & exporting reports
├── sql/
│   └── project3_queries.sql # Pure SQL queries (SELECT, WHERE, GROUP BY, HAVING, ORDER BY)
├── .gitignore             # Excludes raw/cleaned datasets, logs, virtual environments
└── README.md