"""
Meme Stock Radar: Reddit + Momentum + Gemini
--------------------------------------------

This script:
1. Fetches stock data from Yahoo Finance (volume)
2. Analyzes social sentiment (example Reddit posts)
3. Combines both signals
4. Uses Gemini to summarize which tickers show meme-like momentum

🔧 Requirements:
pip install yfinance pandas google-generativeai praw
pip install -q -U google-genai
"""

import pandas as pd
from io import StringIO
import yfinance as yf
import google.generativeai as genai
import api_keys

# Configure Gemini
genai.configure(api_key=api_keys.GEMINI_API_KEY)

# Global variables
# TODO: get tickers from webscraping
TICKERS = ["TSLA", "NVDA"]
LOOKBACK_DAYS = 3

# Test posts generated w/AI
# TODO: Replace with actual post data later
reddit_posts = [
    "TSLA is mooning, everyone’s buying calls! 🚀🚀",
    "TSLA prices predicted to rise!",
    "NVDA might drop soon, too overpriced."
]

# Fetch stock data
def fetch_stock_data(tickers, days=5):
    data = []
    for t in tickers:
        df = yf.download(t, period=f"{days}d", interval="1d", progress=False)
        if not df.empty:
            avg_vol = df["Volume"].mean()
            latest = df.iloc[-1]
            vol_ratio = latest["Volume"] / avg_vol
            data.append({
                "ticker": t,
                "volume_ratio": round(vol_ratio, 2)
            })
    return pd.DataFrame(data)


def parse_gemini_csv_manual(raw_text):
    """
    Manually parse Gemini CSV-like output into a DataFrame.
    """
    raw_text = raw_text.strip()
    lines = raw_text.splitlines()

    # Find the header line
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("ticker,sentiment,sentiment_score"):
            start_idx = i
            break

    if start_idx is None:
        print("⚠️ No valid header found in Gemini output")
        return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])

    # Parse lines after header
    data = []
    for line in lines[start_idx + 1:]:
        if not line.strip():  # skip empty lines
            continue
        parts = line.split(",")
        if len(parts) != 3:
            continue  # skip malformed lines
        ticker, sentiment, score = parts
        try:
            score = float(score)
        except ValueError:
            score = None
        data.append({
            "ticker": ticker.strip(),
            "sentiment": sentiment.strip(),
            "sentiment_score": score
        })

    return pd.DataFrame(data)


momentum_df = fetch_stock_data(TICKERS, LOOKBACK_DAYS)

# SENTIMENT ANALYSIS (Gemini)
model = genai.GenerativeModel("gemini-2.5-flash")

prompt = f"""
Analyze the sentiment for each of the following Reddit posts.
Return these as a string with csv format? Include headers "ticker", "sentiment", and "sentiment_score" (-1 to +1).

Posts:
{reddit_posts}
"""
response = model.generate_content(prompt)
sentiment_df = parse_gemini_csv_manual(response.text)

# COMBINE SENTIMENT + MOMENTUM
if not sentiment_df.empty:
    avg_sentiment = sentiment_df.groupby("ticker")["sentiment_score"].mean().reset_index()
    combined = momentum_df.merge(avg_sentiment, on="ticker", how="left")
else:
    combined = momentum_df.copy()

# GEMINI SUMMARY OF OVERALL MARKET SENTIMENT
summary_prompt = f"""
You are an AI financial analyst.
Given this data combining volume, price change, and sentiment:

{combined.to_string(index=False)}

Explain which stocks appear to have the strongest meme-like momentum or hype potential.
Focus on both high relative volume and positive sentiment.
Keep the summary within 50 words.
"""

summary_response = model.generate_content(summary_prompt)

print("Gemini Market Summary:\n")
print(summary_response.text)