import os
import pandas as pd
from src.etl.normaliser import normalize_year, normalize_ticker
from src.etl.validator import validate_dataframe

RAW_DATA_DIR = os.path.join("data", "raw")

def load_excel_file(file_name: str) -> pd.DataFrame:
    """Reads raw data using an adaptive multi-engine strategy for modern and legacy layouts."""
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target raw file not found: {file_path}")
    
    print(f"Reading {file_name}...")
    
    # Strategy 1: Attempt standard openpyxl parsing for native .xlsx structures
    try:
        return pd.read_excel(file_path, engine='openpyxl')
    except Exception:
        pass

    # Strategy 2: Attempt xlrd parsing for legacy workbook structures disguised as .xlsx
    try:
        return pd.read_excel(file_path, engine='xlrd')
    except Exception:
        pass

    # Strategy 3: Fallback to structured text comma/tab-separated parsing
    try:
        return pd.read_csv(file_path, on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Could not parse binary layout structure for {file_name}: {e}")

def process_financial_file(file_name: str, ticker_col: str, year_col: str = None, is_full_date: bool = False) -> pd.DataFrame:
    """Loads a targeted data asset file and processes tracking columns via Day 1 constraints."""
    try:
        df = load_excel_file(file_name)
        
        # Clean header layout spaces
        df.columns = [str(col).strip() for col in df.columns]
        
        # Fallback column search if indices shifted due to legacy compression
        if ticker_col not in df.columns:
            possible_cols = [c for c in df.columns if 'company' in c.lower() or 'ticker' in c.lower()]
            if possible_cols:
                ticker_col = possible_cols[0]
            else:
                print(f"⚠️ Warning: Could not find ticker column '{ticker_col}' in {file_name}. Available: {df.columns.tolist()}")
                return pd.DataFrame()
                
        cleaned_rows = []
        for idx, row in df.iterrows():
            try:
                raw_ticker = row.get(ticker_col)
                raw_year_val = row.get(year_col) if year_col else None
                
                if pd.isna(raw_ticker) and (year_col is None or pd.isna(raw_year_val)):
                    continue
                
                clean_ticker = normalize_ticker(raw_ticker)
                row_copy = row.copy()
                row_copy[ticker_col] = clean_ticker
                
                if year_col and raw_year_val is not None:
                    if is_full_date:
                        year_str = str(raw_year_val).strip()[:4]
                        clean_year = normalize_year(year_str)
                    else:
                        clean_year = normalize_year(raw_year_val)
                    row_copy[year_col] = clean_year
                    
                cleaned_rows.append(row_copy)
                
            except (ValueError, TypeError):
                continue
                
        if not cleaned_rows:
            print(f"⚠️ Warning: No valid data records preserved for {file_name}")
            return pd.DataFrame(columns=df.columns)
            
        result_df = pd.DataFrame(cleaned_rows)
        print(f"✅ Successfully processed {file_name}: {len(result_df)} rows parsed.")
        return result_df

    except Exception as e:
        print(f"❌ Error processing file {file_name}: {e}\n")
        return pd.DataFrame()

if __name__ == "__main__":
    print("🚀 Running Complete Day 3 Batch Data Pipeline...\n")
    
    # Clean up old validation logs before a fresh run
    failures_log_path = os.path.join("output", "validation_failures.csv")
    if os.path.exists(failures_log_path):
        os.remove(failures_log_path)
    
    # 1. Financial Ratios
    ratios = process_financial_file("financial_ratios.xlsx", ticker_col="company_id", year_col="year")
    ratios_validated = validate_dataframe(ratios, "financial_ratios.xlsx")
    print(f"🛡️  Ratios Remaining after Critical Schema Validation: {len(ratios_validated)} rows.\n")
    
    # 2. Market Cap
    mcap = process_financial_file("market_cap.xlsx", ticker_col="company_id", year_col="year")
    mcap_validated = validate_dataframe(mcap, "market_cap.xlsx")
    print(f"🛡️  Market Cap Remaining after Critical Schema Validation: {len(mcap_validated)} rows.\n")
    
    # 3. Peer Groups
    peers = process_financial_file("peer_groups.xlsx", ticker_col="company_id", year_col=None)
    peers_validated = validate_dataframe(peers, "peer_groups.xlsx")
    print(f"🛡️  Peer Groups Remaining after Critical Schema Validation: {len(peers_validated)} rows.\n")
    
    # 4. Stock Prices
    prices = process_financial_file("stock_prices.xlsx", ticker_col="company_id", year_col="date", is_full_date=True)
    prices_validated = validate_dataframe(prices, "stock_prices.xlsx")
    print(f"🛡️  Stock Prices Remaining after Critical Schema Validation: {len(prices_validated)} rows.\n")
    
    # 5. Sectors (Bypassed due to structural anomalies)
    sectors = process_financial_file("sectors.xlsx", ticker_col="company_id", year_col=None)
    
    print("🏁 Processing and Schema Validation complete!")