# data web-scraped with beautiful soup
# in seperate file web_scraped.py

##import web_scraped_mock as ws # FOR web_scraped.py, this will re-run the web scraping / update with latest data
from backend.web_scraped_mock import target_tickers, stock_data #, mentions --> then we can implement that here
import pandas as pd
import ta
import sqlite3
from backend.notifier import send_alert_email
from datetime import datetime

data_frames = [] 

for ticker in target_tickers:
    df = stock_data(ticker)
    df['Ticker'] = ticker
    data_frames.append(df)


data = pd.concat(data_frames, ignore_index=True)

data['volume_z'] = data.groupby('Ticker')['Volume'].transform(
    lambda x: (x - x.rolling(50).mean()) / x.rolling(50).std())

data['Volume_Ratio'] = data['Volume'] / data.groupby('Ticker')['Volume'].transform('mean')

# Classification to classify status of volume spikes:

def classify_alert(z):
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

data['Volume_Alert'] = data['volume_z'].apply(classify_alert)

# RSI Indicator:
def compute_rsi(series, window=14):
    rsi = ta.momentum.RSIIndicator(close=series, window=window).rsi()
    return rsi.reindex(series.index, fill_value=None)

data['RSI'] = data.groupby('Ticker')['Close'].transform(lambda x: compute_rsi(x))

# Generate latest alerts summary:

latest = data.groupby('Ticker').tail(1)[['Ticker', 'Close', 'Volume', 'volume_z', 'Volume_Ratio', 'Volume_Alert', 'RSI']]

latest['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Generate a table summary for testing purposes:
#print("\n=== Latest Volume and RSI Alerts ===")
#print(latest.sort_values('volume_z', ascending=False).to_string(index=False))
print(f'{data}')


# Store latest alerts in alerts.db

with sqlite3.connect("backend/alerts.db") as conn: 
    conn.execute("""
        CREATE TABLE IF NOT EXISTS latest_alerts (
            Ticker TEXT,
            Close REAL,
            Volume INTEGER,
            volume_z REAL,
            Volume_Ratio REAL,
            Volume_Alert TEXT,
            RSI REAL,
            Timestamp TEXT
        )
    """)
    # Clear old alerts
    conn.execute("DELETE FROM latest_alerts")
    # Insert new alerts
    for _, row in latest.iterrows():
        conn.execute(
            "INSERT INTO latest_alerts (Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (row['Ticker'], row['Close'], row['Volume'],row['volume_z'], row['Volume_Ratio'], row['Volume_Alert'], row['RSI'], row['Timestamp'])
        )

# Sends email alerts to users based on their preferences and latest analysis results

with sqlite3.connect("backend/alerts.db") as conn:
    users = conn.execute("SELECT email, alerts FROM user_prefs").fetchall()

for email, alerts_str in users:
    alert_list = alerts_str.split(",")
    user_alerts = latest[latest['Volume_Alert'].isin(alert_list)]

    for _, row in user_alerts.iterrows():
        send_alert_email(
            to_email=email,
            ticker=row['Ticker'],
            alert=row['Volume_Alert'],
            rsi=row['RSI'],
            timestamp=row['Timestamp'],
            price=row['Close'], 
            volume=row['Volume'],
            volume_ratio=row['Volume_Ratio']
            )

# Note: In actual implementation, ensure to handle email sending limits and avoid spamming users.

