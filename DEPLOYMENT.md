# Deployment Guide

This guide covers deploying **G.G. Trading** with:
- **Frontend**: Vercel (free tier)
- **Backend**: Railway (free tier with limitations) or Render

---

## Prerequisites

1. GitHub account with your code pushed to a repository
2. [Vercel account](https://vercel.com) (free)
3. [Railway account](https://railway.app) (free tier: $5 credit/month) OR [Render account](https://render.com) (free tier)

---

## Step 1: Push Your Code to GitHub

If you haven't already:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for deployment"

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/Stock-Database.git

# Push
git push -u origin main
```

---

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Account & Project

1. Go to [Railway](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `Stock-Database` repository

### 2.2 Configure Railway for Backend

Since your repo has both frontend and backend, configure Railway to only deploy the backend:

1. After connecting the repo, click on the service
2. Go to **Settings** tab
3. Under **Build**, set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.3 Add PostgreSQL Database

1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Wait for it to provision
3. Click on the PostgreSQL service → **"Variables"** tab
4. Copy the `DATABASE_URL` value

### 2.4 Set Environment Variables

1. Click on your backend service → **"Variables"** tab
2. Add these variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | *(paste the PostgreSQL URL from step 2.3)* |
| `SECRET_KEY` | *(generate: `openssl rand -hex 32`)* |
| `FRONTEND_URL` | `https://your-app.vercel.app` *(update after Vercel deploy)* |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `LOG_TO_FILE` | `false` |
| `LOG_TO_CONSOLE` | `true` |
| `ALPHAVANTAGE_API_KEY` | *(your API key from alphavantage.co)* |

### 2.5 Deploy & Get Backend URL

1. Railway will auto-deploy when you add variables
2. Go to **Settings** → **Networking** → **Generate Domain**
3. Copy your backend URL (e.g., `https://stock-database-production.up.railway.app`)

### 2.6 Run Database Migrations

In Railway, go to your backend service → **"Shell"** tab and run:

```bash
cd backend
alembic upgrade head
```

Or run it locally pointing to the production database:

```bash
DATABASE_URL="your-railway-postgres-url" alembic upgrade head
```

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account & Project

1. Go to [Vercel](https://vercel.com) and sign in with GitHub
2. Click **"Add New..."** → **"Project"**
3. Import your `Stock-Database` repository

### 3.2 Configure Vercel for Frontend

1. In the project configuration:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

2. Add Environment Variables:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-backend.railway.app` *(from step 2.5)* |

3. Click **"Deploy"**

### 3.3 Get Your Frontend URL

After deployment, Vercel will give you a URL like:
- `https://stock-database.vercel.app`

### 3.4 Update Backend CORS

Go back to Railway and update the `FRONTEND_URL` environment variable with your Vercel URL.

---

## Step 4: Verify Deployment

1. Visit your Vercel URL
2. Try to register a new account
3. Create a portfolio
4. Add a transaction

---

## Alternative: Deploy Backend to Render

If you prefer Render over Railway:

### Create Render Web Service

1. Go to [Render](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Add Render PostgreSQL

1. Click **"New +"** → **"PostgreSQL"**
2. Create a free instance
3. Copy the **Internal Database URL**

### Set Environment Variables

Same as Railway (step 2.4), but in Render's **Environment** tab.

---

## Troubleshooting

### "CORS Error" in browser console
- Make sure `FRONTEND_URL` in Railway matches your exact Vercel URL
- Include `https://` and no trailing slash

### "Database connection failed"
- Verify `DATABASE_URL` is correct
- Check if PostgreSQL service is running

### "Module not found" during build
- Make sure `requirements.txt` is in the `backend` directory
- Check Railway/Render build logs

### Stock prices not loading
- Make sure `ALPHAVANTAGE_API_KEY` is set
- Free tier has 25 requests/day limit

---

## Local Development After Deployment

Create a `.env` file in `backend/`:

```env
DATABASE_URL=sqlite:///./stock-tracker.db
SECRET_KEY=dev-secret-key
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

Create a `.env` file in `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

---

## Cost Summary

| Service | Free Tier |
|---------|-----------|
| **Vercel** | Unlimited for personal projects |
| **Railway** | $5/month credit (usually enough for small apps) |
| **Render** | 750 hours/month (spins down after 15 min inactivity) |

For a hobby project, you can run entirely free!

