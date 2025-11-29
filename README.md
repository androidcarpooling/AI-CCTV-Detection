# 🎥 AI CCTV Face Recognition System

A production-ready, cloud-deployable face recognition system using InsightFace's SCRFD detector and ArcFace recognition model. Designed for CCTV monitoring, video analysis, and real-time face matching.

## ✨ Features

- **🎯 High Accuracy**: SCRFD detector + ArcFace recognition (state-of-the-art)
- **🌐 Web Interface**: Modern, intuitive UI for uploading photos/videos and viewing results
- **☁️ Cloud Ready**: Docker containerized for easy deployment to AWS, GCP, Azure, Railway, etc.
- **📹 Multiple Input Sources**: Images, video files, RTSP CCTV feeds
- **💾 Flexible Database**: SQLite (default), PostgreSQL, Redis support
- **⚡ Real-Time Processing**: Fast cosine similarity matching (100k+ embeddings in <5ms)
- **🔔 Event System**: Alerts, logs, tracking, webhooks
- **📊 Dashboard**: Real-time monitoring and statistics

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)

1. **Start the web application:**
```bash
python web_app.py
```

2. **Open browser:** http://localhost:5000

3. **Upload blacklist photos** in the "Blacklist Management" tab

4. **Process videos** in the "Process Video" tab (upload or provide file path)

### Option 2: Command Line

1. **Build watchlist from photos:**
```bash
python main.py build-watchlist --photos-dir ./photos --output-db watchlist.db
```

2. **Process video:**
```bash
python main.py process-video --video ./demo.mp4 --watchlist watchlist.db --output results.json
```

3. **Process RTSP stream:**
```bash
python main.py process-rtsp --rtsp-url rtsp://camera-url --watchlist watchlist.db
```

## ☁️ Cloud Deployment

### Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Or manually
docker build -t ai-cctv-face-recognition .
docker run -p 5000:5000 ai-cctv-face-recognition
```

### Supported Platforms
- ✅ AWS (EC2, ECS, Elastic Beanstalk)
- ✅ Google Cloud (Cloud Run, Compute Engine)
- ✅ Azure (Container Instances, App Service)
- ✅ DigitalOcean (App Platform, Droplets)
- ✅ Railway
- ✅ Render
- ✅ Any Docker-compatible platform

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions.

## Architecture

- `face_detector.py`: SCRFD face detection
- `face_recognizer.py`: ArcFace embedding generation
- `database.py`: Database abstraction layer
- `matcher.py`: Real-time face matching
- `event_handler.py`: Event system (alerts, logs, webhooks)
- `input_handlers.py`: Image, video, RTSP input processing
- `dashboard.py`: Web UI dashboard

## Configuration

Create a `.env` file:
```
SIMILARITY_THRESHOLD=0.35
DATABASE_TYPE=sqlite
DATABASE_URL=watchlist.db
REDIS_HOST=localhost
REDIS_PORT=6379
WEBHOOK_URL=https://your-webhook-url.com
```

