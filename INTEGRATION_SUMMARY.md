# Backend Integration Summary

## Overview
Successfully integrated RSI calculations and metrics with the multi-user email system. The backend now uses a unified database-driven architecture.

## Architecture

### Data Flow
```
[Stock Data] → [stock_analysis.py] → [alerts.db] → [integrated_backend.py API] → [Frontend GUI]
                        ↓
                [Email Notifications]
```

## Components

### 1. **stock_analysis.py** (Data Processing + Emails)
**What it does:**
- Fetches stock data (currently mock, ready for real web scraping)
- Calculates all metrics:
  - ✅ RSI (Relative Strength Index)
  - ✅ Volume Z-Score
  - ✅ Volume Ratio
  - ✅ Price Change %
  - ✅ Sentiment Score (mock, ready for real scraping)
  - ✅ Mention Count (mock, ready for real scraping)
- Updates `latest_alerts` table in database
- **Sends multi-user emails** based on individual preferences
- Tracks sent alerts to avoid duplicates

**Key Features:**
- Only sends emails for **newly triggered** alerts
- Filters by user preferences (High/Medium/Low)
- Maintains active alerts with trigger volume tracking

### 2. **integrated_backend.py** (API Server)
**What it does:**
- Flask API server on port 5001
- **Prioritizes database data** from stock_analysis.py
- Falls back to live calculation if database is empty
- Provides `/api/alerts` endpoint for frontend
- Includes Gemini AI for sentiment analysis (when needed)

**Key Features:**
- Reads from database first (fast, consistent)
- Generates AI advice for alerts
- Caching for performance
- Seamless fallback to live data

### 3. **scheduler.py** (Automation)
**What it does:**
- Runs `stock_analysis.py` every 30 minutes
- Runs immediately on startup
- Logs all operations

**Usage:**
```bash
python backend/scheduler.py
```

### 4. **apps.py** (FastAPI - Alternative API)
**What it does:**
- FastAPI server on port 8000
- Provides `/latest-alerts` endpoint
- Manages user preferences
- Reads from same database as integrated_backend

**Endpoints:**
- `POST /preferences` - Save user email + alert preferences
- `GET /preferences/{email}` - Get user preferences
- `GET /latest-alerts` - Get current alerts with all metrics

## Database Schema

### Table: `latest_alerts`
```sql
Ticker TEXT PRIMARY KEY,
Close REAL,                  -- Current price
Volume INTEGER,              -- Current volume
volume_z REAL,              -- Volume Z-Score
Volume_Ratio REAL,          -- Volume vs average
Volume_Alert TEXT,          -- "High Alert", "Medium Alert", "Low Alert"
RSI REAL,                   -- RSI indicator (0-100)
Price_Change REAL,          -- % change
Sentiment_Score REAL,       -- Sentiment (-1 to 1)
Mention_Count INTEGER,      -- Social media mentions
Timestamp TEXT              -- Last update time
```

### Table: `user_prefs`
```sql
email TEXT PRIMARY KEY,
high_alerts INTEGER,        -- 1 = enabled, 0 = disabled
medium_alerts INTEGER,
low_alerts INTEGER,
enabled INTEGER,            -- Master enable/disable
created_at TIMESTAMP
```

### Table: `active_alerts`
```sql
Ticker TEXT PRIMARY KEY,
Alert_Level TEXT,
Trigger_Volume REAL,        -- Volume that triggered alert
Timestamp TEXT
```

### Table: `sent_alerts`
```sql
id INTEGER PRIMARY KEY,
email TEXT,
ticker TEXT,
priority TEXT,
alert_id TEXT,
sent_at TIMESTAMP,
UNIQUE(email, alert_id)     -- Prevents duplicate emails
```

## How to Run

### Development Mode (3 separate terminals)

**Terminal 1: Scheduler (Data Processing + Emails)**
```bash
cd NewHacks-2025
python backend/scheduler.py
```

**Terminal 2: Integrated Backend (Main API)**
```bash
cd NewHacks-2025
python backend/integrated_backend.py
```

**Terminal 3: Frontend**
```bash
cd NewHacks-2025/meme-stock-dashboard
npm run dev
```

### Alternative: FastAPI Backend
```bash
uvicorn backend.apps:app --reload --port 8000
```

## Features Implemented

### ✅ Multi-User Email System
- Each user registers with email + preferences (High/Medium/Low alerts)
- System sends personalized emails based on preferences
- Tracks sent alerts to prevent spam
- Only sends emails for newly triggered alerts
- Works independently of browser (scheduled)

### ✅ Comprehensive Metrics
- **RSI**: Technical indicator (0-100)
  - >70: Overbought (red in GUI)
  - <30: Oversold (green in GUI)
  - 30-70: Neutral (blue in GUI)
- **Volume Z-Score**: Statistical measure of volume spike
- **Sentiment Score**: Social media sentiment (-1 to 1)
  - >0.5: Bullish (green)
  - <-0.5: Bearish (red)
  - -0.5 to 0.5: Neutral (yellow)
- **Volume Ratio**: Current volume vs average
- **Price Change**: % change
- **Mention Count**: Social media activity

### ✅ Smart Alert Management
- Alerts remain active while volume stays elevated
- Automatic removal when volume normalizes
- Priority classification (High/Medium/Low/Normal)
- Z-score based thresholds:
  - ≥4.0: High Alert
  - ≥2.5: Medium Alert
  - ≥1.5: Low Alert

### ✅ GUI Integration
The frontend `StockCard` component displays all 7 metrics:
1. Mentions
2. Volume Ratio
3. RSI (color-coded)
4. Volume Z-Score
5. Sentiment (color-coded)
6. Detected Time
7. Status

## Next Steps for Production

### 1. Replace Mock Data with Real Web Scraping
Update `stock_analysis.py`:
```python
# Replace this:
from backend.web_scraped_mock import target_tickers, stock_data

# With real scraping:
from backend.web_scraper import fetch_reddit_data, fetch_stock_data
```

Implement `backend/web_scraper.py` using:
- **Reddit API (PRAW)** for r/wallstreetbets
- **yfinance** for real stock data
- **BeautifulSoup** for additional sources

### 2. Environment Variables
Create `.env` file:
```
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
GEMINI_API_KEY=your-gemini-key
DATABASE_PATH=backend/alerts.db
REFRESH_INTERVAL_MINUTES=30
```

### 3. Deploy Scheduler as Service
Use systemd, supervisor, or PM2 to keep scheduler running:
```bash
pm2 start backend/scheduler.py --name stock-scheduler
pm2 startup
pm2 save
```

### 4. Rate Limiting
Add rate limiting to prevent API abuse:
- Reddit: 60 requests/minute
- Gemini: 10 requests/minute
- Email: Configure sending limits

## Testing

### Test Email System
1. Add your email via GUI settings
2. Run `stock_analysis.py` manually:
   ```bash
   python backend/stock_analysis.py
   ```
3. Check your inbox for alerts

### Test API
```bash
# Get current alerts
curl http://localhost:5001/api/alerts

# Get alerts with refresh
curl http://localhost:5001/api/alerts?refresh=true
```

### Test Database
```bash
sqlite3 backend/alerts.db
sqlite> SELECT * FROM latest_alerts;
sqlite> SELECT * FROM user_prefs;
sqlite> SELECT * FROM sent_alerts;
```

## Files Modified

1. ✅ `backend/stock_analysis.py` - Added sentiment, mention count, price change
2. ✅ `backend/integrated_backend.py` - Database integration, RSI calculation
3. ✅ `backend/scheduler.py` - Improved logging and documentation
4. ✅ `backend/apps.py` - Updated API to return all metrics
5. ✅ `meme-stock-dashboard/src/types/index.ts` - Added new fields
6. ✅ `meme-stock-dashboard/src/components/StockCard.tsx` - Display all metrics
7. ✅ `meme-stock-dashboard/src/data/mockData.ts` - Updated with new fields

## Summary

The system is now fully integrated with:
- ✅ Unified database architecture
- ✅ Multi-user email system
- ✅ All metrics (RSI, sentiment, volume z-score)
- ✅ Automated scheduling
- ✅ GUI displaying all data
- ✅ Fallback mechanisms for reliability
- ✅ No duplicate emails
- ✅ Per-user preference filtering

Ready for production after replacing mock data with real web scraping!

