#!/bin/bash
# Startup script for the face recognition system

echo "Starting AI CCTV Face Recognition System..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if models exist
if [ ! -d "$HOME/.insightface/models/buffalo_l" ]; then
    echo "Models not found. They will be downloaded on first run."
fi

# Run the web application
python web_app.py

