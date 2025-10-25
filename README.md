# 🚀 Meme Stock Alert Dashboard

A real-time stock monitoring system that combines **volume analysis**, **social sentiment analysis**, and **email notifications** to detect potential meme stock momentum.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-green) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Next.js](https://img.shields.io/badge/Next.js-14-black)

## 🎯 Features

- **📊 Real-time Volume Analysis**: Detects unusual trading volume spikes using statistical z-scores
- **🤖 AI-Powered Sentiment**: Uses Google's Gemini AI to analyze sentiment
- **📧 Email Alerts**: Automatic notifications for high-priority stock movements
- **📈 Beautiful Dashboard**: Modern, responsive UI with real-time updates
- **🔄 Auto-Refresh**: Continuous monitoring with configurable refresh intervals
- **⚡ Fast & Efficient**: Built with Flask backend and Next.js frontend

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Next.js Dashboard (Port 3000)          │
│                     - Real-time UI                      │
│                     - Auto-refresh                      │
│                     - Email settings                    │
└────────────────┬──────────────────┬─────────────────────┘
                 │                  │
        ┌────────▼────────┐  ┌─────▼──────────┐
        │ Integrated      │  │ Email Backend  │
        │ Backend         │  │ (Port 5002)    │
        │ (Port 5001)     │  │ - SMTP Service │
        │ - Volume        │  │ - Notifications│
        │   Analysis      │  └────────────────┘
        │ - Sentiment AI  │
        │ - Stock Data    │
        └─────────────────┘
                 │
        ┌────────▼────────┐
        │   yFinance      │
        │   Gemini AI     │
        │   Data Sources  │
        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey)) - Required for AI sentiment analysis

### Installation

1. **Clone the repository**
```bash
cd /path/to/NewHacks-2025
```

2. **Set up API keys**
```bash
cp api_keys.py.example api_keys.py
# Edit api_keys.py and add your Gemini API key
```

3. **Install dependencies**
```bash
pip3 install -r requirements.txt
cd meme-stock-dashboard && npm install && cd ..
```

4. **Start all services**
```bash
./start-all-services.sh
```

The dashboard will be available at **http://localhost:3000**

## 📚 Manual Setup (Alternative)

If you prefer to start services individually:

### 1. Start Integrated Backend
```bash
cd backend
python3 integrated_backend.py
# Runs on port 5001
```

### 2. Start Email Backend
```bash
cd meme-stock-dashboard/python-backend
PORT=5002 python3 app.py
# Runs on port 5002
```

### 3. Start Frontend
```bash
cd meme-stock-dashboard
npm run dev
# Runs on port 3000
```

## 🔧 Configuration

### Monitored Tickers

Edit `backend/integrated_backend.py`:
```python
TARGET_TICKERS = ["GME", "AMC", "BB", "TSLA", "NVDA", ...]
```

### Alert Thresholds

Volume z-score thresholds (in `backend/integrated_backend.py`):
```python
z >= 4.0   → High Alert
z >= 2.5   → Medium Alert
z >= 1.5   → Low Alert
z < 1.5    → Normal
```

### Refresh Intervals

- Frontend: 30 seconds (configurable in `page.tsx`)
- Backend cache: 30 seconds (configurable in `integrated_backend.py`)

## 📊 API Endpoints

### Integrated Backend (Port 5001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/alerts` | GET | Get all stock alerts |
| `/api/alerts?refresh=true` | GET | Force refresh alerts |
| `/api/stock/<ticker>` | GET | Get detailed stock info |
| `/api/stats` | GET | Get system statistics |
| `/health` | GET | Health check |

### Email Backend (Port 5002)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/email` | POST | Send email notifications |
| `/api/email` | GET | Get email service info |
| `/health` | GET | Health check |

## 🧪 Example API Response

```json
{
  "success": true,
  "alerts": [
    {
      "id": "GME-1234567890",
      "ticker": "GME",
      "mentionCount": 247,
      "volumeRatio": 4.2,
      "currentPrice": 23.45,
      "priceChange": 12.5,
      "detectedAt": "2025-10-25T10:30:00Z",
      "priority": "high",
      "sentimentScore": 0.85,
      "volumeZScore": 4.3
    }
  ],
  "count": 1,
  "timestamp": "2025-10-25T10:30:00Z"
}
```

## 🎨 Features Breakdown

### Volume Analysis
- Calculates 50-day rolling average and standard deviation
- Computes z-scores for volume spikes
- Detects anomalies in real-time

### Sentiment Analysis
- Powered by Google Gemini AI
- Analyzes social media posts
- Returns bullish/bearish/neutral sentiment
- Sentiment scores from -1 (bearish) to +1 (bullish)

### Email Notifications
- Beautiful HTML email templates
- Priority-based notifications
- Configurable recipients
- Failed notification tracking

## 📁 Project Structure

```
NewHacks-2025/
├── backend/
│   ├── gemini.py              # Original Gemini integration
│   └── integrated_backend.py  # Main integrated backend
├── meme-stock-dashboard/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx       # Main dashboard
│   │   │   └── api/           # API routes
│   │   ├── components/        # React components
│   │   └── types/             # TypeScript types
│   ├── python-backend/
│   │   └── app.py             # Email backend
│   └── package.json
├── requirements.txt           # Python dependencies
├── api_keys.py.example        # API key template
├── start-all-services.sh      # Startup script
└── README.md
```

## 🔐 Security Notes

- Never commit `api_keys.py` to version control
- Use environment variables for production
- Email credentials should be app-specific passwords
- CORS is enabled for development (restrict in production)

## 🐛 Troubleshooting

### "No module named 'api_keys'"
- Copy `api_keys.py.example` to `api_keys.py`
- Add your Gemini API key

### Port already in use
```bash
# Find and kill process on port 5001
lsof -ti:5001 | xargs kill -9

# Or change ports in the configuration files
```

### Email not sending
- Verify Gmail app password is correct
- Check SMTP settings in `python-backend/app.py`
- Ensure "Less secure app access" is enabled (if using regular password)

### No stock data
- Check internet connection
- yfinance may have rate limits
- Some tickers might not be available

## 🚧 Future Enhancements

- [ ] Enhanced sentiment data sources
- [ ] Historical trend analysis
- [ ] Machine learning price prediction
- [ ] Mobile app
- [ ] WebSocket support for real-time updates
- [ ] User authentication
- [ ] Multiple watchlists
- [ ] Custom alert thresholds per stock

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

Built with ❤️ for NewHacks 2025

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for stock data
- [Google Gemini](https://ai.google.dev/) for AI sentiment analysis
- [Next.js](https://nextjs.org/) for the frontend framework
- [Flask](https://flask.palletsprojects.com/) for the backend

---

**Note**: This is a hackathon project for educational purposes. Not financial advice. Trade responsibly! 📈
