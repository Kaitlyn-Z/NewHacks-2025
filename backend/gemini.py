"""
Meme Stock Radar: Reddit + Momentum + Gemini

Requirements:
pip install yfinance pandas google-generativeai praw
pip install -q -U google-genai
"""
# TODO: remove later
import yfinance as yf

import pandas as pd
import google.generativeai as genai
import api_keys

# Configure Gemini
genai.configure(api_key=api_keys.GEMINI_API_KEY)

# TODO: get tickers from webscraping
# Can edit lookback days depending on what we think works
TICKERS = ["TSLA", "NVDA"]
LOOKBACK_DAYS = 3

# TODO: Replace with actual post data later
test_reddit_posts = [
    "TSLA is mooning, everyone’s buying calls! 🚀🚀",
    "TSLA prices predicted to rise!",
    "NVDA might drop soon, too overpriced."
]

# Fetch stock data
# TODO: replace with other code later, delete this function 
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
    print("fetch)strock_data data: ")
    print(data)
    return pd.DataFrame(data)

# Turn Gemini CSV-like output into pandas DataFrame
def parse_gemini_csv_response(raw_text):
    """
    Manually parse CSV-like String response from Gemini into a pandas DataFrame.
    Expects headers: ticker,sentiment,sentiment_score
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
        print("No valid header found in Gemini output.")
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

    print("parse_gemini_csv_response data: ")
    print(data)

    return pd.DataFrame(data)

def generate_gemini_sentiment_analysis(posts):
    prompt = f"""
    Analyze the sentiment for each of the following Reddit posts.
    Return these as a string with csv format. Include headers "ticker", "sentiment", and "sentiment_score" (-1 to +1).

    Posts:
    {posts}
    """
    response = model.generate_content(prompt)
    sentiment_df = parse_gemini_csv_response(response.text)
    return sentiment_df

def generate_gemini_summary(combined_df):
    prompt = f"""
    You are an AI financial analyst.
    Given this data combining volume, price change, and sentiment:

    {combined_df.to_string(index=False)}

    Explain which stocks appear to have the strongest meme-like momentum or hype potential.
    Focus on both high relative volume and positive sentiment.
    Keep the summary within 50 words.
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("Running Gemini Meme Stock Radar...")

    # Generate momentum data w/yfinance
    momentum_df = fetch_stock_data(TICKERS, LOOKBACK_DAYS)

    # Sentiment analysis (Gemini)
    model = genai.GenerativeModel("gemini-2.5-flash")
    sentiment_df = generate_gemini_sentiment_analysis(test_reddit_posts)

    # COMBINE SENTIMENT + MOMENTUM
    if not sentiment_df.empty:
        avg_sentiment = sentiment_df.groupby("ticker")["sentiment_score"].mean().reset_index()
        combined = momentum_df.merge(avg_sentiment, on="ticker", how="left")
    else:
        combined = momentum_df.copy()

    # Generate summary analysis (Gemini)
    summary_response = generate_gemini_summary(combined)
    print("Gemini Market Summary:\n")
    print(summary_response)