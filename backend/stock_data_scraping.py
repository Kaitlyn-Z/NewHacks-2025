"""
Module for scraping stock data using yfinance. Data will be used for AI analysis
and other analysis.
"""

import pandas as pd
import yfinance as yf


# Scrape data for given tickers (from Reddit scraping) and put in pandas DataFrame
# Use data for stock analysis (volume spikes, RSI, etc.)
def fetch_stock_data(tickers, days):
    all_data = []

    for t in tickers:
        # Download the last N days of daily data
        df = yf.download(t, period=f"{days}d", interval="1h", progress=False)

        if not df.empty:
            for date, row in df.iterrows():
                all_data.append({
                    "ticker": t,
                    "date": date.date(),
                    "close": round(row["Close"].item(), 2),
                    "volume": int(row["Volume"].item())
                })

    # Combine all tickers into one DataFrame
    df = pd.DataFrame(all_data)
    return df


# Testing purposes
def main():
    from tabulate import tabulate
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]
    df = fetch_stock_data(tickers, days=1)
    print(tabulate(df, headers='keys', showindex=False))


if __name__ == "__main__":
    main()
