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

import time
import schedule
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper():
    """Run the stock analysis script"""
    try:
        logger.info("Running stock analysis...")
        subprocess.run(["python", "backend/stock_analysis.py"], check=True)
        logger.info("Stock analysis completed successfully")
    except Exception as e:
        logger.error(f"Stock analysis failed: {e}")

# Run immediately on startup
logger.info("Running initial stock analysis...")
run_scraper()

# Schedule to run every 30 minutes
schedule.every(30).minutes.do(run_scraper)

if __name__ == "__main__":
    logger.info("Scheduler started. Running every 30 minutes...")
    logger.info("Press Ctrl+C to stop")
    while True:
        schedule.run_pending()
        time.sleep(10)
