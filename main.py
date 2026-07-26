import sys
import time
from src.db.connection import init_database
from src.etl.loader import process_financial_file, validate_dataframe, insert_dataframe_to_table
from src.analytics.queries import create_analytics_views, run_analytics_summary

def run_end_to_end_pipeline():
    """Master orchestrator to execute DB setup, ETL processing, and analytics views generation."""
    start_time = time.time()
    print("==================================================")
    print("🚀 STARTING NIFTY 100 MASTER DATA PIPELINE SLOTS")
    print("==================================================\n")

    # Phase 1: Database Setup
    print("🔹 Phase 1: Initializing Target Relational Database Schema...")
    init_database()
    
    # Phase 2: ETL Batch Ingestion & Validation
    print("\n🔹 Phase 2: Running ETL Ingestion & Schema Validation...")
    
    # Ratios
    ratios = process_financial_file("financial_ratios.xlsx", ticker_col="company_id", year_col="year")
    ratios_valid = validate_dataframe(ratios, "financial_ratios.xlsx")
    insert_dataframe_to_table(ratios_valid, "financial_ratios")
    
    # Market Cap
    mcap = process_financial_file("market_cap.xlsx", ticker_col="company_id", year_col="year")
    mcap_valid = validate_dataframe(mcap, "market_cap.xlsx")
    insert_dataframe_to_table(mcap_valid, "market_cap")
    
    # Peer Groups
    peers = process_financial_file("peer_groups.xlsx", ticker_col="company_id", year_col=None)
    peers_valid = validate_dataframe(peers, "peer_groups.xlsx")
    insert_dataframe_to_table(peers_valid, "peer_groups")
    
    # Stock Prices
    prices = process_financial_file("stock_prices.xlsx", ticker_col="company_id", year_col="date", is_full_date=True)
    prices_valid = validate_dataframe(prices, "stock_prices.xlsx")
    insert_dataframe_to_table(prices_valid, "stock_prices")

    # Phase 3: Business Intelligence & SQL Analytics Generation
    print("\n🔹 Phase 3: Rebuilding Analytical SQL Views & Summary Metrics...")
    create_analytics_views()
    run_analytics_summary()

    elapsed = round(time.time() - start_time, 2)
    print("\n==================================================")
    print(f"✅ PIPELINE EXECUTION COMPLETE IN {elapsed} SECONDS")
    print("==================================================")

if __name__ == "__main__":
    run_end_to_end_pipeline()