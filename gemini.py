"""
Meme Stock Radar: Reddit + Momentum + Gemini
--------------------------------------------

This script:
1. Fetches stock data from Yahoo Finance (price, volume)
2. Analyzes social sentiment (example Reddit posts)
3. Combines both signals
4. Uses Gemini to summarize which tickers show meme-like momentum

🔧 Requirements:
pip install yfinance pandas google-generativeai praw
"""

import pandas as pd
import yfinance as yf
import google.generativeai as genai

# ==============================
# 1️⃣ CONFIGURATION
# ==============================

genai.configure(api_key="YOUR_GEMINI_API_KEY")

TICKERS = ["TSLA", "NVDA", "AAPL", "GME", "AMC"]
LOOKBACK_DAYS = 5

# Example posts you could replace with scraped Reddit or Stocktwits text
reddit_posts = [
    "TSLA is mooning, everyone’s buying calls! 🚀🚀",
    "NVDA might drop soon, too overpriced.",
    "GME could squeeze again, massive volume incoming!",
    "AAPL steady as usual, boring but safe.",
    "AMC short interest looks crazy high right now."
]

# ==============================
# 2️⃣ FETCH STOCK DATA
# ==============================

def fetch_stock_data(tickers, days=5):
    data = []
    for t in tickers:
        df = yf.download(t, period=f"{days}d", interval="1d", progress=False)
        if not df.empty:
            avg_vol = df["Volume"].mean()
            latest = df.iloc[-1]
            vol_ratio = latest["Volume"] / avg_vol
            pct_change = (latest["Close"] - latest["Open"]) / latest["Open"] * 100
            data.append({
                "ticker": t,
                "volume_ratio": round(vol_ratio, 2),
                "price_change_%": round(pct_change, 2)
            })
    return pd.DataFrame(data)

momentum_df = fetch_stock_data(TICKERS, LOOKBACK_DAYS)
print("📊 Momentum Data:")
print(momentum_df, "\n")

# ==============================
# 3️⃣ SENTIMENT ANALYSIS (Gemini)
# ==============================

model = genai.GenerativeModel("gemini-1.5-pro")

prompt = f"""
Analyze the sentiment for each of the following Reddit posts.
Return JSON with "ticker", "sentiment", and "sentiment_score" (-1 to +1).

Posts:
{reddit_posts}
"""

response = model.generate_content(prompt)
print("🧠 Raw Gemini Sentiment Output:\n", response.text, "\n")

# Try to load Gemini JSON output safely (if formatted as JSON)
try:
    import json
    sentiment_data = json.loads(response.text)
    sentiment_df = pd.DataFrame(sentiment_data)
except Exception:
    print("⚠️ Could not parse as JSON — Gemini might have formatted it as text instead.")
    sentiment_df = pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])

print("🗣️ Sentiment Data:")
print(sentiment_df, "\n")

# ==============================
# 4️⃣ COMBINE SENTIMENT + MOMENTUM
# ==============================

if not sentiment_df.empty:
    avg_sentiment = sentiment_df.groupby("ticker")["sentiment_score"].mean().reset_index()
    combined = momentum_df.merge(avg_sentiment, on="ticker", how="left")
else:
    combined = momentum_df.copy()

print("📈 Combined Data:")
print(combined, "\n")

# ==============================
# 5️⃣ GEMINI SUMMARY OF OVERALL MARKET SENTIMENT
# ==============================

summary_prompt = f"""
You are an AI financial analyst.
Given this data combining volume, price change, and sentiment:

{combined.to_string(index=False)}

Explain which stocks appear to have the strongest meme-like momentum or hype potential.
Focus on both high relative volume and positive sentiment.
"""

summary_response = model.generate_content(summary_prompt)

print("🤖 Gemini Market Summary:\n")
print(summary_response.text)
