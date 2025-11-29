#!/bin/bash

# Start AI CCTV Face Recognition System Locally

cd /home/isha/face_recognition_system || exit 1

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Check if port 5000 is in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Port 5000 is already in use. Killing existing process..."
    kill -9 $(lsof -t -i:5000) 2>/dev/null || pkill -f "web_app.py" 2>/dev/null
    sleep 2
fi

# Start the application
echo "Starting AI CCTV Face Recognition System..."
echo "Access at: http://localhost:5000"
echo "Health check: http://localhost:5000/health"
echo ""
echo "Press CTRL+C to stop"
echo ""

python3 web_app.py

