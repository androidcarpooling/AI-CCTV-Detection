# Quick Setup Guide for Render.com

## 🚀 Deploy to Render in 5 Minutes

### Step 1: Update Dockerfile (Optional)
Your current Dockerfile should work, but if you want Render-specific version:
```bash
cp Dockerfile.render Dockerfile
git add Dockerfile
git commit -m "Update Dockerfile for Render"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest)

### Step 3: Create Web Service
1. Click "New +" button (top right)
2. Select "Web Service"
3. Connect your GitHub account if not already connected
4. Select repository: `androidcarpooling/AI-CCTV-Detection`
5. Click "Connect"

### Step 4: Configure Service
Fill in the form:
- **Name:** `ai-cctv-detection` (or any name you like)
- **Environment:** Select `Docker`
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Dockerfile Path:** `Dockerfile`
- **Docker Context:** (leave empty)

### Step 5: Environment Variables
Click "Advanced" and add:
- **Key:** `PORT`
- **Value:** `10000`

(Actually, Render sets this automatically, but you can add it to be safe)

### Step 6: Plan Selection
- **Free Plan:** Free tier (spins down after 15 min inactivity)
- **Starter Plan:** $7/month (always on)

For testing, use Free plan. For production, use Starter.

### Step 7: Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for build and deployment
3. Your app will be live at: `https://ai-cctv-detection.onrender.com`

### Step 8: Test
Once deployed:
```bash
# Test health endpoint
curl https://ai-cctv-detection.onrender.com/health

# Open in browser
open https://ai-cctv-detection.onrender.com
```

## ✅ That's It!

Your app is now live and accessible to everyone!

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Make sure all dependencies are in `requirements.txt`
- Verify Dockerfile is correct

### App Not Responding
- Check deploy logs
- Verify PORT environment variable
- Make sure health endpoint works: `/health`

### Free Tier Spins Down
- Free tier apps sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Upgrade to Starter plan ($7/month) for always-on

## 📝 Notes

- Render automatically deploys on every push to `main` branch
- You can set up custom domain in Render dashboard
- Free tier has resource limits (512MB RAM, 0.1 CPU)
- For video processing, Starter plan recommended

