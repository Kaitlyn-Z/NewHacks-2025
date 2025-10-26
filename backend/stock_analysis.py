# backend/stock_analysis.py

"""
Module for processing stock alerts using pre-scraped stock data
from web_scraped.py. Creates sqlite3 tables for latest and active alerts
in alerts.db, sends email alerts for new triggers, and updates dashboard data.
"""

# backend/stock_analysis.py
import pandas as pd
import sqlite3
import ta
from datetime import datetime
from notifier import send_alert_email
from backend.stock_data_scraping import fetch_stock_data
import os

# Compute absolute path to alerts.db relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "alerts.db")

def classify_alert(z: float) -> str:
    if pd.isna(z): return 'No data'
    elif z >= 4: return 'High Alert'
    elif z >= 2.5: return 'Medium Alert'
    elif z >= 1.5: return 'Low Alert'
    else: return 'Normal'

def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    rsi = ta.momentum.RSIIndicator(close=series, window=window).rsi()
    return rsi.reindex(series.index, fill_value=None)

def prepare_stock_data(tickers_list, days=1) -> pd.DataFrame:
    data_frames = []
    for t in tickers_list:
        df = fetch_stock_data([t], days)
        if df.empty: continue
        df['Ticker'] = t
        data_frames.append(df)
    if not data_frames: return pd.DataFrame()
    data = pd.concat(data_frames, ignore_index=True)
    data['volume_z'] = data.groupby('Ticker')['Volume'].transform(
        lambda x: (x - x.rolling(50).mean()) / x.rolling(50).std()
    )
    data['Volume_Ratio'] = data['Volume'] / data.groupby('Ticker')['Volume'].transform('mean')
    data['Volume_Alert'] = data['volume_z'].apply(classify_alert)
    data['RSI'] = data.groupby('Ticker')['Close'].transform(lambda x: compute_rsi(x))
    data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data

def setup_database(db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS active_alerts (
                Ticker TEXT PRIMARY KEY,
                Alert_Level TEXT,
                Trigger_Volume REAL,
                Timestamp TEXT
            )
        """)

def get_latest_active_alerts(data: pd.DataFrame, threshold_z: float = 1.5):
    latest = data.groupby('Ticker').tail(1)[
        ['Ticker', 'Close', 'Volume', 'volume_z', 'Volume_Ratio', 'Volume_Alert', 'RSI', 'Timestamp']
    ]
    active_alerts_new = latest[latest['volume_z'] >= threshold_z].copy()
    active_alerts_new['Trigger_Volume'] = active_alerts_new['Volume']
    return latest, active_alerts_new

def update_active_alerts(data: pd.DataFrame, active_alerts_new: pd.DataFrame,
                         db_path=DB_PATH, volume_tolerance=1.5):
    newly_added = []
    with sqlite3.connect(db_path) as conn:
        existing_alerts = pd.read_sql_query("SELECT * FROM active_alerts", conn)
        existing_tickers = set(existing_alerts['Ticker']) if not existing_alerts.empty else set()
        for _, row in existing_alerts.iterrows():
            ticker_data = active_alerts_new[active_alerts_new['Ticker'] == row['Ticker']]
            if ticker_data.empty:
                current_vol = data[data['Ticker'] == row['Ticker']].iloc[-1]['Volume']
                if current_vol < row['Trigger_Volume'] * volume_tolerance:
                    conn.execute("DELETE FROM active_alerts WHERE Ticker=?", (row['Ticker'],))
        for _, row in active_alerts_new.iterrows():
            if row['Ticker'] not in existing_tickers:
                newly_added.append(row['Ticker'])
            conn.execute("""
                REPLACE INTO active_alerts (Ticker, Alert_Level, Trigger_Volume, Timestamp)
                VALUES (?, ?, ?, ?)
            """, (row['Ticker'], row['Volume_Alert'], row['Trigger_Volume'], row['Timestamp']))
    return newly_added

def send_new_alert_emails(active_alerts_new: pd.DataFrame, newly_added: list, db_path=DB_PATH):
    if not newly_added: return
    with sqlite3.connect(db_path) as conn:
        users = conn.execute("SELECT email, alerts FROM user_prefs").fetchall()
    for email, alerts_str in users:
        alert_list = alerts_str.split(",")
        user_alerts = active_alerts_new[
            (active_alerts_new['Ticker'].isin(newly_added)) &
            (active_alerts_new['Volume_Alert'].isin(alert_list))
        ]
        for _, row in user_alerts.iterrows():
            send_alert_email(
                to_email=email,
                ticker=row['Ticker'],
                alert=row['Volume_Alert'],
                rsi=row['RSI'],
                timestamp=row['Timestamp'],
                price=row['Close'],
                volume=row['Trigger_Volume'],
                volume_ratio=1.0
            )

def update_latest_alerts_table(active_alerts_new: pd.DataFrame, db_path=DB_PATH):
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM latest_alerts")
        for _, row in active_alerts_new.iterrows():
            conn.execute("""
                INSERT INTO latest_alerts 
                (Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Ticker'], row['Close'], row['Trigger_Volume'], row['volume_z'],
                row['Volume_Ratio'], row['Volume_Alert'], row['RSI'], row['Timestamp']
            ))

def run_alert_pipeline(tickers, days: int = 1, alert_threshold_z: float = 1.5, volume_tolerance: float = 1.5):
    setup_database()
    data = prepare_stock_data(tickers, days)
    if data.empty:
        print("No stock data available. Exiting pipeline.")
        return pd.DataFrame()
    latest, active_alerts_new = get_latest_active_alerts(data, threshold_z=alert_threshold_z)
    newly_added = update_active_alerts(data, active_alerts_new, volume_tolerance=volume_tolerance)
    send_new_alert_emails(active_alerts_new, newly_added)
    update_latest_alerts_table(active_alerts_new)
    print(f"Processed alerts for {len(active_alerts_new)} active tickers.")
    return active_alerts_new
