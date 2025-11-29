#!/bin/bash

# Start AI CCTV Face Recognition System with Gunicorn (Production Mode)

cd /home/isha/face_recognition_system || exit 1

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing gunicorn..."
    pip install gunicorn
fi

# Check if port 5000 is in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Port 5000 is already in use. Killing existing process..."
    kill -9 $(lsof -t -i:5000) 2>/dev/null || pkill -f "gunicorn" 2>/dev/null
    sleep 2
fi

# Start the application with gunicorn
PORT=${PORT:-5000}
echo "Starting AI CCTV Face Recognition System with Gunicorn (Production Mode)..."
echo "Access at: http://localhost:${PORT}"
echo "Health check: http://localhost:${PORT}/health"
echo ""
echo "Press CTRL+C to stop"
echo ""

# Use exact same command as Dockerfile for production testing
gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 300 --keepalive 5 --access-logfile - --error-logfile - --log-level info --preload web_app:app

