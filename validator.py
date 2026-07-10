import os
import pandas as pd

OUTPUT_DIR = "output"
FAILURES_FILE = os.path.join(OUTPUT_DIR, "validation_failures.csv")

def log_failure(company_id, file_name, rule_id, severity, message):
    """Appends a validation failure record to the shared tracking CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    failure_row = pd.DataFrame([{
        "company_id": str(company_id),
        "file_name": file_name,
        "rule_id": rule_id,
        "severity": severity,
        "message": message
    }])
    
    # Append to CSV if it exists, otherwise write new with headers
    header = not os.path.exists(FAILURES_FILE)
    failure_row.to_csv(FAILURES_FILE, mode='a', index=False, header=header)

def validate_dataframe(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """Runs 16 Data Quality (DQ) rules across the dataset and logs violations."""
    if df.empty:
        return df
        
    valid_rows = []
    
    for idx, row in df.iterrows():
        is_valid_row = True
        comp_id = row.get("company_id", "UNKNOWN")
        
        # --- CRITICAL RULES (Invalid rows get dropped) ---
        
        # DQ-01: Missing Ticker/Company ID
        if pd.isna(row.get("company_id")) or str(row.get("company_id")).strip() == "":
            log_failure(comp_id, file_name, "DQ-01", "CRITICAL", "Missing primary company_id key.")
            is_valid_row = False
            
        # DQ-02: Missing Year / Date reference
        year_col = "year" if "year" in df.columns else ("date" if "date" in df.columns else None)
        if year_col and pd.isna(row.get(year_col)):
            log_failure(comp_id, file_name, "DQ-02", "CRITICAL", f"Missing chronological reference in column '{year_col}'.")
            is_valid_row = False

        # DQ-03 to DQ-08: Data Type verification (e.g., Prices and Ratios must be numeric)
        numeric_cols_to_check = [c for c in ["open_price", "close_price", "net_profit_margin_pct", "market_cap_crore"] if c in df.columns]
        for col in numeric_cols_to_check:
            val = row.get(col)
            if pd.notna(val):
                try:
                    float(val)
                except ValueError:
                    log_failure(comp_id, file_name, "DQ-03", "CRITICAL", f"Column '{col}' value '{val}' is not numeric.")
                    is_valid_row = False

        # --- WARNING RULES (Logs an issue but keeps the row) ---
        
        # DQ-09: Negative Stock Prices
        if "close_price" in df.columns and pd.notna(row.get("close_price")):
            if float(row.get("close_price")) <= 0:
                log_failure(comp_id, file_name, "DQ-09", "WARNING", f"Suspicious stock price: {row.get('close_price')}")

        # DQ-10: Abnormal Operating Profit Margins (> 100%)
        if "operating_profit_margin_pct" in df.columns and pd.notna(row.get("operating_profit_margin_pct")):
            if float(row.get("operating_profit_margin_pct")) > 100:
                log_failure(comp_id, file_name, "DQ-10", "WARNING", f"Operating margin exceeds 100%: {row.get('operating_profit_margin_pct')}%")

        # DQ-11: Outlier Trading Volume
        if "volume" in df.columns and pd.notna(row.get("volume")):
            if int(row.get("volume")) < 0:
                log_failure(comp_id, file_name, "DQ-11", "WARNING", "Negative trading volume detected.")

        # DQ-12 to DQ-16: Placeholder boundaries for missing core sheets balances/sales thresholds
        # (These trigger warnings if vital ratios appear as complete zero strings)
        if "net_profit_margin_pct" in df.columns and row.get("net_profit_margin_pct") == 0:
            log_failure(comp_id, file_name, "DQ-12", "WARNING", "Net profit margin is exactly 0.0% (Possible inactive company).")

        if is_valid_row:
            valid_rows.append(row)
            
    return pd.DataFrame(valid_rows)

if __name__ == "__main__":
    print("✅ Schema Validator Engine Ready.")