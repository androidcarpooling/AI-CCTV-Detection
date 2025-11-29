#!/bin/bash

# Test Production Setup Locally (Mock Railway Environment)

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Production Setup (Gunicorn)${NC}"
echo -e "${GREEN}========================================${NC}"

cd /home/isha/face_recognition_system || exit 1

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}ERROR: Virtual environment not found${NC}"
    exit 1
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}Installing gunicorn...${NC}"
    pip install gunicorn
fi

# Kill any existing processes
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
pkill -f "gunicorn" 2>/dev/null
pkill -f "web_app.py" 2>/dev/null
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    kill -9 $(lsof -t -i:5000) 2>/dev/null
fi
sleep 2

# Set PORT (simulate Railway)
export PORT=5000

# Start Gunicorn in background
echo -e "${GREEN}Starting Gunicorn (Production Mode)...${NC}"
echo -e "${YELLOW}Command: gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - --log-level info --preload web_app:app${NC}"
echo ""

gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - --log-level info --preload web_app:app &
GUNICORN_PID=$!

# Wait for server to start
echo -e "${YELLOW}Waiting for server to start...${NC}"
sleep 5

# Test health endpoint
echo -e "${GREEN}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/health)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP $HEALTH_RESPONSE)${NC}"
    curl -s http://localhost:${PORT}/health | python3 -m json.tool
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH_RESPONSE)${NC}"
fi

echo ""
echo -e "${GREEN}Testing root endpoint...${NC}"
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/)
if [ "$ROOT_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Root endpoint works (HTTP $ROOT_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Root endpoint failed (HTTP $ROOT_RESPONSE)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server is running!${NC}"
echo -e "${GREEN}Access at: http://localhost:${PORT}${NC}"
echo -e "${GREEN}Health: http://localhost:${PORT}/health${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Wait for user interrupt
trap "echo ''; echo -e '${YELLOW}Stopping server...${NC}'; kill $GUNICORN_PID 2>/dev/null; exit 0" INT TERM

# Keep script running
wait $GUNICORN_PID

