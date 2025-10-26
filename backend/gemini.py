"""
Backend module integrating Google Gemini for stock analysis and recommendations
"""

import os
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

# TODO: import sqlite3 table from stock_analysis.py
# use latest_alerts table from stock_analysis.py
from stock_data_scraping import fetch_stock_data


def parse_gemini_csv_manual(raw_text):
    raw_text = raw_text.strip()
    lines = raw_text.splitlines()

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("ticker,sentiment,sentiment_score"):
            start_idx = i
            break

    if start_idx is None:
        print("No valid header found in Gemini output")
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


def analyze_sentiment(client, posts):
    prompt = f"""
    Analyze the sentiment for each of the Reddit posts in the dataframe.
    Return the results as CSV text with headers: ticker, sentiment, sentiment_score (-1 to +1).

    Posts:
    {posts}
    """

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    return parse_gemini_csv_manual(response.text)

def summarize_market(client, df):
    summary_prompt = f"""
    You are an AI financial analyst.
    Given this data combining volume ratio and sentiment score:
    {df.to_string(index=False)}

    Use real market data from the web if needed.
    Explain which stocks have the strongest meme-like momentum (high volume + positive sentiment).
    Keep the summary under 50 words.
    """

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=summary_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )
    )

    return response.text


def main():
    # Load environment variables
    load_dotenv()

    # Configure Gemini client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    tickers = ["TSLA", "NVDA", "BYND"]
    lookback_days = 3

    # Example Reddit posts (replace later with real scraped data)
    reddit_posts = [
        "TSLA is mooning, everyone’s buying calls! 🚀🚀",
        "TSLA prices predicted to rise!",
        "NVDA might drop soon, too overpriced."
    ]

    momentum_df = fetch_stock_data(tickers, lookback_days)
    sentiment_df = analyze_sentiment(client, reddit_posts)

    if not sentiment_df.empty:
        avg_sentiment = sentiment_df.groupby("ticker")["sentiment_score"].mean().reset_index()
        combined = momentum_df.merge(avg_sentiment, on="ticker", how="left")
    else:
        combined = momentum_df.copy()

    summary = summarize_market(client, combined)
    print("📰 Gemini Market Summary:\n")
    print(summary)


if __name__ == "__main__":
    main()
