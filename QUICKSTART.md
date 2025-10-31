# Quick Start Guide

Get the LLM Trading Competition running in under 5 minutes!

## Prerequisites

Make sure you have these installed and running:

- **PostgreSQL** (database)
- **Redis** (cache)
- **Python 3.10+** (backend)
- **Node.js 18+** (frontend)

## One-Command Startup

From the project root directory:

```bash
./start.sh
```

That's it! The script will:
1. ✅ Check that PostgreSQL and Redis are running
2. ✅ Install dependencies if needed (backend venv, frontend node_modules)
3. ✅ Optionally reset and initialize the competition
4. ✅ Start the backend API server
5. ✅ Start the frontend dashboard
6. ✅ Give you the URLs to access

## Stop Everything

```bash
./stop.sh
```

This gracefully stops both backend and frontend services.

## What Gets Started

### Backend (FastAPI)
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Log**: `backend.log`

### Frontend (Next.js)
- **URL**: http://localhost:3000
- **Log**: `frontend.log`

## Competition Initialization

When you run `./start.sh`, it will ask:

```
Do you want to reset and initialize the competition? (y/N):
```

**Press `y`** if you want to:
- Delete all existing competition data
- Create a fresh competition
- Register 4 LLM participants (Claude, GPT-4o, GPT-4o mini, DeepSeek Reasoner)
- Give each participant $10,000 starting capital

**Press `n`** if you want to keep existing data.

## First Time Setup

### 1. Start Services

macOS:
```bash
brew services start postgresql
brew services start redis
```

Linux:
```bash
sudo systemctl start postgresql
sudo systemctl start redis
```

Docker:
```bash
docker-compose up postgres redis -d
```

### 2. Configure Environment

Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys:
- `ANTHROPIC_API_KEY` - Get from https://console.anthropic.com/
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` - Get from Azure portal (portal.azure.com)
  - Make sure you have deployments named "gpt-4o" and "gpt-4o-mini"
- `DEEPSEEK_API_KEY` - Get from https://platform.deepseek.com/

### 3. Apply Database Migrations

```bash
cd backend
./venv/bin/alembic upgrade head
cd ..
```

### 4. Start Everything

```bash
./start.sh
```

## Troubleshooting

### "PostgreSQL is not running"

**macOS:**
```bash
brew services start postgresql
# or
pg_ctl -D /usr/local/var/postgres start
```

**Linux:**
```bash
sudo systemctl start postgresql
```

**Docker:**
```bash
docker-compose up postgres -d
```

### "Redis is not running"

**macOS:**
```bash
brew services start redis
```

**Linux:**
```bash
sudo systemctl start redis
```

**Docker:**
```bash
docker-compose up redis -d
```

### "Backend failed to start"

Check the logs:
```bash
tail -f backend.log
```

Common issues:
- Database connection error: Check `DATABASE_URL` in `.env`
- Port 8000 already in use: Stop the conflicting process or use `./stop.sh`

### "Frontend failed to start"

Check the logs:
```bash
tail -f frontend.log
```

Common issues:
- Port 3000 already in use: Stop the conflicting process or use `./stop.sh`
- Missing dependencies: Run `cd frontend && npm install`

### Start Services Separately

If you need more control:

**Backend only:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

## After Starting

### Access the Dashboard
Open http://localhost:3000 in your browser

### Select a Participant
Use the dropdown to select a participant (e.g., "gpt4o")

### View Activity
- **Portfolio**: See equity, cash, positions
- **Recent Trades**: View trading history
- **Invocation Logs**: See LLM prompts and responses
- **Leaderboard**: Compare performance

### Monitor Logs

**Backend:**
```bash
tail -f backend.log
```

**Frontend:**
```bash
tail -f frontend.log
```

### Watch Live Trading

The scheduler automatically invokes LLMs every 60 minutes. Watch the logs to see:
- Market data updates
- LLM invocations
- Trading decisions
- Order execution

## Manual Competition Reset

If you want to reset without using `./start.sh`:

```bash
cd backend
./venv/bin/python scripts/init_competition.py
cd ..
```

## Configuration

### Competition Parameters

Edit `backend/scripts/init_competition.py`:

```python
COMPETITION_CONFIG = {
    "initial_capital": Decimal("10000.00"),  # Starting money
    "max_leverage": Decimal("10.0"),         # Max leverage
    "duration_days": 7,                      # Competition length
    "invocation_interval_minutes": 60,       # LLM call frequency
}
```

### Participants

Edit `backend/scripts/init_competition.py`:

```python
PARTICIPANTS_CONFIG = [
    {
        "name": "claude-sonnet",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20241022",
    },
    # Add more participants...
]
```

## For Development

### Run Tests

```bash
cd backend
./venv/bin/pytest
```

### Apply New Migrations

```bash
cd backend
./venv/bin/alembic upgrade head
```

### Create Migration

```bash
cd backend
./venv/bin/alembic revision --autogenerate -m "description"
```

## Next Steps

- 📊 View the dashboard at http://localhost:3000
- 📖 Read API docs at http://localhost:8000/docs
- 🔍 Check `backend/scripts/README.md` for more details
- 🤖 Watch LLMs compete in real-time!

---

**Need help?** Check the main README or backend/scripts/README.md for more details.
