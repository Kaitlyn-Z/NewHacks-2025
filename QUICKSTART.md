# 🚀 Quick Start Guide

Get your Meme Stock Dashboard running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check npm
npm --version
```

## Step 1: Get Gemini API Key (2 minutes)

### Gemini AI API Key (Required)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key - you'll need it for sentiment analysis

## Step 2: Setup (1 minute)

```bash
# Clone/navigate to project
cd /path/to/NewHacks-2025

# Create API keys file
cp api_keys.py.example api_keys.py

# Edit with your keys
nano api_keys.py  # or use any text editor
```

Edit `api_keys.py` to add your Gemini API key:
```python
GEMINI_API_KEY = "your_actual_gemini_key_here"
```

## Step 3: Install Dependencies (1 minute)

```bash
# Install Python packages
pip3 install -r requirements.txt

# Install Node.js packages
cd meme-stock-dashboard
npm install
cd ..
```

## Step 4: Start Everything (30 seconds)

### Option A: One-Command Start (Recommended)
```bash
./start-all-services.sh
```

### Option B: Manual Start (if script doesn't work)

**Terminal 1 - Integrated Backend:**
```bash
cd backend
python3 integrated_backend.py
```

**Terminal 2 - Email Backend:**
```bash
cd meme-stock-dashboard/python-backend
PORT=5002 python3 app.py
```

**Terminal 3 - Frontend:**
```bash
cd meme-stock-dashboard
npm run dev
```

## Step 5: Open Dashboard

Open your browser and go to:
```
http://localhost:3000
```

🎉 **Done!** You should see the dashboard with live stock alerts!

## 🎛️ Configure Email Notifications (Optional)

1. Click the "Email Settings" button in the dashboard
2. Enter your email address
3. Click "Save"
4. Test by clicking "Send Test Email"

**Note**: The email feature uses a pre-configured Gmail account. For production, update the SMTP settings in `meme-stock-dashboard/python-backend/app.py`.

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'api_keys'"
**Solution**: Copy `api_keys.py.example` to `api_keys.py` and add your keys.

### "Port already in use"
**Solution**: Kill the process or change the port:
```bash
# Kill process on port 5001
lsof -ti:5001 | xargs kill -9
```

### No data showing in dashboard
**Solution**: 
1. Check backend is running (http://localhost:5001/health)
2. Check browser console for errors (F12)
3. Wait 30 seconds for first data fetch
4. Verify your Gemini API key is correct in `api_keys.py`

## 📊 What to Expect

- **Initial Load**: Takes ~10 seconds to fetch stock data
- **Auto-Refresh**: Every 30 seconds
- **Email Alerts**: Sent for high-priority alerts only
- **Tickers Monitored**: 9 default stocks

## 🎯 Next Steps

1. **Customize Tickers**: Edit `backend/integrated_backend.py` → `TARGET_TICKERS`
2. **Adjust Thresholds**: Edit alert thresholds in `VolumeAnalyzer.classify_alert()`
3. **Enhance Sentiment Data**: Replace `MOCK_POSTS` with enhanced data sources

## 📞 Need Help?

- Check `logs/` directory for error messages
- Ensure all 3 services are running (check ports 3000, 5001, 5002)
- Verify API keys are correct in `api_keys.py`

---

**Happy Trading! 📈** (Not financial advice)


