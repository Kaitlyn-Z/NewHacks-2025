"""
Module for processing stock alerts using pre-scraped stock data
from stock_data_scraping.py. Creates sqlite3 tables for latest 
and active alerts in alerts.db.
"""

import ta
import sqlite3
import pandas as pd
from datetime import datetime
from notifier import send_alert_email
from stock_data_scraping import fetch_stock_data


def prepare_stock_data(tickers, days):
    """
    Use stock_data_scraping.py's fetch_stock_data to get data.
    Calculates volume_z, Volume_Ratio, Volume_Alert, and RSI.
    Returns processed DataFrame.
    """
    # Fetch data from stock_data_scraping.py
    data = fetch_stock_data(tickers, days)

    # Volume z-score
    data['volume_z'] = data.groupby('ticker')['volume'].transform(
        lambda x: (x - x.rolling(50).mean()) / x.rolling(50).std()
    )

    # Volume ratio
    data['Volume_Ratio'] = data['volume'] / data.groupby('ticker')['volume'].transform('mean')

    # Classify alerts
    data['Volume_Alert'] = data['volume_z'].apply(classify_alert)

    # RSI
    data['RSI'] = data.groupby('ticker')['close'].transform(lambda x: compute_rsi(x))

    # Add timestamp
    data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return data


def classify_alert(z):
    """Classify volume z-score into alert levels."""
    if pd.isna(z):
        return 'No data'
    elif z >= 4:
        return 'High Alert'
    elif z >= 2.5:
        return 'Medium Alert'
    elif z >= 1.5:
        return 'Low Alert'
    else:
        return 'Normal'


def compute_rsi(series, window=14):
    """Compute RSI for a series."""
    rsi = ta.momentum.RSIIndicator(close=series, window=window).rsi()
    return rsi.reindex(series.index, fill_value=None)


def get_latest_alerts(data, alert_threshold_z=1.5):
    """
    Extract the latest alerts per ticker based on volume z-score threshold.
    Returns two DataFrames: latest overall, active alerts only.
    """
    latest = data.groupby('ticker').tail(1)[
        ['ticker', 'close', 'volume', 'volume_z', 'Volume_Ratio', 'Volume_Alert', 'RSI', 'Timestamp']
    ]

    active_alerts = latest[latest['volume_z'] >= alert_threshold_z].copy()
    active_alerts['Trigger_Volume'] = active_alerts['volume']

    return latest, active_alerts


def setup_database(db_path="backend/alerts.db"):
    """Create database tables if they don't exist."""
    with sqlite3.connect(db_path) as conn:
        # Create latest_alerts table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS latest_alerts (
                Ticker TEXT PRIMARY KEY,
                Close REAL,
                Volume INTEGER,
                volume_z REAL,
                Volume_Ratio REAL,
                Volume_Alert TEXT,
                RSI REAL,
                Timestamp TEXT
            )
        """)

        # Create active_alerts table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS active_alerts (
                Ticker TEXT PRIMARY KEY,
                Alert_Level TEXT,
                Trigger_Volume REAL,
                Timestamp TEXT
            )
        """)


def update_active_alerts(data, active_alerts_new, db_path="backend/alerts.db", volume_tolerance=1.5):
    """Update active alerts table in database. Returns newly added tickers."""
    newly_added = []
    with sqlite3.connect(db_path) as conn:
        existing_alerts = pd.read_sql_query("SELECT * FROM active_alerts", conn)
        existing_tickers = set(existing_alerts['Ticker']) if not existing_alerts.empty else set()

        # Remove alerts below tolerance
        for _, row in existing_alerts.iterrows():
            ticker_data = active_alerts_new[active_alerts_new['ticker'] == row['Ticker']]
            if ticker_data.empty:
                current_vol = data[data['ticker'] == row['Ticker']].iloc[-1]['volume']
                if current_vol < row['Trigger_Volume'] * volume_tolerance:
                    conn.execute("DELETE FROM active_alerts WHERE Ticker=?", (row['Ticker'],))

        # Add/update new alerts
        for _, row in active_alerts_new.iterrows():
            if row['ticker'] not in existing_tickers:
                newly_added.append(row['ticker'])
            conn.execute("""
                REPLACE INTO active_alerts (Ticker, Alert_Level, Trigger_Volume, Timestamp)
                VALUES (?, ?, ?, ?)
            """, (row['ticker'], row['Volume_Alert'], row['Trigger_Volume'], row['Timestamp']))

    return newly_added


def send_new_alert_emails(active_alerts_new, newly_added, db_path="backend/alerts.db"):
    """Send emails to users for newly added alerts only."""
    if not newly_added:
        return

    with sqlite3.connect(db_path) as conn:
        users = conn.execute("SELECT email, alerts FROM user_prefs").fetchall()

    for email, alerts_str in users:
        alert_list = alerts_str.split(",")
        user_alerts = active_alerts_new[
            (active_alerts_new['ticker'].isin(newly_added)) &
            (active_alerts_new['Volume_Alert'].isin(alert_list))
        ]
        for _, row in user_alerts.iterrows():
            send_alert_email(
                to_email=email,
                ticker=row['ticker'],
                alert=row['Volume_Alert'],
                rsi=row['RSI'],
                timestamp=row['Timestamp'],
                price=row['close'],
                volume=row['Trigger_Volume'],
                volume_ratio=1.0
            )


def update_latest_alerts_table(active_alerts_new, db_path="backend/alerts.db"):
    """Update the latest_alerts table for dashboard display."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM latest_alerts")
        for _, row in active_alerts_new.iterrows():
            conn.execute("""
                INSERT INTO latest_alerts 
                (Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['ticker'], row['close'], row['Trigger_Volume'], row['volume_z'],
                row['Volume_Ratio'], row['Volume_Alert'], row['RSI'], row['Timestamp']
            ))


# For testing
def main():
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]
    setup_database()
    data = prepare_stock_data(tickers, days=1)
    latest, active_alerts_new = get_latest_alerts(data)
    newly_added = update_active_alerts(data, active_alerts_new)
    send_new_alert_emails(active_alerts_new, newly_added)
    update_latest_alerts_table(active_alerts_new)
    print("Alerts processed successfully.")


if __name__ == "__main__":
    main()
