"""
Meme Stock Radar: Reddit + Momentum + Gemini
--------------------------------------------

This script:
1. Fetches stock data from Yahoo Finance (volume)
2. Analyzes social sentiment (example Reddit posts)
3. Combines both signals
4. Uses Gemini to summarize which tickers show meme-like momentum

Requirements:
"""

import os
import pandas as pd
import yfinance as yf
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Global variables
TICKERS = ["TSLA", "NVDA"]
LOOKBACK_DAYS = 3

# Example Reddit posts (TODO: replace with real data)
reddit_posts = [
    "TSLA is mooning, everyone’s buying calls! 🚀🚀",
    "TSLA prices predicted to rise!",
    "NVDA might drop soon, too overpriced."
]


# --- Fetch stock data ---
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


# --- Manually parse CSV-like Gemini output ---
def parse_gemini_csv_manual(raw_text):
    raw_text = raw_text.strip()
    lines = raw_text.splitlines()

    # Find header line
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("ticker,sentiment,sentiment_score"):
            start_idx = i
            break

    if start_idx is None:
        print("⚠️ No valid header found in Gemini output")
        return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])

    data = []
    for line in lines[start_idx + 1:]:
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) != 3:
            continue
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


def analyze_sentiment(posts):
    """Uses Gemini to generate sentiment CSV for each ticker."""
    prompt = f"""
    Analyze the sentiment for each of the following Reddit posts.
    Return results as CSV text with headers: ticker,sentiment,sentiment_score (-1 to +1).
    Posts:
    {posts}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    print("🧠 Raw Gemini Output:\n", response.text, "\n")
    return parse_gemini_csv_manual(response.text)


def summarize_market(df):
    """Summarizes combined momentum and sentiment data."""
    summary_prompt = f"""
    You are an AI financial analyst.
    Given this data combining volume ratio and sentiment score:
    {df.to_string(index=False)}

    Explain which stocks have the strongest meme-like momentum (high volume + positive sentiment).
    Keep the summary under 50 words.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=summary_prompt
    )

    return response.text


def main():
    momentum_df = fetch_stock_data(TICKERS, LOOKBACK_DAYS)
    sentiment_df = analyze_sentiment(reddit_posts)

    if not sentiment_df.empty:
        avg_sentiment = sentiment_df.groupby("ticker")["sentiment_score"].mean().reset_index()
        combined = momentum_df.merge(avg_sentiment, on="ticker", how="left")
    else:
        combined = momentum_df.copy()

    print("\n📊 Combined Data:")
    print(combined, "\n")

    summary = summarize_market(combined)
    print("📰 Gemini Summary:\n")
    print(summary)


if __name__ == "__main__":
    main()
