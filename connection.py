import os
import sqlite3

DB_DIR = "db"
DB_PATH = os.path.join(DB_DIR, "nifty100_intelligence.db")

def get_db_connection():
    """Establishes and returns a connection to the local SQLite database file."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # This enables dictionary-like row access (e.g., row['company_id'])
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Creates the structural relational schema tables for our normalized assets."""
    print(f"Initializing core database at: {DB_PATH}...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Stock Prices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL,
            date TEXT NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            close_price REAL,
            volume INTEGER,
            adjusted_close REAL,
            UNIQUE(company_id, date)
        );
    """)
    
    # 2. Create Financial Ratios Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_ratios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            net_profit_margin_pct REAL,
            operating_profit_margin_pct REAL,
            return_on_equity_pct REAL,
            debt_to_equity REAL,
            interest_coverage REAL,
            asset_turnover REAL,
            free_cash_flow_cr REAL,
            capex_cr REAL,
            earnings_per_share REAL,
            book_value_per_share REAL,
            dividend_payout_ratio_pct REAL,
            total_debt_cr REAL,
            cash_from_operations_cr REAL,
            UNIQUE(company_id, year)
        );
    """)

    # 3. Create Market Capitalization Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_cap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            market_cap_crore REAL,
            enterprise_value_crore REAL,
            pe_ratio REAL,
            pb_ratio REAL,
            ev_ebitda REAL,
            dividend_yield_pct REAL,
            UNIQUE(company_id, year)
        );
    """)

    # 4. Create Peer Groups Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS peer_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id TEXT NOT NULL UNIQUE,
            peer_group_name TEXT,
            is_benchmark INTEGER
        );
    """)
    
    conn.commit()
    conn.close()
    print("✅ All core relational database tables created successfully!")

if __name__ == "__main__":
    init_database()