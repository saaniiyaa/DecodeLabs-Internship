# DecodeLabs Data Analytics Internship

This repository contains the end-to-end implementation of foundational data analytics workflows developed during the DecodeLabs Internship. The project is structured across automated data auditing, cleaning/normalization, and exploratory data analysis (EDA) with statistical outlier detection.

---

## Repository Structure

```text
├── scripts/
│   ├── 01_audit.py        # Validates schema, integrity, duplicate IDs, missing values
│   ├── 02_clean.py        # Cleans formatting, normalizes columns, outputs audit log
│   ├── 03_eda.py          # Summary statistics, monthly trends, correlation matrices
│   └── 04_insights.py     # Outlier analysis (IQR), monthly revenue drivers, correlations
├── .gitignore             # Excludes raw/cleaned datasets, logs, virtual environments
└── README.md