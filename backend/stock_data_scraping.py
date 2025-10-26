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
                    "ticker": t,
                    "date": date.date(),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })

        except Exception as e:
            #print(f"Error fetching data for {t}: {e}")
            continue  # Skip to the next ticker

    if all_data:
        df_all = pd.DataFrame(all_data)
    else:
        df_all = pd.DataFrame(columns=["ticker", "date", "close", "volume"])

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
