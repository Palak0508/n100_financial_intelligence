import os
import pandas as pd
from src.etl.normaliser import normalize_year, normalize_ticker
from src.etl.validator import validate_dataframe
from src.etl.writer import insert_dataframe_to_table

RAW_DATA_DIR = os.path.join("data", "raw")

def load_excel_file(file_name: str) -> pd.DataFrame:
    """Reads raw data using an adaptive multi-engine strategy for modern and legacy layouts."""
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target raw file not found: {file_path}")
    
    print(f"Reading {file_name}...")
    try:
        return pd.read_excel(file_path, engine='openpyxl')
    except Exception:
        pass

    try:
        return pd.read_excel(file_path, engine='xlrd')
    except Exception:
        pass

    try:
        return pd.read_csv(file_path, on_bad_lines='skip')
    except Exception as e:
        raise ValueError(f"Could not parse binary layout structure for {file_name}: {e}")

def process_financial_file(file_name: str, ticker_col: str, year_col: str = None, is_full_date: bool = False) -> pd.DataFrame:
    """Loads a targeted data asset file and processes tracking columns via Day 1 constraints."""
    try:
        df = load_excel_file(file_name)
        df.columns = [str(col).strip() for col in df.columns]
        
        if ticker_col not in df.columns:
            possible_cols = [c for c in df.columns if 'company' in c.lower() or 'ticker' in c.lower()]
            if possible_cols:
                ticker_col = possible_cols[0]
            else:
                print(f"⚠️ Warning: Could not find ticker column '{ticker_col}' in {file_name}.")
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
            return pd.DataFrame(columns=df.columns)
            
        return pd.DataFrame(cleaned_rows)
    except Exception as e:
        print(f"❌ Error processing file {file_name}: {e}\n")
        return pd.DataFrame()

if __name__ == "__main__":
    print("🚀 Running Day 4 Master ETL Target Loading Pipeline...\n")
    
    # Clean up old validation logs before a fresh run
    failures_log_path = os.path.join("output", "validation_failures.csv")
    if os.path.exists(failures_log_path):
        os.remove(failures_log_path)
    
    # 1. Financial Ratios File ➡️ DB
    ratios = process_financial_file("financial_ratios.xlsx", ticker_col="company_id", year_col="year")
    ratios_validated = validate_dataframe(ratios, "financial_ratios.xlsx")
    insert_dataframe_to_table(ratios_validated, "financial_ratios")
    
    # 2. Market Cap File ➡️ DB
    mcap = process_financial_file("market_cap.xlsx", ticker_col="company_id", year_col="year")
    mcap_validated = validate_dataframe(mcap, "market_cap.xlsx")
    insert_dataframe_to_table(mcap_validated, "market_cap")
    
    # 3. Peer Groups File ➡️ DB
    peers = process_financial_file("peer_groups.xlsx", ticker_col="company_id", year_col=None)
    peers_validated = validate_dataframe(peers, "peer_groups.xlsx")
    insert_dataframe_to_table(peers_validated, "peer_groups")
    
    # 4. Stock Prices File ➡️ DB
    prices = process_financial_file("stock_prices.xlsx", ticker_col="company_id", year_col="date", is_full_date=True)
    prices_validated = validate_dataframe(prices, "stock_prices.xlsx")
    insert_dataframe_to_table(prices_validated, "stock_prices")
    
    print("\n🏁 Master Data Warehouse Pipeline Sync Complete!")