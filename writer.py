import pandas as pd
from src.db.connection import get_db_connection

def insert_dataframe_to_table(df: pd.DataFrame, table_name: str):
    """Inserts a cleaned dataframe into the target database table using upsert rules."""
    if df.empty:
        print(f"⚠️  No records to write for table: {table_name}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all column headers from the DataFrame
    columns = df.columns.tolist()
    
    # Exclude 'id' row metrics if generated during parsing to let SQLite manage increments
    if 'id' in columns:
        columns.remove('id')
        
    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    
    # Dynamic SQLite conflict handlers based on table constraint signatures
    if table_name == "peer_groups":
        conflict_clause = "ON CONFLICT(company_id) DO UPDATE SET peer_group_name=excluded.peer_group_name, is_benchmark=excluded.is_benchmark"
    elif table_name == "stock_prices":
        conflict_clause = "ON CONFLICT(company_id, date) DO UPDATE SET close_price=excluded.close_price, volume=excluded.volume"
    else:
        conflict_clause = "ON CONFLICT(company_id, year) DO UPDATE SET net_profit_margin_pct=excluded.net_profit_margin_pct" if table_name == "financial_ratios" else "ON CONFLICT(company_id, year) DO UPDATE SET market_cap_crore=excluded.market_cap_crore"

    insert_query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders}) {conflict_clause};"
    
    records_to_insert = []
    for _, row in df.iterrows():
        # Extrapolate values in explicit column order, converting NaN into clear None markers
        record = [None if pd.isna(row[col]) else row[col] for col in columns]
        records_to_insert.append(record)
        
    try:
        cursor.executemany(insert_query, records_to_insert)
        conn.commit()
        print(f"💾 Successfully database-synced {len(records_to_insert)} records into '{table_name}'.")
    except Exception as e:
        print(f"❌ Error inserting into {table_name}: {e}")
    finally:
        conn.close()