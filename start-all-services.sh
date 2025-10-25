#!/bin/bash

# Start All Meme Stock Dashboard Services
# This script starts:
# 1. Integrated Backend (port 5001) - Stock data + Sentiment analysis
# 2. Email Backend (port 5002) - Email notifications
# 3. Next.js Frontend (port 3000) - Dashboard UI

set -e

echo "🚀 Starting Meme Stock Dashboard Services..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check for api_keys.py
if [ ! -f "api_keys.py" ]; then
    echo "⚠️  Warning: api_keys.py not found. Copying from example..."
    if [ -f "api_keys.py.example" ]; then
        cp api_keys.py.example api_keys.py
        echo "📝 Please edit api_keys.py and add your actual API keys."
        exit 1
    fi
fi

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip3 install -r requirements.txt > /dev/null 2>&1 || {
    echo "⚠️  Some dependencies may have failed to install, continuing anyway..."
}

# Install Node.js dependencies
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
cd meme-stock-dashboard
npm install > /dev/null 2>&1 || echo "⚠️  npm install had some warnings, continuing..."
cd ..

# Create log directory
mkdir -p logs

echo ""
echo -e "${GREEN}✅ Dependencies installed!${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start Integrated Backend
echo -e "${BLUE}🔧 Starting Integrated Backend (port 5001)...${NC}"
cd backend
python3 integrated_backend.py > ../logs/integrated_backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 2

# Start Email Backend
echo -e "${BLUE}📧 Starting Email Backend (port 5002)...${NC}"
cd meme-stock-dashboard/python-backend
PORT=5002 python3 app.py > ../../logs/email_backend.log 2>&1 &
EMAIL_PID=$!
cd ../..
sleep 2

# Start Next.js Frontend
echo -e "${BLUE}🌐 Starting Next.js Frontend (port 3000)...${NC}"
cd meme-stock-dashboard
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

echo ""
echo "================================================"
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo "================================================"
echo ""
echo "📊 Service URLs:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Integrated Backend: http://localhost:5001"
echo "   Email Backend:      http://localhost:5002"
echo ""
echo "📋 Service Status:"
echo "   Integrated Backend PID: $BACKEND_PID"
echo "   Email Backend PID:      $EMAIL_PID"
echo "   Frontend PID:           $FRONTEND_PID"
echo ""
echo "📝 Logs location: ./logs/"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background processes
wait

