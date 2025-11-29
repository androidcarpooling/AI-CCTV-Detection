# Production Setup Testing Guide

## Git Tag for Working Version

Tag the current working version:
```bash
cd /home/isha/face_recognition_system
git tag -a v1.0.0-working -m "Working version with Gunicorn production setup"
git push origin v1.0.0-working
```

To restore this version later:
```bash
git checkout v1.0.0-working
```

## Test Production Setup Locally

### Option 1: Quick Test Script
```bash
cd /home/isha/face_recognition_system
./test_production.sh
```

This script will:
- Start Gunicorn with production settings
- Test health endpoint
- Test root endpoint
- Keep server running until CTRL+C

### Option 2: Manual Production Start
```bash
cd /home/isha/face_recognition_system
source venv/bin/activate

# Install gunicorn if not installed
pip install gunicorn

# Kill any existing processes
pkill -f gunicorn
pkill -f web_app.py

# Start with production settings (matches Dockerfile)
export PORT=5000
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 300 --keepalive 5 --access-logfile - --error-logfile - --log-level info --preload web_app:app
```

### Option 3: Using Start Script
```bash
cd /home/isha/face_recognition_system
./start_production.sh
```

## Test Endpoints

Once running, test these:
```bash
# Health check
curl http://localhost:5000/health

# Root endpoint
curl http://localhost:5000/

# Stats API
curl http://localhost:5000/api/stats
```

## Production Settings (Matches Railway)

- **Workers**: 2
- **Threads**: 4 per worker
- **Timeout**: 300 seconds (for video processing)
- **Keepalive**: 5 seconds
- **Preload**: Enabled (loads app before forking workers)
- **Logging**: Access and error logs to stdout

## Railway Configuration

Make sure Railway settings match:
- **Target Port**: `8080` (or leave empty for auto-detection)
- **Health Check Path**: `/health` (optional, but recommended)

