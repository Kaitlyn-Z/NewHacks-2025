# data web-scraped with beautiful soup
# in seperate file web_scraped.py

import web_scraped.py as ws # temporary name
from ws import target_stickers, stock_data # anything else needed?
import pandas as pd
import ta

data_frames = [] 

for ticker in target_stickers:
    df = stock_data(ticker)
    df['Ticker'] = ticker
    data_frames.append(df)

data = pd.concat(data_frames, ignore_index=True)

data['volume_z'] = data.groupby('Ticker')['Volume'].transform(
    lambda x: (x - x.rolling(50).mean()) / x.rolling(50).std())

# compute the rolling z score of the volume for eaach target stock

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

