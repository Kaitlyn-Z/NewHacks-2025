# How to Start the Auto-Refreshing System

## Overview
The system has 3 main components that need to run simultaneously:

1. **Scheduler** - Auto-updates stock data every 30 minutes
2. **Backend API** - Serves data to the frontend
3. **Frontend** - Displays the dashboard

## Quick Start (4 Terminals)

### Terminal 1: Email Service (Port 5002)
```bash
cd NewHacks-2025/meme-stock-dashboard/python-backend
python3 app.py
```

**What it does:**
- ✅ Runs email service on port 5002
- ✅ Handles test emails from frontend
- ✅ Stores user preferences in memory
- ✅ Pre-configured with Gmail SMTP

**You should see:**
```
INFO:__main__:Starting Email Service on port 5002
 * Running on http://0.0.0.0:5002
```

### Terminal 2: Scheduler (Auto-Refresh Every 30 Minutes)
```bash
cd NewHacks-2025
python3 backend/scheduler.py
```

**What it does:**
- Runs `stock_analysis.py` immediately on startup
- Then runs it every 30 minutes automatically
- Updates `alerts.db` with latest stock data
- Sends emails to users based on their preferences
- Calculates: RSI, Volume Z-Score, Sentiment, Price Changes

**You should see:**
```
INFO:__main__:Running initial stock analysis...
INFO:__main__:Running stock analysis...
INFO:__main__:Stock analysis completed successfully
INFO:__main__:Scheduler started. Running every 30 minutes...
```

### Terminal 3: Backend API (Port 5001)
```bash
cd NewHacks-2025
python3 backend/integrated_backend.py
```

**What it does:**
- Runs Flask API on port 5001
- Serves `/api/alerts` endpoint to frontend
- Reads from database (updated by scheduler)
- Falls back to live calculation if database is empty

**You should see:**
```
INFO:integrated_backend:Starting Integrated Backend on port 5001
 * Running on http://0.0.0.0:5001
```

### Terminal 4: Frontend (Port 3000)
```bash
cd NewHacks-2025/meme-stock-dashboard
npm run dev
```

**What it does:**
- Runs Next.js frontend on port 3000
- Auto-refreshes every 30 seconds
- Displays all metrics from backend

**You should see:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

## Optional: FastAPI Backend (for Database Preferences)

If you want to save user preferences to the database (for scheduled emails):

### Terminal 5 (Optional):
```bash
cd NewHacks-2025
uvicorn backend.apps:app --reload --port 8000
```

**Note:** The email service (Terminal 1) handles test emails and immediate notifications. 
The FastAPI backend saves preferences to the database for the scheduler to use.

## How Auto-Refresh Works

### Backend (Every 30 minutes)
```
Scheduler runs → stock_analysis.py
    ↓
1. Fetch stock data
2. Calculate RSI, volume metrics
3. Generate sentiment scores
4. Update database (alerts.db)
5. Send emails to users
    ↓
Backend API reads from updated database
```

### Frontend (Every 30 seconds)
```
Frontend timer → Fetch from /api/alerts
    ↓
Display updated data on dashboard
```

## Verify It's Working

### Check Database
```bash
sqlite3 backend/alerts.db "SELECT * FROM latest_alerts"
```

### Check Scheduler Status
Look for this log every 30 minutes:
```
INFO:__main__:Running stock analysis...
INFO:__main__:Stock analysis completed successfully
```

### Check Frontend
- Dashboard should show "Last updated: [current time]"
- Data refreshes every 30 seconds
- Backend data updates every 30 minutes

## Troubleshooting

### Scheduler not running?
```bash
# Check if it's running
ps aux | grep scheduler.py

# Kill if stuck
pkill -f scheduler.py

# Restart
python3 backend/scheduler.py
```

### Database not updating?
```bash
# Run stock_analysis manually
python3 backend/stock_analysis.py

# Check if database updated
sqlite3 backend/alerts.db "SELECT Timestamp FROM latest_alerts"
```

### Frontend not refreshing?
- Check browser console for errors
- Verify backend is running on port 5001
- Check "Last updated" time in header

## Production Setup

For production, use PM2 or systemd to keep services running:

```bash
# Install PM2
npm install -g pm2

# Start scheduler
pm2 start backend/scheduler.py --name scheduler --interpreter python3

# Start backend
pm2 start backend/integrated_backend.py --name backend --interpreter python3

# Start frontend
cd meme-stock-dashboard && pm2 start npm --name frontend -- start

# Save configuration
pm2 save
pm2 startup

# Monitor
pm2 monit
```

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    SCHEDULER (30 min)                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  stock_analysis.py                                  │  │
│  │  • Fetch stock data                                │  │
│  │  • Calculate RSI, volume metrics, sentiment        │  │
│  │  • Update alerts.db database                       │  │
│  │  • Send emails to users                            │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │ Updates
                         ▼
              ┌─────────────────────┐
              │     alerts.db       │
              │  (SQLite Database)  │
              └──────────┬──────────┘
                         │ Reads
                         ▼
┌──────────────────────────────────────────────────────────┐
│              BACKEND API (Flask - Port 5001)              │
│  ┌────────────────────────────────────────────────────┐  │
│  │  integrated_backend.py                             │  │
│  │  • GET /api/alerts                                 │  │
│  │  • Reads from database                             │  │
│  │  • Falls back to live calculation                  │  │
│  └────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────┘
                         │ API Calls
                         ▼
┌──────────────────────────────────────────────────────────┐
│           FRONTEND (Next.js - Port 3000)                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Dashboard                                          │  │
│  │  • Auto-refreshes every 30 seconds                 │  │
│  │  • Displays: RSI, Sentiment, Volume Z-Score        │  │
│  │  • Shows: Price, Mentions, Status                  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Key Features

✅ **Auto-updates every 30 minutes** (backend data)
✅ **Auto-refreshes every 30 seconds** (frontend display)
✅ **Multi-user email system** with preference filtering
✅ **Persistent data** in SQLite database
✅ **All metrics**: RSI, Sentiment, Volume Z-Score, Price Change
✅ **Email notifications** for new alerts only (no duplicates)

## Next Steps

1. Start all 3 terminals as shown above
2. Open http://localhost:3000 in your browser
3. Watch the scheduler logs for 30-minute updates
4. Set up your email preferences in the GUI
5. Wait for the next alert cycle to receive emails

