"""
Module for scraping stock data using yfinance.
Fetches tickers from Reddit hotstocks if not provided.
"""

# backend/stock_data_scraping.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_stock_data(tickers, days=1):
    """Fetch OHLCV data for given tickers and return a DataFrame."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    data_frames = []

    for t in tickers:
        try:
            df = yf.download(t, start=start_date, end=end_date, progress=False)
            if df.empty:
                continue
            df.reset_index(inplace=True)
            df = df.rename(columns={
                "Date": "Date", "Open": "Open", "High": "High",
                "Low": "Low", "Close": "Close", "Volume": "Volume"
            })
            df["Ticker"] = t
            data_frames.append(df)
        except Exception:
            continue

    if not data_frames:
        return pd.DataFrame()
    return pd.concat(data_frames, ignore_index=True)
