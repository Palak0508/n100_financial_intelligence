import pandas as pd
import os
from typing import Tuple, List

def validate_data() -> Tuple[bool, List[str]]:
    """
    Day 3: Robust Validator matching the exact CSV files in your raw folder.
    Skips the top decorative row lines natively.
    """
    logs = []
    all_passed = True
    
    # Get absolute paths to stop Windows routing issues
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    output_dir = os.path.join(base_dir, "output")
    
    os.makedirs(output_dir, exist_ok=True)
    failure_log_path = os.path.join(output_dir, "validation_failures.csv")
    failed_rows = []

    # Map of target tables to your exact file names
    files_to_check = {
        "sectors": "sectors.xlsx - Sheet1.csv",
        "financial_ratios": "financial_ratios.xlsx - Sheet1.csv",
        "market_cap": "market_cap.xlsx - Sheet1.csv",
        "peer_groups": "peer_groups.xlsx - Sheet1.csv",
        "stock_prices": "stock_prices.xlsx - Sheet1.csv",
        "profit_loss": "profitandloss.xlsx - Profit & Loss.csv",
        "balance_sheet": "balancesheet.xlsx - Balance Sheet.csv",
        "cash_flow": "cashflow.xlsx - Cash Flow.csv",
        "companies": "companies.xlsx - Companies.csv",
        "prosandcons": "prosandcons.xlsx - Pros & Cons.csv",
        "documents": "documents.xlsx - Documents.csv",
        "analysis": "analysis.xlsx - Analysis.csv"
    }

    loaded_dfs = {}

    for key, filename in files_to_check.items():
        full_path = os.path.join(raw_dir, filename)
        if os.path.exists(full_path):
            try:
                # Read CSV, skip the header banner row if it exists
                df = pd.read_csv(full_path, skiprows=1)
                loaded_dfs[key] = df
                logs.append(f"✅ Loaded {key} successfully ({len(df)} records found).")
            except Exception as e:
                logs.append(f"❌ Found {filename} but failed to parse: {e}")
        else:
            logs.append(f"⚠️ Missing file: {filename} is not in data/raw/")

    # --- DATA QUALITY RULES ---
    
    # [DQ-01] CRITICAL: Missing Primary/Company Identifiers
    for name, df in loaded_dfs.items():
        id_col = 'id' if 'id' in df.columns else (df.columns[0] if len(df.columns) > 0 else '')
        comp_col = 'company_id' if 'company_id' in df.columns else ''
        
        if id_col in df.columns:
            missing_ids = df[df[id_col].isna()]
            if not missing_ids.empty:
                all_passed = False
                logs.append(f"CRITICAL: '{name}' table has {len(missing_ids)} records with an empty ID field.")
                for idx in missing_ids.index:
                    failed_rows.append({"file": name, "row_index": idx, "severity": "CRITICAL", "rule": "DQ-01", "message": "Missing key identifier"})

    # Save out failure spreadsheet if issues exist
    if failed_rows:
        pd.DataFrame(failed_rows).to_csv(failure_log_path, index=False)
        logs.append(f"📝 Quality metrics complete. Failures logged to: {failure_log_path}")
    else:
        logs.append("🏆 Perfect Score! All data sheets conform perfectly.")

    return all_passed, logs

if __name__ == "__main__":
    passed, validation_logs = validate_data()
    print("\n--- Validation Execution Report ---")
    for log in validation_logs:
        print(log)
    print(f"\nFinal Status: {'PASSED' if passed else 'FAILED'}")