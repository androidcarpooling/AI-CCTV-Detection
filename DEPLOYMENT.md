# Cloud Deployment Guide

This guide covers deploying the AI CCTV Face Recognition System to various cloud platforms.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker installed
- Docker Compose (optional, for easier management)

### Quick Start

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Or build and run manually:**
```bash
# Build the image
docker build -t ai-cctv-face-recognition .

# Run the container
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/watchlist.db:/app/watchlist.db \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/watchlist_photos:/app/watchlist_photos \
  --name face-recognition \
  ai-cctv-face-recognition
```

3. **Access the web interface:**
   - Open http://localhost:5000 in your browser

## ☁️ Cloud Platform Deployment

### AWS (EC2 / ECS / Elastic Beanstalk)

#### Option 1: EC2 Instance

1. **Launch EC2 instance:**
   - Choose Ubuntu 22.04 LTS
   - Minimum: t3.medium (2 vCPU, 4GB RAM)
   - Recommended: t3.large or larger for better performance

2. **SSH into instance and setup:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/androidcarpooling/AI-CCTV-Detection.git
cd AI-CCTV-Detection

# Build and run
docker-compose up -d
```

3. **Configure security group:**
   - Allow inbound traffic on port 5000 (HTTP)
   - Or use port 80/443 with nginx reverse proxy

#### Option 2: AWS ECS (Elastic Container Service)

1. **Push image to ECR:**
```bash
aws ecr create-repository --repository-name ai-cctv-face-recognition
docker tag ai-cctv-face-recognition:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ai-cctv-face-recognition:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ai-cctv-face-recognition:latest
```

2. **Create ECS task definition and service**
   - Use Fargate or EC2 launch type
   - Minimum: 2 vCPU, 4GB memory
   - Recommended: 4 vCPU, 8GB memory

### Google Cloud Platform (GCP)

#### Cloud Run (Serverless)

1. **Build and deploy:**
```bash
# Build image
gcloud builds submit --tag gcr.io/<project-id>/ai-cctv-face-recognition

# Deploy to Cloud Run
gcloud run deploy ai-cctv-face-recognition \
  --image gcr.io/<project-id>/ai-cctv-face-recognition \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --allow-unauthenticated
```

#### Compute Engine (VM)

Similar to AWS EC2 setup above.

### Azure

#### Container Instances

```bash
# Create resource group
az group create --name face-recognition-rg --location eastus

# Create container instance
az container create \
  --resource-group face-recognition-rg \
  --name ai-cctv-face-recognition \
  --image ai-cctv-face-recognition:latest \
  --cpu 2 \
  --memory 4 \
  --ports 5000 \
  --dns-name-label face-recognition-app
```

#### App Service

1. Create App Service with Docker container support
2. Configure with minimum 2 cores, 4GB RAM
3. Set environment variables

### DigitalOcean

#### App Platform

1. Connect GitHub repository
2. Select Dockerfile
3. Configure:
   - Build command: `docker build -t app .`
   - Run command: `python web_app.py`
   - Environment: `PORT=5000`
   - Resources: 2GB RAM, 1 vCPU minimum

#### Droplet (VM)

Similar to AWS EC2 setup.

### Railway

1. **Connect GitHub repository:**
   - Go to Railway dashboard
   - New Project → Deploy from GitHub
   - Select repository

2. **Configure:**
   - Build command: `docker build -t app .`
   - Start command: `python web_app.py`
   - Add environment variables if needed

3. **Deploy:**
   - Railway auto-deploys on push to main branch

### Render

1. **Create new Web Service:**
   - Connect GitHub repository
   - Build command: `docker build -t app .`
   - Start command: `python web_app.py`

2. **Configure:**
   - Instance type: Standard (2GB RAM minimum)
   - Environment: Docker

## 🔧 Environment Variables

Configure these in your cloud platform:

```bash
DATABASE_TYPE=sqlite  # or postgresql, redis
DATABASE_URL=watchlist.db  # or connection string
SIMILARITY_THRESHOLD=0.35
LOG_LEVEL=INFO
WEBHOOK_URL=  # Optional: for alerts
```

## 📊 Resource Requirements

### Minimum (for testing):
- CPU: 1-2 cores
- RAM: 2-4 GB
- Storage: 10 GB

### Recommended (production):
- CPU: 4+ cores
- RAM: 8+ GB
- Storage: 50+ GB (for videos and results)

### GPU (optional, for faster processing):
- NVIDIA GPU with CUDA support
- Update Dockerfile to use CUDA base image
- Change providers to `CUDAExecutionProvider` in code

## 🔒 Security Considerations

1. **Use HTTPS:**
   - Set up nginx reverse proxy with SSL
   - Or use cloud platform's load balancer with SSL

2. **Authentication:**
   - Add authentication middleware to web_app.py
   - Use Flask-Login or similar

3. **File Upload Limits:**
   - Already configured (500MB max)
   - Adjust in web_app.py if needed

4. **Database Security:**
   - Use PostgreSQL/Redis for production
   - Secure connection strings
   - Enable encryption at rest

## 📈 Scaling

### Horizontal Scaling:
- Use load balancer
- Multiple container instances
- Shared database (PostgreSQL/Redis)

### Vertical Scaling:
- Increase CPU/RAM allocation
- Use GPU instances for faster processing

## 🐛 Troubleshooting

### Container won't start:
- Check logs: `docker logs <container-name>`
- Verify port 5000 is available
- Check disk space

### Models not downloading:
- SSL certificate issues (already handled in code)
- Network connectivity
- Check ~/.insightface directory

### Out of memory:
- Increase container memory limit
- Process videos in smaller batches
- Reduce FPS parameter

## 📝 Monitoring

### Health Check Endpoint:
```bash
curl http://localhost:5000/api/stats
```

### Logs:
```bash
# Docker
docker logs -f <container-name>

# Docker Compose
docker-compose logs -f
```

## 🔄 Updates

To update the application:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

