#!/bin/bash

echo "🚀 Starting Meme Stock Dashboard with Python Email Service"
echo "=========================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "📧 Starting Python Email Service..."
cd python-backend

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start Python backend in background
python3 run.py &
PYTHON_PID=$!

echo "✅ Python Email Service started (PID: $PYTHON_PID)"
echo "🌐 Python API: http://localhost:5000"

# Go back to root directory
cd ..

echo "🎨 Starting React Frontend..."
# Start React frontend
npm run dev &
REACT_PID=$!

echo "✅ React Frontend started (PID: $REACT_PID)"
echo "🌐 React App: http://localhost:3000"

echo ""
echo "🎉 Both services are running!"
echo "📧 Python Email Service: http://localhost:5000"
echo "🎨 React Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait
