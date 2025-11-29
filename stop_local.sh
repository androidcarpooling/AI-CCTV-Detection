#!/bin/bash

# Stop AI CCTV Face Recognition System

echo "Stopping AI CCTV Face Recognition System..."

# Kill by port
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    kill -9 $(lsof -t -i:5000) 2>/dev/null
    echo "Stopped process on port 5000"
fi

# Kill by process name
pkill -f "web_app.py" 2>/dev/null && echo "Stopped web_app.py processes"

echo "Done!"

