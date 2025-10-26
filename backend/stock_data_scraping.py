"""
Module for scraping stock data using yfinance.
Fetches tickers from Reddit hotstocks if not provided.
"""

# backend/stock_data_scraping.py
import warnings
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(tickers, days=None, start_date=None, end_date=None):
    import yfinance as yf
    all_data = []
    for t in tickers:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if start_date and end_date:
                    df = yf.download(t, start=start_date, end=end_date)
                elif days:
                    df = yf.download(t, period=f"{days}d", interval="1d")
                else:
                    df = yf.download(t, period="3mo", interval="1d")
            df = df.rename(columns={
                "Date": "Date", "Open": "Open", "High": "High",
                "Low": "Low", "Close": "Close", "Volume": "Volume"
            })
            df['Ticker'] = t
            all_data.append(df)
        except Exception as e:
            print(f"Error fetching data for {t}: {e}")
            continue
    if not all_data:
        return pd.DataFrame()
    return pd.concat(all_data)
