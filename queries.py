import sqlite3
from src.db.connection import get_db_connection

def create_analytics_views():
    """Creates persistent SQL Views for business intelligence analysis."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # View 1: YoY Profit Margin Analysis
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS view_profit_margin_yoy AS
        SELECT 
            company_id,
            year,
            net_profit_margin_pct,
            LAG(net_profit_margin_pct) OVER (PARTITION BY company_id ORDER BY year) as prev_year_margin,
            ROUND(net_profit_margin_pct - LAG(net_profit_margin_pct) OVER (PARTITION BY company_id ORDER BY year), 2) as margin_change_yoy
        FROM financial_ratios;
    """)

    # View 2: Peer Group Performance Benchmark Comparison
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS view_peer_group_benchmark AS
        SELECT 
            p.peer_group_name,
            f.company_id,
            f.year,
            f.net_profit_margin_pct,
            ROUND(AVG(f.net_profit_margin_pct) OVER (PARTITION BY p.peer_group_name, f.year), 2) as peer_avg_margin,
            ROUND(f.net_profit_margin_pct - AVG(f.net_profit_margin_pct) OVER (PARTITION BY p.peer_group_name, f.year), 2) as performance_vs_peers
        FROM financial_ratios f
        JOIN peer_groups p ON f.company_id = p.company_id;
    """)

    # View 3: Stock Price Summary & Volatility
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS view_stock_price_summary AS
        SELECT 
            company_id,
            COUNT(date) as total_trading_days,
            ROUND(AVG(close_price), 2) as avg_close_price,
            ROUND(MIN(close_price), 2) as min_close_price,
            ROUND(MAX(close_price), 2) as max_close_price,
            SUM(volume) as total_volume
        FROM stock_prices
        GROUP BY company_id;
    """)

    conn.commit()
    conn.close()
    print("✅ All Day 5 Analytical SQL Views created successfully!")

def run_analytics_summary():
    """Fetches and displays summary intelligence from the newly created views."""
    conn = get_db_connection()
    
    print("\n📊 --- TOP PERFORMING COMPANIES VS PEER AVERAGE ---")
    query_peers = """
        SELECT company_id, peer_group_name, year, net_profit_margin_pct, peer_avg_margin, performance_vs_peers 
        FROM view_peer_group_benchmark 
        WHERE performance_vs_peers > 0 
        LIMIT 5;
    """
    peers_df = conn.execute(query_peers).fetchall()
    for row in peers_df:
        print(f"Company: {row['company_id']} | Peer Group: {row['peer_group_name']} | Margin: {row['net_profit_margin_pct']}% (vs Peer Avg: {row['peer_avg_margin']}%)")

    print("\n📈 --- STOCK PRICE AGGREGATE SUMMARY (SAMPLE) ---")
    query_stocks = "SELECT * FROM view_stock_price_summary LIMIT 5;"
    stocks_df = conn.execute(query_stocks).fetchall()
    for row in stocks_df:
        print(f"Company: {row['company_id']} | Days Traded: {row['total_trading_days']} | Avg Price: ₹{row['avg_close_price']}")

    conn.close()

if __name__ == "__main__":
    create_analytics_views()
    run_analytics_summary()