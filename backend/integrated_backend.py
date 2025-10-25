"""
Integrated Meme Stock Backend
Combines: Volume Analysis + Sentiment Analysis + Real-time Data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai
import json
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Load API keys
try:
    import api_keys
    genai.configure(api_key=api_keys.GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
except ImportError:
    logger.warning("api_keys.py not found. Gemini features will be disabled.")
    api_keys = None

# Configuration
LOOKBACK_DAYS = 50  # For volume calculations
SENTIMENT_LOOKBACK = 3  # Days for sentiment analysis
REFRESH_INTERVAL = 30  # seconds

# Monitored stock tickers
TARGET_TICKERS = ["GME", "AMC", "BB", "TSLA", "NVDA", "PLTR", "NOK", "AAPL", "MSFT"]

# Mock social media posts for sentiment analysis
# In production, replace with actual social media data
MOCK_POSTS = [
    "GME is mooning! Volume is crazy 🚀🚀🚀",
    "AMC holding strong, bullish sentiment",
    "TSLA predictions looking good for next week",
    "BB showing strong technicals, buying calls",
    "NVDA might drop, seems overpriced now",
    "PLTR gaining traction on social media",
    "NOK volume spike detected",
    "AAPL showing steady growth",
    "MSFT cloud business looking strong"
]


class VolumeAnalyzer:
    """Handles volume spike detection and classification"""
    
    @staticmethod
    def fetch_stock_data(ticker: str, days: int = 50) -> pd.DataFrame:
        """Fetch stock data with volume information"""
        try:
            df = yf.download(ticker, period=f"{days}d", interval="1d", progress=False)
            if df.empty:
                logger.warning(f"No data for {ticker}")
                return pd.DataFrame()
            
            df['Ticker'] = ticker
            return df
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def calculate_volume_zscore(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate rolling z-score for volume"""
        if df.empty or len(df) < 50:
            return df
        
        # Calculate 50-day rolling mean and std
        df['volume_mean'] = df['Volume'].rolling(window=50, min_periods=1).mean()
        df['volume_std'] = df['Volume'].rolling(window=50, min_periods=1).std()
        
        # Calculate z-score
        df['volume_z'] = (df['Volume'] - df['volume_mean']) / df['volume_std']
        
        return df
    
    @staticmethod
    def classify_alert(z_score: float) -> str:
        """Classify volume alert level"""
        if pd.isna(z_score):
            return 'normal'
        elif z_score >= 4:
            return 'high'
        elif z_score >= 2.5:
            return 'medium'
        elif z_score >= 1.5:
            return 'low'
        else:
            return 'normal'
    
    @staticmethod
    def get_volume_ratio(df: pd.DataFrame) -> float:
        """Calculate volume ratio (latest vs average)"""
        if df.empty or len(df) < 2:
            return 1.0
        
        avg_volume = df['Volume'].iloc[:-1].mean()
        latest_volume = df['Volume'].iloc[-1]
        
        if avg_volume == 0:
            return 1.0
        
        return latest_volume / avg_volume


class SentimentAnalyzer:
    """Handles sentiment analysis using Gemini AI"""
    
    def __init__(self):
        self.model = None
        if api_keys:
            try:
                self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
                logger.info("Gemini model initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
    
    def parse_gemini_response(self, raw_text: str) -> pd.DataFrame:
        """Parse CSV-like response from Gemini"""
        try:
            raw_text = raw_text.strip()
            lines = raw_text.splitlines()
            
            # Find header line
            start_idx = None
            for i, line in enumerate(lines):
                if 'ticker' in line.lower() and 'sentiment' in line.lower():
                    start_idx = i
                    break
            
            if start_idx is None:
                logger.warning("No valid header in Gemini response")
                return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])
            
            # Parse data
            data = []
            for line in lines[start_idx + 1:]:
                if not line.strip() or line.startswith('#'):
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    ticker, sentiment, score = parts[0], parts[1], parts[2]
                    try:
                        score = float(score)
                    except ValueError:
                        score = 0.0
                    
                    data.append({
                        "ticker": ticker.upper(),
                        "sentiment": sentiment.lower(),
                        "sentiment_score": score
                    })
            
            return pd.DataFrame(data)
        
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])
    
    def analyze_sentiment(self, posts: List[str]) -> pd.DataFrame:
        """Analyze sentiment of posts using Gemini"""
        if not self.model:
            logger.warning("Gemini model not available, returning neutral sentiment")
            return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])
        
        try:
            prompt = f"""
            Analyze the sentiment for each stock ticker mentioned in these social media posts.
            Return ONLY a CSV format with headers: ticker,sentiment,sentiment_score
            
            Rules:
            - sentiment should be: bullish, bearish, or neutral
            - sentiment_score should be a number from -1 (very bearish) to +1 (very bullish)
            - Only include tickers that are explicitly mentioned
            - One line per ticker
            
            Posts:
            {chr(10).join(posts)}
            
            Example output format:
            ticker,sentiment,sentiment_score
            GME,bullish,0.8
            AMC,neutral,0.1
            """
            
            response = self.model.generate_content(prompt)
            return self.parse_gemini_response(response.text)
        
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return pd.DataFrame(columns=["ticker", "sentiment", "sentiment_score"])
    
    def generate_stock_advice(self, ticker: str, price: float, price_change: float, 
                              volume_ratio: float, sentiment_score: float) -> str:
        """Generate investment advice for a specific stock using Gemini"""
        if not self.model:
            return "AI analysis unavailable. Please check system configuration."
        
        try:
            prompt = f"""
            You are a financial advisor AI. Provide brief, actionable investment advice for the following stock:
            
            Ticker: {ticker}
            Current Price: ${price:.2f}
            Price Change: {price_change:+.2f}%
            Volume Ratio: {volume_ratio:.2f}x (current volume vs average)
            Sentiment Score: {sentiment_score:.2f} (from -1 bearish to +1 bullish)
            
            Provide advice in 2-3 sentences. Consider:
            - The unusual volume activity (high volume ratio indicates unusual trading activity)
            - Price momentum and sentiment
            - Risk factors for meme stocks
            
            Keep it concise and professional. Do not include disclaimers.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Error generating advice for {ticker}: {e}")
            return "Unable to generate advice at this time."


class StockAlertSystem:
    """Main system that combines volume and sentiment analysis"""
    
    def __init__(self):
        self.volume_analyzer = VolumeAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.cache = {}
        self.last_update = None
    
    def get_alerts(self, force_refresh: bool = False) -> List[Dict]:
        """Generate stock alerts combining volume and sentiment"""
        
        # Use cache if recent
        if not force_refresh and self.last_update:
            elapsed = (datetime.now() - self.last_update).seconds
            if elapsed < REFRESH_INTERVAL and self.cache:
                logger.info("Returning cached alerts")
                return self.cache.get('alerts', [])
        
        logger.info("Generating fresh alerts...")
        alerts = []
        
        # Fetch sentiment data
        sentiment_df = self.sentiment_analyzer.analyze_sentiment(MOCK_POSTS)
        
        # Process each ticker
        for ticker in TARGET_TICKERS:
            try:
                # Fetch stock data
                df = self.volume_analyzer.fetch_stock_data(ticker, LOOKBACK_DAYS)
                if df.empty:
                    continue
                
                # Calculate volume metrics
                df = self.volume_analyzer.calculate_volume_zscore(df)
                latest = df.iloc[-1]
                
                volume_z = latest['volume_z'] if 'volume_z' in df.columns else 0
                volume_ratio = self.volume_analyzer.get_volume_ratio(df)
                priority = self.volume_analyzer.classify_alert(volume_z)
                
                # Get sentiment
                sentiment_data = sentiment_df[sentiment_df['ticker'] == ticker]
                sentiment_score = sentiment_data['sentiment_score'].mean() if not sentiment_data.empty else 0.0
                
                # Calculate mention count (mock for now)
                mention_count = int(abs(sentiment_score) * 100 + volume_ratio * 50)
                
                # Get price data
                current_price = float(latest['Close'])
                prev_close = float(df.iloc[-2]['Close']) if len(df) > 1 else current_price
                price_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                
                # Generate AI advice
                advice = self.sentiment_analyzer.generate_stock_advice(
                    ticker, current_price, price_change, volume_ratio, sentiment_score
                )
                
                # Only include alerts with some activity
                if priority != 'normal' or abs(sentiment_score) > 0.3:
                    alert = {
                        'id': f"{ticker}-{int(time.time())}",
                        'ticker': ticker,
                        'mentionCount': mention_count,
                        'volumeRatio': round(volume_ratio, 2),
                        'currentPrice': round(current_price, 2),
                        'priceChange': round(price_change, 2),
                        'detectedAt': datetime.now().isoformat(),
                        'priority': priority,
                        'sentimentScore': round(sentiment_score, 2),
                        'volumeZScore': round(volume_z, 2),
                        'advice': advice
                    }
                    alerts.append(alert)
                
            except Exception as e:
                logger.error(f"Error processing {ticker}: {e}")
                continue
        
        # Sort by priority and volume ratio
        priority_order = {'high': 0, 'medium': 1, 'low': 2, 'normal': 3}
        alerts.sort(key=lambda x: (priority_order.get(x['priority'], 3), -x['volumeRatio']))
        
        # Update cache
        self.cache['alerts'] = alerts
        self.last_update = datetime.now()
        
        logger.info(f"Generated {len(alerts)} alerts")
        return alerts


# Initialize the alert system
alert_system = StockAlertSystem()


# API Endpoints
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current stock alerts"""
    try:
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        alerts = alert_system.get_alerts(force_refresh=force_refresh)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'timestamp': datetime.now().isoformat(),
            'count': len(alerts)
        })
    except Exception as e:
        logger.error(f"Error in /api/alerts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_detail(ticker):
    """Get detailed information for a specific stock"""
    try:
        ticker = ticker.upper()
        
        # Fetch data
        df = VolumeAnalyzer.fetch_stock_data(ticker, LOOKBACK_DAYS)
        if df.empty:
            return jsonify({
                'success': False,
                'error': f'No data available for {ticker}'
            }), 404
        
        df = VolumeAnalyzer.calculate_volume_zscore(df)
        
        # Prepare response
        latest = df.iloc[-1]
        history = df.tail(30)[['Close', 'Volume', 'volume_z']].to_dict('records')
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'currentPrice': float(latest['Close']),
            'volume': int(latest['Volume']),
            'volumeZScore': float(latest['volume_z']) if 'volume_z' in df.columns else 0,
            'history': history
        })
    except Exception as e:
        logger.error(f"Error in /api/stock/{ticker}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall system statistics"""
    try:
        alerts = alert_system.get_alerts()
        
        stats = {
            'totalAlerts': len(alerts),
            'highPriority': len([a for a in alerts if a['priority'] == 'high']),
            'mediumPriority': len([a for a in alerts if a['priority'] == 'medium']),
            'lowPriority': len([a for a in alerts if a['priority'] == 'low']),
            'totalMentions': sum(a['mentionCount'] for a in alerts),
            'lastUpdate': alert_system.last_update.isoformat() if alert_system.last_update else None
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Integrated Meme Stock Backend',
        'gemini_available': alert_system.sentiment_analyzer.model is not None,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Integrated Backend on port {port}")
    logger.info(f"Monitoring tickers: {', '.join(TARGET_TICKERS)}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

