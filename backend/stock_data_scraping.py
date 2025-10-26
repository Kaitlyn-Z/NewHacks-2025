"""
Module for scraping stock data using yfinance. Data will be used for AI analysis
and other analysis.
"""

import pandas as pd
import yfinance as yf
from signals.hotstocks.cli import get_hot_tickers
from signals.hotstocks.config import load_config

cfg = load_config("config.json")

tickers = get_hot_tickers(cfg)

# Scrape data for given tickers (from Reddit scraping) and put in pandas DataFrame
# Use data for stock analysis (volume spikes, RSI, etc.)
def fetch_stock_data(tickers, days):
    all_data = []
    for t in tickers:
        try:
            # Attempt to download data
            df = yf.download(t, period=f"{days}d", interval="1h", progress=False)

            # Check if ticker returned valid data
            if df.empty:
                #print(f"No data found for {t}. Skipping.")
                continue

            # Collect relevant fields
            for date, row in df.iterrows():
                all_data.append({
                    "Ticker": t,
                    "Date": date.date(),
                    "Close": round(row["Close"], 2),
                    "Volume": int(row["Volume"])
                })

        except Exception as e:
            #print(f"Error fetching data for {t}: {e}")
            continue  # Skip to the next ticker

    df_all = pd.DataFrame.from_records(all_data)

    # Enforce column order and data types
    df_all = df_all.astype({
        "ticker": "string",
        "date": "string",
        "close": "float",
        "volume": "int"
    }, errors="ignore")

    return df_all


# Testing purposes
def main():
    from tabulate import tabulate
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]
    df = fetch_stock_data(tickers, days=1)
    print(tabulate(df, headers='keys', showindex=False))


if __name__ == "__main__":
    main()
