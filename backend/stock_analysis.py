# data web-scraped with beautiful soup
# in seperate file web_scraped.py

##import web_scraped_mock as ws # FOR web_scraped.py, this will re-run the web scraping / update with latest data
from web_scraped_mock import target_tickers, stock_data #, mentions --> then we can implement that here
import pandas as pd
import ta
import sqlite3
from notifier import send_alert_email
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

ALERT_THRESHOLD_Z = 1.5
active_alerts_new = latest[latest['volume_z'] >= ALERT_THRESHOLD_Z].copy()
active_alerts_new['Trigger_Volume'] = active_alerts_new['Volume'] 

# Generate a table summary for testing purposes:
#print("\n=== Latest Volume and RSI Alerts ===")
#print(latest.sort_values('volume_z', ascending=False).to_string(index=False))
print(f'{data}')

# ---------------------------------------------------------------------
# STEP 3: Database setup
# ---------------------------------------------------------------------
with sqlite3.connect("backend/alerts.db") as conn:
    # Dashboard table
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
    # Active alerts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS active_alerts (
            Ticker TEXT PRIMARY KEY,
            Alert_Level TEXT,
            Trigger_Volume REAL,
            Timestamp TEXT
        )
    """)

# ---------------------------------------------------------------------
# STEP 4: Load currently active alerts
# ---------------------------------------------------------------------
with sqlite3.connect("backend/alerts.db") as conn:
    existing_alerts = pd.read_sql_query("SELECT * FROM active_alerts", conn)

existing_tickers = set(existing_alerts['Ticker']) if not existing_alerts.empty else set()

# ---------------------------------------------------------------------
# STEP 5: Update active alerts
# ---------------------------------------------------------------------
VOLUME_TOLERANCE = 1.5  # stays active while current volume >= 1.5 * trigger volume
newly_added = []

with sqlite3.connect("backend/alerts.db") as conn:
    # Remove alerts that dropped below tolerance
    for _, row in existing_alerts.iterrows():
        ticker_data = active_alerts_new[active_alerts_new['Ticker'] == row['Ticker']]
        if ticker_data.empty:
            current_vol = data[data['Ticker']==row['Ticker']].iloc[-1]['Volume']
            if current_vol < row['Trigger_Volume'] * VOLUME_TOLERANCE:
                conn.execute("DELETE FROM active_alerts WHERE Ticker=?", (row['Ticker'],))

    # Add/update new alerts
    for _, row in active_alerts_new.iterrows():
        if row['Ticker'] not in existing_tickers:
            newly_added.append(row['Ticker'])
        conn.execute("""
            REPLACE INTO active_alerts (Ticker, Alert_Level, Trigger_Volume, Timestamp)
            VALUES (?, ?, ?, ?)
        """, (row['Ticker'], row['Volume_Alert'], row['Trigger_Volume'], row['Timestamp']))

# ---------------------------------------------------------------------
# STEP 6: Send emails for newly added alerts only
# ---------------------------------------------------------------------
if newly_added:
    with sqlite3.connect("backend/alerts.db") as conn:
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
                volume_ratio=1.0  # always 1 relative to trigger
            )

# ---------------------------------------------------------------------
# STEP 7: Update latest_alerts table for dashboard (only active alerts)
# ---------------------------------------------------------------------
with sqlite3.connect("backend/alerts.db") as conn:
    conn.execute("DELETE FROM latest_alerts")
    for _, row in active_alerts_new.iterrows():
        conn.execute("""INSERT INTO latest_alerts (Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (row['Ticker'], row['Close'], row['Trigger_Volume'], row['volume_z'],
      row['Volume_Ratio'], row['Volume_Alert'], row['RSI'], row['Timestamp']))


# Store latest alerts in alerts.db

#with sqlite3.connect("backend/alerts.db") as conn: 
#    conn.execute("""
#        CREATE TABLE IF NOT EXISTS latest_alerts (
#            Ticker TEXT,
#            Close REAL,
#            Volume INTEGER,
#            volume_z REAL,
#            Volume_Ratio REAL,
#            Volume_Alert TEXT,
#            RSI REAL,
#            Timestamp TEXT
#        )
#    """)
#    # Clear old alerts
#    conn.execute("DELETE FROM latest_alerts")
    # Insert new alerts
 #   for _, row in latest.iterrows():
 #       conn.execute(
 #           "INSERT INTO latest_alerts (Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, Timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
  #          (row['Ticker'], row['Close'], row['Volume'],row['volume_z'], row['Volume_Ratio'], row['Volume_Alert'], row['RSI'], row['Timestamp'])
  #      )

# Sends email alerts to users based on their preferences and latest analysis results

#with sqlite3.connect("backend/alerts.db") as conn:
#    users = conn.execute("SELECT email, alerts FROM user_prefs").fetchall()

#for email, alerts_str in users:
 #   alert_list = alerts_str.split(",")
 #   user_alerts = latest[latest['Volume_Alert'].isin(alert_list)]

  #  for _, row in user_alerts.iterrows():
  #      send_alert_email(
   #         to_email=email,
   #         ticker=row['Ticker'],
   #         alert=row['Volume_Alert'],
    #        rsi=row['RSI'],
    #        timestamp=row['Timestamp'],
    #        price=row['Close'], 
     #       volume=row['Volume'],
     #       volume_ratio=row['Volume_Ratio']
     #       )

# Note: In actual implementation, ensure to handle email sending limits and avoid spamming users.

