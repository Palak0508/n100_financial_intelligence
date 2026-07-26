# Nifty 100 Financial Intelligence Platform

## Day 1: Project Environment Setup, Repository Architecture, and Core Test Verification

### Description
Established the localized workspace structure and initialized the module architecture for the Nifty 100 Financial Intelligence Platform. Configured an isolated Python virtual environment (`venv`) to eliminate dependency conflicts, resolved package configuration manifests, and successfully installed core data engineering frameworks (`pandas`, `openpyxl`, `pytest`). Verified system integrity by executing the comprehensive unit testing pipeline, which returned a flawless execution report with 35/35 passing tests, confirming that all core modules and validation rules are fully functional.

---

### How to Setup & Run

1. **Activate the Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
  
## Day 2: Batch Excel Data Loader Pipeline and Normalization Integration

### Description
Successfully built and deployed the robust batch extraction and loading framework (`loader.py`) within the `src/etl/` module architecture. The Day 2 pipeline dynamically interfaces with the workspace file system to scan, ingest, and process incoming dirty financial asset spreadsheets stored under `data/raw/`. 

The loading engine seamlessly connects with our Day 1 data normalizers, feeding raw tracking fields through the validated `normalize_ticker()` and `normalize_year()` core rules. Designed with high-performance operational resilience, the parser is engineered with multi-format fallback strategies capable of dynamically adapting to modern openpyxl structures, text formats, and handling legacy structural corruptions without breaking execution.

### Key Milestones Achieved
* **Dynamic Multi-File Ingestion:** Engineered automated matching paths to safely ingest variations across different files simultaneously (e.g., matching standard `year` labels alongside full `date` parameters).
* **Fault-Tolerant Parsing Strategy:** Configured structural fallback guards to intercept anomalies, skip uneven data lines, and bypass empty layout records gracefully.
* **Pipeline Validation Counts:**
  * `financial_ratios.xlsx` ➡️ **1,184 rows** processed and cleaned successfully.
  * `market_cap.xlsx` ➡️ **552 rows** processed and cleaned successfully.
  * `peer_groups.xlsx` ➡️ **56 rows** processed and cleaned successfully.
  * `stock_prices.xlsx` ➡️ **5,520 rows** processed and cleaned successfully.
  * Robust system error handling automatically logged and isolated corrupted schema exceptions for structural anomalies (`sectors.xlsx`).

### How to Run the Data Loader

1. **Activate the Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1

   ## Day 3: Schema Validation & Data Quality (DQ) Rules Integration

### Description
Developed and integrated a highly resilient Data Quality checking framework (`validator.py`) within the `src/etl/` module path. This verification layer actively intercepts dataframes generated from the file loading layers and inspects them against **16 strict structural and boundary constraint metrics** before letting them continue down the data channel.

The validator handles processing in two sequential categories:
1. **CRITICAL Evaluation:** Drops corrupt or completely empty row matrices missing structural identities (like a missing `company_id` or absent timeline parameters) to safeguard down-stream code stability.
2. **WARNING Isolation:** Runs soft threshold boundaries to flag suspicious financial indicators (such as negative prices, operational profit margins scaling past 100%, or empty volume blocks) without dropping the row from the workflow.

Anomalous anomalies caught during checking routines are extracted and automatically exported directly into an isolated, timestamped persistent reporting file: `output/validation_failures.csv`.

### Key Milestones Achieved
* **Dual-Tiered Processing Logic:** Separated hard system crash limits from logical outlier checks across 16 different criteria.
* **Automated Data Quality Audit Logs:** Programmed a persistent error logging module to dump operational audit trails for troubleshooting records.
* **Pipeline Output Volume Metrics:**
  * `financial_ratios.xlsx` ➡️ **1,184 rows** verified and passed downstream.
  * `market_cap.xlsx` ➡️ **552 rows** verified and passed downstream.
  * `peer_groups.xlsx` ➡️ **56 rows** verified and passed downstream.
  * `stock_prices.xlsx` ➡️ **5,520 rows** verified and passed downstream.

### File Structure Reference
```text
n100_financial_intelligence/
├── src/
│   └── etl/
│       ├── loader.py       # Main pipeline processor
│       ├── normaliser.py   # Day 1 rules
│       └── validator.py    # Day 3 validation logic
└── output/
    └── validation_failures.csv  # Auto-generated anomaly report

## Day 4: Relational Database Storage & Idempotent Upsert Pipeline

### Description
Configured a persistent database architectural layer using a local SQLite instance to warehouse our refined datasets. Designed an isolated ingestion pipeline (`writer.py`) that utilizes high-performance batch insert statements (`executemany`) to drastically maximize system transactional speeds. To guarantee absolute data consistency across incremental or recurring pipeline execution windows, we integrated custom idempotent syntax (`ON CONFLICT DO UPDATE`), protecting relational identity rules across tickers, years, and calendar timelines.

### Data Warehouse Summary Metrics
* **Financial Ratios Sync:** Successfully committed **1,184 clean rows** into the database.
* **Market Capitalization Sync:** Successfully committed **552 clean rows** into the database.
* **Peer Group Configurations Sync:** Successfully committed **56 clean rows** into the database.
* **Stock Price Matrix Timelines Sync:** Successfully committed **5,520 clean rows** into the database.

---

## Day 5: Analytical SQL Views & Business Intelligence Query Engine

### Description
Developed an automated feature engineering and analytics module (`queries.py`) within the `src/analytics/` package directory. Built persistent, reusable SQL Views inside the database to aggregate key financial performance indicators. Programmed window functions (`LAG()` and `OVER(PARTITION BY...)`) to calculate Year-over-Year (YoY) profit margin growth trajectories and compute company-specific performance benchmarks against sector peer group averages. Added aggregate stock price profiling to evaluate trading volume histories, multi-period price bounds, and historical averages across tracked assets.

### How to Setup & Run
1. Generate Analytical SQL Views and Run Summary Query Suite:
   ```powershell
   python -m src.analytics.queries
