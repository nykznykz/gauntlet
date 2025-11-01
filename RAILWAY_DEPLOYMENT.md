# Railway Deployment Guide

This guide explains how to deploy Gauntlet on Railway with separate backend and frontend services.

## Architecture Overview

- **Backend Service**: FastAPI application with PostgreSQL and Redis
- **Frontend Service**: Next.js application
- **Database**: PostgreSQL (Railway Plugin)
- **Cache**: Redis (Railway Plugin)

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. Railway CLI (optional but recommended): `npm i -g @railway/cli`
3. Git repository connected to Railway

## Deployment Steps

### 1. Create Railway Project

```bash
# Option A: Using Railway CLI
railway login
railway init

# Option B: Using Railway Dashboard
# Go to https://railway.app/new
# Click "New Project" > "Deploy from GitHub repo"
# Select your Gauntlet repository
```

### 2. Add Database Services

#### PostgreSQL

1. In Railway dashboard, click "New" > "Database" > "Add PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` environment variable
3. Note: The database URL format will be: `postgresql://user:password@host:port/database`

#### Redis

1. Click "New" > "Database" > "Add Redis"
2. Railway will automatically create a `REDIS_URL` environment variable
3. Note: The Redis URL format will be: `redis://host:port`

### 3. Deploy Backend Service

#### Create Backend Service

1. Click "New" > "GitHub Repo" (if not already added)
2. Or click "New" > "Empty Service" and connect to your repo
3. Configure the service:
   - **Name**: `gauntlet-backend`
   - **Root Directory**: `backend`
   - **Build Command**: Auto-detected from `railway.json`
   - **Start Command**: Auto-detected from `railway.json`

#### Configure Backend Environment Variables

Add these environment variables to the backend service:

**Database** (auto-populated if you added PostgreSQL plugin):
```
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
```

**LLM API Keys** (required - add your actual keys):
```
ANTHROPIC_API_KEY=sk-ant-xxx
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

**Market Data** (optional):
```
BINANCE_API_KEY=
BINANCE_API_SECRET=
```

**Application Settings**:
```
SECRET_KEY=<generate-a-secure-random-key>
API_KEY=<generate-a-secure-api-key>
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Scheduler**:
```
SCHEDULER_ENABLED=True
TIMEZONE=UTC
PRICE_CACHE_TTL=60
LEADERBOARD_CACHE_TTL=300
```

**Server** (Railway automatically sets PORT):
```
HOST=0.0.0.0
PORT=${PORT}
```

#### Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate API_KEY
python -c "import secrets; print('api-' + secrets.token_urlsafe(32))"
```

#### Deploy Backend

1. Click "Deploy" or push to your connected branch
2. Railway will automatically:
   - Install Python dependencies from `requirements.txt`
   - Run database migrations with Alembic (`alembic upgrade head`)
   - Start the FastAPI server with Uvicorn
3. Once deployed, note the backend URL (e.g., `https://gauntlet-backend-production.up.railway.app`)

### 4. Deploy Frontend Service

#### Create Frontend Service

1. Click "New" > "GitHub Repo" > Select your repo again
2. Configure the service:
   - **Name**: `gauntlet-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: Auto-detected from `railway.json`
   - **Start Command**: Auto-detected from `railway.json`

#### Configure Frontend Environment Variables

Add these environment variables to the frontend service:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.up.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend-url.up.railway.app/ws
```

Replace `your-backend-url.up.railway.app` with your actual backend Railway URL from step 3.

#### Deploy Frontend

1. Click "Deploy" or push to your connected branch
2. Railway will automatically:
   - Install Node.js dependencies (`npm install`)
   - Build the Next.js application (`npm run build`)
   - Start the production server (`npm start`)
3. Once deployed, your frontend will be accessible at the Railway-provided URL

### 5. Post-Deployment Configuration

#### Connect Services

Ensure backend and frontend services are in the same Railway project to share the database and Redis plugins.

#### Custom Domain (Optional)

1. Go to frontend service settings
2. Click "Settings" > "Domains"
3. Add your custom domain and configure DNS

#### Monitoring

- View logs: Click on each service to see real-time logs
- Metrics: Railway provides CPU, memory, and network metrics
- Health checks: Backend has a `/health` endpoint you can monitor

## Service Configuration Files

Railway deployment uses these configuration files:

### Backend Files

- `backend/railway.json`: Railway service configuration
- `backend/nixpacks.toml`: Nixpacks build configuration
- `backend/Procfile`: Process commands (migration + web server)

### Frontend Files

- `frontend/railway.json`: Railway service configuration
- `frontend/nixpacks.toml`: Nixpacks build configuration

## Database Migrations

Migrations run automatically on deployment via the `Procfile`:
```
release: alembic upgrade head
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

To run migrations manually:
```bash
railway run alembic upgrade head
```

## Troubleshooting

### Backend Won't Start

1. Check environment variables are set correctly
2. Verify `DATABASE_URL` format: `postgresql://user:password@host:port/database`
3. Check logs for missing dependencies or migration errors
4. Ensure PostgreSQL plugin is added and connected

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_URL` points to correct backend URL
2. Check backend CORS settings in `backend/app/main.py`
3. Ensure backend is deployed and healthy (check `/health` endpoint)

### Database Connection Issues

1. Verify PostgreSQL plugin is added
2. Check `DATABASE_URL` is populated in backend environment variables
3. Railway databases may take a few seconds to initialize on first deploy

### Migration Errors

1. Check Alembic migration files in `backend/alembic/versions/`
2. Run migrations manually: `railway run alembic upgrade head`
3. Check database schema matches migration expectations

### Redis Connection Issues

1. Verify Redis plugin is added
2. Check `REDIS_URL` is populated in backend environment variables
3. Redis is optional - the app will work without it (with reduced performance)

## Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `SECRET_KEY` | Application secret key | `random-secure-key` |
| `API_KEY` | API authentication key | `api-random-key` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-xxx` |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://backend.railway.app` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL | `wss://backend.railway.app/ws` |

## Scaling

Railway automatically scales based on your plan:

- **Free Tier**: 500 hours/month shared across services
- **Developer Plan**: $5/month per service
- **Team Plan**: Advanced scaling and collaboration features

To scale:
1. Go to service settings
2. Adjust "Replicas" (Pro plan required for multiple replicas)

## Cost Optimization

1. **Free Tier**: Suitable for development/testing
   - Backend: ~$0 (within free hours)
   - Frontend: ~$0 (within free hours)
   - PostgreSQL: Free plugin
   - Redis: Free plugin

2. **Production**: Estimated $10-20/month
   - Backend: $5/month (Developer plan)
   - Frontend: $5/month (Developer plan)
   - Database: Free plugin
   - Redis: Free plugin

## Continuous Deployment

Railway automatically deploys when you push to your connected branch:

1. Push to `main` branch (or your configured branch)
2. Railway detects changes and triggers build
3. Runs health checks
4. Deploys to production with zero downtime

## Rollback

To rollback to a previous deployment:

1. Go to service deployments
2. Find the previous successful deployment
3. Click "Redeploy"

## Manual Deployment

Using Railway CLI:

```bash
# Deploy specific service
railway up --service gauntlet-backend

# Run commands in Railway environment
railway run python backend/scripts/init_competition.py

# View logs
railway logs --service gauntlet-backend
```

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Gauntlet Issues: https://github.com/your-repo/issues
