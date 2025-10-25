# data web-scraped with beautiful soup
# in seperate file web_scraped.py

##import web_scraped_mock as ws # FOR web_scraped.py, this will re-run the web scraping / update with latest data
from web_scraped_mock import target_tickers, stock_data
import pandas as pd
import ta

data_frames = [] 

for ticker in target_tickers:
    df = stock_data(ticker)
    df['Ticker'] = ticker
    data_frames.append(df)

data = pd.concat(data_frames, ignore_index=True)

data['volume_z'] = data.groupby('Ticker')['Volume'].transform(
    lambda x: (x - x.rolling(50).mean()) / x.rolling(50).std())

# compute the rolling z score of the volume for eaach target stock 
# --> how unusual is the volume compared to the last 50 days
# --> should we make this less than 50 days to identify short-term spikes?
# --> or should we make it more than 50 days to make it more robust to fluctuations?

# Classification to classify status of volume spikes

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

rsi_window = 14 # typical window for RSI calculation
data['RSI'] = data.groupby('Ticker')['Close'].transform(
    lambda x: ta.momentum.RSIIndicator(close=x, window=rsi_window).rsi()) 

# GENERATED SUGGESTION (to display a table / dashboard of results for *testing purposes*):
latest = data.groupby('Ticker').tail(1)[['Ticker', 'Volume', 'volume_z', 'Volume_Alert', 'RSI']]
print("\n=== Latest Volume and RSI Alerts ===")
print(latest.sort_values('volume_z', ascending=False).to_string(index=False))

# Store latest alerts in the database in the backend
# --> backend/alerts.db will store user emails + preferences + latest alerts

with sqlite3.connect("backend/alerts.db") as conn: # Crea
    conn.execute("""
        CREATE TABLE IF NOT EXISTS latest_alerts (
            Ticker TEXT,
            Volume_Alert TEXT,
            volume_z REAL,
            RSI REAL
        )
    """)
    # Clear old alerts
    conn.execute("DELETE FROM latest_alerts")
    # Insert new alerts
    for _, row in latest.iterrows():
        conn.execute(
            "INSERT INTO latest_alerts (Ticker, Volume_Alert, volume_z, RSI) VALUES (?, ?, ?, ?)",
            (row['Ticker'], row['Volume_Alert'], row['volume_z'], row['RSI'])
        )

# Sends email alerts to users based on their preferences and latest analysis results

import sqlite3
from backend.notifier import send_alert_email

# After generating 'latest' DataFrame
with sqlite3.connect("backend/alerts.db") as conn:
    users = conn.execute("SELECT email, alerts FROM user_prefs").fetchall()

for email, alerts_str in users:
    alert_list = alerts_str.split(",")

    # Filter alerts that match user's preferences
    user_alerts = latest[latest['Volume_Alert'].isin(alert_list)]

    for _, row in user_alerts.iterrows():
        send_alert_email(
            to_email=email,
            ticker=row['Ticker'],
            alert=row['Volume_Alert'],
            volume_z=row['volume_z'],
            rsi=row['RSI']
        )

# Note: In actual implementation, ensure to handle email sending limits and avoid spamming users.

