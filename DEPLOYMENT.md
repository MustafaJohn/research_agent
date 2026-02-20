# Deployment Guide

This guide will help you deploy the Research Agent to production.

## Prerequisites

- GitHub account
- Google Gemini API key
- Railway/Render account (for backend)
- Vercel account (for frontend)

## Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub**:
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

## Step 2: Deploy Backend (Railway)

### Option A: Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect the Python project
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `PORT`: Will be set automatically by Railway
   - `CORS_ORIGINS`: Your frontend URL (e.g., `https://your-app.vercel.app`)
6. Railway will automatically deploy
7. Copy the deployment URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: research-agent-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r agent/requirements.txt`
   - **Start Command**: `cd agent && uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `CORS_ORIGINS`: Your frontend URL
6. Click "Create Web Service"
7. Copy the deployment URL

## Step 3: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your backend URL from Step 2
6. Click "Deploy"
7. Copy the deployment URL

## Step 4: Update CORS Settings

1. Go back to your backend deployment (Railway/Render)
2. Update the `CORS_ORIGINS` environment variable to include your Vercel URL:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```
3. Restart the backend service

## Step 5: Test Your Deployment

1. Visit your Vercel frontend URL
2. Enter a research topic
3. Verify that the API calls work correctly

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure all dependencies are in `requirements.txt`
- **Port issues**: Ensure `$PORT` environment variable is used (Railway/Render sets this)
- **API key errors**: Verify `GEMINI_API_KEY` is set correctly

### Frontend Issues

- **API connection errors**: Check `NEXT_PUBLIC_API_URL` matches your backend URL
- **CORS errors**: Update `CORS_ORIGINS` in backend to include frontend URL
- **Build errors**: Check Node.js version compatibility

### Common Fixes

1. **Clear build cache**: Delete `.next` folder and rebuild
2. **Check logs**: Both Railway and Vercel provide detailed logs
3. **Environment variables**: Double-check all env vars are set correctly

## Free Tier Limits

### Railway
- $5 free credit per month
- 500 hours of usage
- Suitable for small projects

### Render
- Free tier available
- Spins down after inactivity
- May have cold start delays

### Vercel
- Generous free tier
- Unlimited deployments
- Perfect for Next.js apps

## Monitoring

- **Railway**: Check logs in the dashboard
- **Render**: View logs in the service dashboard
- **Vercel**: Check deployment logs and analytics

## Next Steps

- Set up custom domains
- Add monitoring (Sentry, etc.)
- Implement rate limiting
- Add authentication if needed
