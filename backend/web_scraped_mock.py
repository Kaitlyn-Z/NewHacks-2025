# web_scraped_mock.py --> GENERATED FOR TESTING PURPOSES

# Note: Web-scrape from Reddit using BeautifulSoup in actual web_scraped.py
# Reddit API?
# In addition to data below, we want *MENTIONS* (for Dashboard display later, in React)

# Mock data generator to test your volume & RSI analysis code
# ------------------------------------------------------------

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ------------------------------------------------------------
# 1. Mock list of tickers
# ------------------------------------------------------------
target_tickers = ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'TSLA']

# ----------------------------------------------------------------------
# 2. Mock stock data generator # USE THIS FOR *actual* web_scraped.py *
# ----------------------------------------------------------------------
def stock_data(ticker: str) -> pd.DataFrame:
    """
    Simulates 200 days of stock data for a given ticker.
    Includes Date, Close, and Volume columns (just like real scraped data).
    """

    np.random.seed(hash(ticker) % (2**32 - 1))  # make each ticker deterministic

    n_days = 200
    dates = [datetime.today() - timedelta(days=i) for i in range(n_days)]
    dates.reverse()  # oldest first

    # Simulated price series (random walk)
    prices = 100 + np.cumsum(np.random.normal(0, 1.5, n_days))

    # Simulated volume series with occasional spikes
    base_volume = np.random.randint(3_000_000, 8_000_000, n_days)
    spike_indices = np.random.choice(n_days, size=5, replace=False)
    base_volume[spike_indices] *= np.random.randint(2, 5, size=5)  # simulate big spikes

    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Volume': base_volume
    })

    return df

# ------------------------------------------------------------
# 3. Optional quick test (only runs if you execute this file directly)
# ------------------------------------------------------------
if __name__ == "__main__":
    for t in target_tickers:
        print(f"\n--- {t} Sample Data ---")
        print(stock_data(t).head())