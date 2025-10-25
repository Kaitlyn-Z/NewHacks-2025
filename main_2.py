# data web-scraped with beautiful soup
# in seperate file web_scraped.py

#import web_scraped.py as ws # temporary name
#from ws import target_stickers, stock_data # anything else needed?
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

# from ChatGPT suggestion --> need 'Close' data too from web scraping.

# import yahoo finance as yf 
# [see if this would allow us to obtain the 'Close' data for our target stocks]

#rsi_indicator = ta.momentum.RSIIndicator(close=close_prices, window=50) # should window be 50 or 14?
#rsi_values = rsi_indicator.rsi()
#data['RSI_50'] = rsi_values

# GENERATED SUGGESTION (to display a table / dashboard of results for *testing purposes*):
latest = data.groupby('Ticker').tail(1)[['Ticker', 'Volume', 'volume_z', 'Volume_Alert', 'RSI']]
print("\n=== Latest Volume and RSI Alerts ===")
print(latest.sort_values('volume_z', ascending=False).to_string(index=False))

# --> What other information would be useful to display on dashboard?
# Consult the website design mockup.

# POSSIBLE RECOMMENDATION SYSTEM:

# If RSI < 30 and Volume_Alert is Medium or High Alert:
#     Recommend "Potential Buy Opportunity"
# If RSI > 70 and Volume_Alert is Medium or High Alert:
#     Recommend "Potential Sell Opportunity"

# Is this legal though ...


# EMAIL NOTIFICATION SYSTEM

# User will have option to subscribe to emails for each category of alerts
# (e.g., only High Alert, Medium and High Alert, etc.)

# Create an email notification system.

