#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AI CCTV Face Recognition - Local Test${NC}"
echo -e "${GREEN}========================================${NC}"

# Navigate to project directory
cd /home/isha/face_recognition_system || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if port 5000 is in use
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Port 5000 is already in use.${NC}"
    echo -e "${YELLOW}Killing existing process...${NC}"
    kill -9 $(lsof -t -i:5000) 2>/dev/null || pkill -f "web_app.py" 2>/dev/null
    sleep 2
fi

# Start the application in background
echo -e "${GREEN}Starting Flask application...${NC}"
python3 web_app.py > /tmp/flask_app.log 2>&1 &
APP_PID=$!

# Wait for app to start
echo -e "${YELLOW}Waiting for app to start (5 seconds)...${NC}"
sleep 5

# Check if app is running
if ! kill -0 $APP_PID 2>/dev/null; then
    echo -e "${RED}ERROR: Application failed to start!${NC}"
    echo -e "${RED}Check logs:${NC}"
    cat /tmp/flask_app.log
    exit 1
fi

echo -e "${GREEN}Application started successfully!${NC}"
echo -e "${GREEN}PID: $APP_PID${NC}"
echo ""

# Test Health Endpoint
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Health Endpoint${NC}"
echo -e "${GREEN}========================================${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
echo "Response: $HEALTH_RESPONSE"
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Health check passed!${NC}"
else
    echo -e "${RED}✗ Health check failed!${NC}"
fi
echo ""

# Test Stats Endpoint
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Stats Endpoint${NC}"
echo -e "${GREEN}========================================${NC}"
STATS_RESPONSE=$(curl -s http://localhost:5000/api/stats)
echo "Response: $STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"
echo ""

# Test Events Endpoint
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Events Endpoint${NC}"
echo -e "${GREEN}========================================${NC}"
EVENTS_RESPONSE=$(curl -s "http://localhost:5000/api/events?limit=5")
echo "Response: $EVENTS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$EVENTS_RESPONSE"
echo ""

# Test Main Page
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Testing Main Page${NC}"
echo -e "${GREEN}========================================${NC}"
MAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$MAIN_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ Main page accessible (HTTP $MAIN_RESPONSE)${NC}"
else
    echo -e "${RED}✗ Main page failed (HTTP $MAIN_RESPONSE)${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Application URL: ${GREEN}http://localhost:5000${NC}"
echo -e "Health Check: ${GREEN}http://localhost:5000/health${NC}"
echo -e "Dashboard: ${GREEN}http://localhost:5000/${NC}"
echo -e "API Stats: ${GREEN}http://localhost:5000/api/stats${NC}"
echo ""
echo -e "${YELLOW}Application is running in background (PID: $APP_PID)${NC}"
echo -e "${YELLOW}To stop the application, run:${NC}"
echo -e "${YELLOW}  kill $APP_PID${NC}"
echo -e "${YELLOW}Or:${NC}"
echo -e "${YELLOW}  pkill -f web_app.py${NC}"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo -e "${YELLOW}  tail -f /tmp/flask_app.log${NC}"

