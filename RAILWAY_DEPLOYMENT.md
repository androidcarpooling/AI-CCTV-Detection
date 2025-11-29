# Railway Deployment Guide

## ✅ Auto-Deployment Setup

**Yes! Railway automatically builds and deploys when you push to your repository.**

### How It Works:
1. Connect your GitHub repo to Railway
2. Railway watches the `main` branch
3. Every push triggers a new build and deployment
4. Build logs are available in Railway dashboard

## 🚀 Quick Setup Steps

### 1. Connect Repository to Railway

1. Go to [Railway Dashboard](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `androidcarpooling/AI-CCTV-Detection`
5. Railway will automatically detect the Dockerfile

### 2. Configure Environment Variables (Optional)

In Railway dashboard, go to your service → Variables tab:

```
PORT=5000  # Railway sets this automatically, but you can override
DATABASE_TYPE=sqlite
DATABASE_URL=watchlist.db
SIMILARITY_THRESHOLD=0.35
LOG_LEVEL=INFO
```

### 3. Deploy

Railway will automatically:
- Build the Docker image
- Install dependencies
- Download InsightFace models
- Start the web application

### 4. Get Your URL

After deployment, Railway provides a public URL like:
- `https://your-app-name.up.railway.app`

## 📝 What Was Fixed

### Dockerfile Fixes:
- ✅ Changed `libgl1-mesa-glx` → `libgl1` (compatible with Debian Trixie)
- ✅ Changed `libxrender-dev` → `libxrender1`
- ✅ Added PORT environment variable support

### Railway Configuration:
- ✅ Created `railway.json` and `railway.toml` for Railway-specific settings
- ✅ Updated `web_app.py` to use PORT env var (Railway requirement)

## 🔄 Auto-Deploy Workflow

1. **Make changes locally**
2. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. **Railway automatically:**
   - Detects the push
   - Starts a new build
   - Deploys the new version
   - Updates your live URL

## 📊 Monitoring

- **Build Logs:** Available in Railway dashboard
- **Deployment Logs:** Real-time logs in Railway dashboard
- **Metrics:** CPU, Memory usage in Railway dashboard

## 💡 Tips

1. **First Build:** Takes longer (~5-10 min) due to model downloads
2. **Subsequent Builds:** Faster (~2-3 min) due to Docker layer caching
3. **Resource Limits:** Railway free tier has limits, upgrade if needed for production
4. **Database:** For production, consider using Railway's PostgreSQL addon instead of SQLite

## 🐛 Troubleshooting

### Build Fails:
- Check build logs in Railway dashboard
- Verify Dockerfile syntax
- Ensure all dependencies are in requirements.txt

### App Won't Start:
- Check deployment logs
- Verify PORT environment variable is set
- Check if models downloaded successfully

### Out of Memory:
- Railway free tier: 512MB RAM
- Upgrade plan for more resources
- Or optimize by processing fewer frames (higher FPS value)

## 🔗 Next Steps

1. Push your code (already done!)
2. Connect repo to Railway
3. Wait for first build to complete
4. Access your app via Railway URL
5. Start using the web interface!

