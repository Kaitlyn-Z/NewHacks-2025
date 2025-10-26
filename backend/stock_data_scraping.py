"""
Module for scraping stock data using yfinance.
Fetches tickers from Reddit hotstocks if not provided.
"""

import pandas as pd
import yfinance as yf
from signals.hotstocks.cli import get_hot_tickers
from signals.hotstocks.config import load_config

def fetch_stock_data(tickers=None, days=1, config_path="config.json"):
    """
    Fetch stock data for a list of tickers using yfinance.
    If tickers is None, automatically fetch hot tickers from Reddit pipeline.

    Returns a DataFrame with columns: Ticker, Date, Close, Volume
    """
    if tickers is None:
        cfg = load_config(config_path)
        tickers = get_hot_tickers(cfg)

    if not tickers:
        return pd.DataFrame(columns=["Ticker", "Date", "Close", "Volume"])

    all_data = []
    for t in tickers:
        try:
            df = yf.download(t, period=f"{days}d", interval="1h", progress=False)
            if df.empty:
                continue
            for date, row in df.iterrows():
                all_data.append({
                    "Ticker": t,
                    "Date": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "Close": round(row["Close"], 2),
                    "Volume": int(row["Volume"])
                })
        except Exception:
            continue  # skip ticker on error

    df_all = pd.DataFrame.from_records(all_data)

    # Ensure correct dtypes
    df_all = df_all.astype({
        "Ticker": "string",
        "Date": "string",
        "Close": "float",
        "Volume": "int"
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
