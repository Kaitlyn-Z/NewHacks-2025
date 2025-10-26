# backend/update_alerts.py
import sqlite3
from backend.stock_analysis import run_alert_pipeline
from signals.hotstocks.cli import load_config, get_hot_tickers

def main():
    cfg = load_config("signals/hotstocks/config.local.json")
    tickers = get_hot_tickers(cfg)
    if not tickers:
        print("No trending tickers found.")
        return
    active_alerts_df = run_alert_pipeline(tickers, days=1)
    if active_alerts_df.empty:
        print("No active alerts generated.")
        return
    conn = sqlite3.connect("backend/alerts.db")
    active_alerts_df.to_sql("latest_alerts_dashboard", conn, if_exists="replace", index=False)
    conn.close()
    print("Active alerts updated for dashboard.")

if __name__ == "__main__":
    main()
