"""
Scheduler for Stock Analysis
-----------------------------
This runs stock_analysis.py every 30 minutes to:
1. Fetch stock data (mock or real from web scraping)
2. Calculate RSI, volume metrics, sentiment
3. Update alerts.db database
4. Send emails to users based on their preferences

The integrated_backend.py API will automatically read from this database.

Usage:
    python backend/scheduler.py

Note: Run this in the background or as a separate service.
"""

# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from backend.stock_analysis import run_alert_pipeline  # your function that creates the DataFrame
import sqlite3

def update_alerts():
    print("Running alert pipeline...")
    df = run_alert_pipeline(days=1)  # or whatever params you want

    # Save to database
    conn = sqlite3.connect("backend/alerts.db")
    df.to_sql("active_alerts", conn, if_exists="replace", index=False)
    conn.close()
    print("Active alerts updated!")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    # Schedule update every 10 minutes (adjust as needed)
    scheduler.add_job(update_alerts, 'interval', minutes=10)
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")

    # Keep the script running
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
