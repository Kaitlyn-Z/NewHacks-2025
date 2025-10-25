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
    # Add parent directory to path to import api_keys
    import sys
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    import api_keys
    genai.configure(api_key=api_keys.GEMINI_API_KEY)
    logger.info("✅ Gemini API configured successfully with key: {}...".format(api_keys.GEMINI_API_KEY[:20]))
except ImportError as e:
    logger.warning(f"api_keys.py not found: {e}. Gemini features will be disabled.")
    api_keys = None
except Exception as e:
    logger.error(f"Error configuring Gemini API: {e}")
    api_keys = None

# Configuration
LOOKBACK_DAYS = 50  # For volume calculations
SENTIMENT_LOOKBACK = 3  # Days for sentiment analysis
REFRESH_INTERVAL = 1800  # seconds (30 minutes - matches scheduler)

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
    def generate_mock_data(ticker: str, days: int = 50) -> pd.DataFrame:
        """Generate realistic mock stock data for testing"""
        # Use ticker as seed for consistent data per ticker
        seed_value = sum(ord(c) for c in ticker)
        np.random.seed(seed_value)
        
        # Generate dates
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='D')
        
        # Base price (different for each ticker)
        base_price = 50 + (seed_value % 200)
        
        # Generate realistic price movements
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * np.exp(np.cumsum(returns))
        
        # Generate volume with occasional spikes
        base_volume = 1_000_000 + (seed_value % 5_000_000)
        volumes = np.random.lognormal(np.log(base_volume), 0.5, days)
        
        # Add volume spikes in recent days (to trigger alerts)
        spike_days = [days-3, days-1]  # Spikes 3 and 1 days ago
        for spike_day in spike_days:
            if 0 <= spike_day < days:
                volumes[spike_day] *= np.random.uniform(2.5, 5.0)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Open': prices * np.random.uniform(0.98, 1.0, days),
            'High': prices * np.random.uniform(1.0, 1.05, days),
            'Low': prices * np.random.uniform(0.95, 1.0, days),
            'Close': prices,
            'Volume': volumes.astype(int),
            'Ticker': ticker
        }, index=dates)
        
        logger.info(f"Generated mock data for {ticker}")
        return df
    
    @staticmethod
    def fetch_stock_data(ticker: str, days: int = 50) -> pd.DataFrame:
        """Fetch stock data with volume information"""
        try:
            df = yf.download(ticker, period=f"{days}d", interval="1d", progress=False)
            if df.empty:
                logger.warning(f"No data for {ticker}, using mock data")
                return VolumeAnalyzer.generate_mock_data(ticker, days)
            
            df['Ticker'] = ticker
            return df
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}, using mock data")
            return VolumeAnalyzer.generate_mock_data(ticker, days)
    
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
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI (Relative Strength Index)"""
        if df.empty or len(df) < period + 1:
            df['RSI'] = 50.0  # Neutral RSI if not enough data
            return df
        
        # Calculate price changes
        delta = df['Close'].diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        df['RSI'] = rsi.fillna(50.0)  # Fill NaN with neutral value
        return df


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
            logger.warning(f"Could not generate AI advice for {ticker}: {e}")
            # Provide enhanced rule-based fallback advice
            sentiment_desc = "bullish" if sentiment_score > 0.3 else "bearish" if sentiment_score < -0.3 else "neutral"
            volume_desc = "extremely high" if volume_ratio > 3 else "elevated" if volume_ratio > 2 else "moderate"
            
            # Build comprehensive advice
            advice_parts = []
            
            # Volume analysis
            advice_parts.append(f"{ticker} is experiencing {volume_desc} trading volume at {volume_ratio:.1f}x the average")
            
            # Price movement analysis
            if abs(price_change) > 5:
                direction = "surging" if price_change > 0 else "declining sharply"
                advice_parts.append(f"with the price {direction} by {abs(price_change):.1f}%")
            elif abs(price_change) > 2:
                direction = "rising" if price_change > 0 else "falling"
                advice_parts.append(f"while {direction} by {abs(price_change):.1f}%")
            else:
                advice_parts.append(f"with relatively stable pricing ({price_change:+.1f}%)")
            
            # Sentiment integration
            if abs(sentiment_score) > 0.5:
                advice_parts.append(f"Social sentiment is strongly {sentiment_desc} ({sentiment_score:+.1f})")
            elif abs(sentiment_score) > 0.3:
                advice_parts.append(f"showing {sentiment_desc} sentiment ({sentiment_score:+.1f})")
            
            # Trading recommendation based on volume and price
            if volume_ratio > 3 and abs(price_change) > 3:
                recommendation = "This combination of high volume and significant price movement suggests heightened volatility. Consider waiting for stabilization before entering positions"
            elif volume_ratio > 3:
                recommendation = "The unusual volume spike warrants close monitoring for potential breakout or breakdown patterns"
            elif volume_ratio > 2:
                recommendation = "Watch for confirmation of trend direction before taking positions"
            else:
                recommendation = "Monitor for volume confirmation before acting"
            
            advice_parts.append(recommendation + ".")
            
            return ". ".join(advice_parts)


class StockAlertSystem:
    """Main system that combines volume and sentiment analysis"""
    
    def __init__(self):
        self.volume_analyzer = VolumeAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.cache = {}
        self.last_update = None
        self.use_database = True  # Use stock_analysis.py database if available
    
    def get_alerts_from_database(self):
        """Get alerts from stock_analysis.py database if available"""
        try:
            import sqlite3
            with sqlite3.connect("backend/alerts.db") as conn:
                rows = conn.execute("""
                    SELECT Ticker, Close, Volume, volume_z, Volume_Ratio, Volume_Alert, RSI, 
                           Price_Change, Sentiment_Score, Mention_Count, Timestamp 
                    FROM latest_alerts
                """).fetchall()
                
                if not rows:
                    return None
                
                alerts = []
                for r in rows:
                    # Map priority
                    priority = 'normal'
                    if 'High' in r[5]:
                        priority = 'high'
                    elif 'Medium' in r[5]:
                        priority = 'medium'
                    elif 'Low' in r[5]:
                        priority = 'low'
                    
                    alert = {
                        'id': f"{r[0]}-{int(time.time())}",
                        'ticker': r[0],
                        'mentionCount': r[9] if r[9] else 0,
                        'volumeRatio': round(r[4], 2) if r[4] else 1.0,
                        'currentPrice': round(r[1], 2) if r[1] else 0,
                        'priceChange': round(r[7], 2) if r[7] else 0,
                        'detectedAt': r[10] if r[10] else datetime.now().isoformat(),
                        'priority': priority,
                        'sentimentScore': round(r[8], 2) if r[8] else 0,
                        'volumeZScore': round(r[3], 2) if r[3] else 0,
                        'rsi': round(r[6], 2) if r[6] else 50.0,
                        'advice': self.generate_advice_for_alert(r[0], r[1], r[7], r[4], r[8])
                    }
                    alerts.append(alert)
                
                return alerts
        except Exception as e:
            logger.warning(f"Could not fetch from database: {e}")
            return None
    
    def generate_advice_for_alert(self, ticker, price, price_change, volume_ratio, sentiment_score):
        """Generate advice for an alert"""
        sentiment_desc = "bullish" if sentiment_score > 0.3 else "bearish" if sentiment_score < -0.3 else "neutral"
        volume_desc = "extremely high" if volume_ratio > 3 else "elevated" if volume_ratio > 2 else "moderate"
        
        advice_parts = []
        advice_parts.append(f"{ticker} is experiencing {volume_desc} trading volume at {volume_ratio:.1f}x the average")
        
        if abs(price_change) > 5:
            direction = "surging" if price_change > 0 else "declining sharply"
            advice_parts.append(f"with the price {direction} by {abs(price_change):.1f}%")
        elif abs(price_change) > 2:
            direction = "rising" if price_change > 0 else "falling"
            advice_parts.append(f"while {direction} by {abs(price_change):.1f}%")
        
        if abs(sentiment_score) > 0.3:
            advice_parts.append(f"Social sentiment is {sentiment_desc} ({sentiment_score:+.1f})")
        
        if volume_ratio > 3 and abs(price_change) > 3:
            recommendation = "This combination suggests heightened volatility. Consider waiting for stabilization"
        elif volume_ratio > 2:
            recommendation = "Watch for confirmation of trend direction before taking positions"
        else:
            recommendation = "Monitor for volume confirmation before acting"
        
        advice_parts.append(recommendation + ".")
        return ". ".join(advice_parts)
    
    def get_alerts(self, force_refresh: bool = False) -> List[Dict]:
        """Generate stock alerts combining volume and sentiment"""
        
        # Try to get alerts from database first (if stock_analysis.py has run)
        if self.use_database and not force_refresh:
            db_alerts = self.get_alerts_from_database()
            if db_alerts:
                logger.info(f"Returning {len(db_alerts)} alerts from database")
                self.cache['alerts'] = db_alerts
                self.last_update = datetime.now()
                return db_alerts
        
        # Use cache if recent
        if not force_refresh and self.last_update:
            elapsed = (datetime.now() - self.last_update).seconds
            if elapsed < REFRESH_INTERVAL and self.cache:
                logger.info("Returning cached alerts")
                return self.cache.get('alerts', [])
        
        logger.info("Generating fresh alerts...")
        alerts = []
        
        # Fetch sentiment data (with quota-aware caching)
        # Only refresh sentiment every 5 minutes to preserve API quota
        sentiment_cache_valid = (
            hasattr(self, 'sentiment_cache_time') and 
            self.sentiment_cache_time and
            (datetime.now() - self.sentiment_cache_time).seconds < 300
        )
        
        if sentiment_cache_valid and hasattr(self, 'cached_sentiment'):
            logger.info("Using cached sentiment data")
            sentiment_df = self.cached_sentiment
        else:
            sentiment_df = self.sentiment_analyzer.analyze_sentiment(MOCK_POSTS)
            self.cached_sentiment = sentiment_df
            self.sentiment_cache_time = datetime.now()
            logger.info("Refreshed sentiment data")
        
        # Process each ticker
        for ticker in TARGET_TICKERS:
            try:
                # Fetch stock data
                df = self.volume_analyzer.fetch_stock_data(ticker, LOOKBACK_DAYS)
                if df.empty:
                    continue
                
                # Calculate volume metrics and RSI
                df = self.volume_analyzer.calculate_volume_zscore(df)
                df = self.volume_analyzer.calculate_rsi(df)
                latest = df.iloc[-1]
                
                volume_z = latest['volume_z'] if 'volume_z' in df.columns else 0
                volume_ratio = self.volume_analyzer.get_volume_ratio(df)
                rsi = float(latest['RSI']) if 'RSI' in df.columns else 50.0
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
                
                # Generate AI advice (optimized to preserve quota)
                # Only use AI for high-priority or significant alerts
                use_ai = (
                    priority in ['high', 'medium'] and  # Only high/medium priority
                    (volume_ratio > 2.5 or abs(sentiment_score) > 0.5) and  # Significant activity
                    self.sentiment_analyzer.model is not None  # AI is available
                )
                
                if use_ai:
                    try:
                        advice = self.sentiment_analyzer.generate_stock_advice(
                            ticker, current_price, price_change, volume_ratio, sentiment_score
                        )
                        # Delay to respect API rate limits (10 requests/minute)
                        time.sleep(6)  # 10 requests/min = 6 sec between requests
                    except Exception as e:
                        logger.debug(f"AI advice unavailable for {ticker}, using rule-based: {e}")
                        # Falls through to rule-based advice below
                        use_ai = False
                
                if not use_ai:
                    # Use enhanced rule-based advice
                    sentiment_desc = "bullish" if sentiment_score > 0.3 else "bearish" if sentiment_score < -0.3 else "neutral"
                    volume_desc = "extremely high" if volume_ratio > 3 else "elevated" if volume_ratio > 2 else "moderate"
                    
                    advice_parts = []
                    advice_parts.append(f"{ticker} is experiencing {volume_desc} trading volume at {volume_ratio:.1f}x the average")
                    
                    if abs(price_change) > 5:
                        direction = "surging" if price_change > 0 else "declining sharply"
                        advice_parts.append(f"with the price {direction} by {abs(price_change):.1f}%")
                    elif abs(price_change) > 2:
                        direction = "rising" if price_change > 0 else "falling"
                        advice_parts.append(f"while {direction} by {abs(price_change):.1f}%")
                    else:
                        advice_parts.append(f"with relatively stable pricing ({price_change:+.1f}%)")
                    
                    if abs(sentiment_score) > 0.5:
                        advice_parts.append(f"Social sentiment is strongly {sentiment_desc} ({sentiment_score:+.1f})")
                    elif abs(sentiment_score) > 0.3:
                        advice_parts.append(f"showing {sentiment_desc} sentiment ({sentiment_score:+.1f})")
                    
                    if volume_ratio > 3 and abs(price_change) > 3:
                        recommendation = "This combination of high volume and significant price movement suggests heightened volatility. Consider waiting for stabilization before entering positions"
                    elif volume_ratio > 3:
                        recommendation = "The unusual volume spike warrants close monitoring for potential breakout or breakdown patterns"
                    elif volume_ratio > 2:
                        recommendation = "Watch for confirmation of trend direction before taking positions"
                    else:
                        recommendation = "Monitor for volume confirmation before acting"
                    
                    advice_parts.append(recommendation + ".")
                    advice = ". ".join(advice_parts)
                
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
                        'rsi': round(rsi, 2),
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

