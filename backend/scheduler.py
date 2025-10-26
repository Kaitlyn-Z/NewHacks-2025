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
from backend.update_alerts import main as update_alerts_main
import time

def scheduled_job():
    print("Running scheduled alert pipeline...")
    update_alerts_main()

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_job, 'interval', minutes=10)
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")