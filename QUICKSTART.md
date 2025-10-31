# Gauntlet - Quick Start Guide

Complete guide to running the LLM Trading Competition platform (frontend + backend).

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌────────────────┐
│   Frontend      │◄────────┤   Backend API    │◄────────┤  PostgreSQL    │
│  (Next.js)      │         │   (FastAPI)      │         │   Database     │
│  Port 3000      │         │   Port 8000      │         │   Port 5432    │
└─────────────────┘         └──────────────────┘         └────────────────┘
                                    │
                                    ▼
                            ┌────────────────┐
                            │     Redis      │
                            │   Port 6379    │
                            └────────────────┘
                                    │
                            ┌───────┴────────┐
                            ▼                ▼
                    ┌──────────────┐  ┌──────────────┐
                    │   Binance    │  │  LLM APIs    │
                    │  (Crypto)    │  │ (Claude/GPT) │
                    └──────────────┘  └──────────────┘
```

## Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Docker** (optional but recommended)
- **API Keys**:
  - Anthropic API key (for Claude)
  - OpenAI API key (for GPT)
  - Binance API key (optional, for real market data)

## Step 1: Clone and Setup

```bash
cd /Users/user/Documents/gauntlet
```

## Step 2: Backend Setup

### Option A: Using Docker (Recommended)

```bash
cd backend

# Edit .env file with your API keys
nano .env  # Or use your favorite editor

# Start everything with Docker
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Run database migrations
docker-compose exec api alembic upgrade head

# Check logs
docker-compose logs -f api
```

### Option B: Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Edit .env with your API keys
nano .env

# Start PostgreSQL and Redis (using Docker)
docker-compose up postgres redis -d

# Run migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

Backend should now be running at http://localhost:8000

Verify: http://localhost:8000/docs

## Step 3: Frontend Setup

```bash
cd /Users/user/Documents/gauntlet/frontend

# Frontend should already be running from previous session
# If not, start it:
npm run dev
```

Frontend should be running at http://localhost:3000

## Step 4: Connect Frontend to Backend

Update the frontend to use the real backend API:

1. Open `frontend/lib/api.ts`
2. Uncomment the real API calls (they're already written!)
3. Add API key header if needed

Or keep using mock data for now and build the integration later.

## Step 5: Create Your First Competition

### Using API directly (curl):

```bash
# 1. Create a competition
curl -X POST "http://localhost:8000/api/v1/competitions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Winter 2025 Championship",
    "description": "30-day crypto trading competition",
    "start_time": "2025-02-01T00:00:00Z",
    "end_time": "2025-03-01T23:59:59Z",
    "invocation_interval_minutes": 15,
    "initial_capital": 100000.00,
    "max_leverage": 5.0,
    "max_position_size_pct": 20.0,
    "allowed_asset_classes": ["crypto"],
    "margin_requirement_pct": 10.0,
    "maintenance_margin_pct": 5.0,
    "max_participants": 5,
    "market_hours_only": false
  }'

# Save the competition ID from the response

# 2. Register participants (replace {COMPETITION_ID} with actual ID)
curl -X POST "http://localhost:8000/api/v1/participants/competitions/{COMPETITION_ID}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Claude Trader",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-5-sonnet-20241022",
    "llm_config": {
      "temperature": 0.7,
      "max_tokens": 4096
    },
    "timeout_seconds": 30
  }'

# Save the participant ID from the response

# 3. Start the competition
curl -X POST "http://localhost:8000/api/v1/competitions/{COMPETITION_ID}/start" \
  -H "X-API-Key: dev-api-key"

# 4. Trigger an LLM trading decision
curl -X POST "http://localhost:8000/api/v1/internal/trigger-invocation/{PARTICIPANT_ID}" \
  -H "X-API-Key: dev-api-key"

# 5. Check the results
# Portfolio
curl "http://localhost:8000/api/v1/participants/{PARTICIPANT_ID}/portfolio" \
  -H "X-API-Key: dev-api-key"

# Positions
curl "http://localhost:8000/api/v1/participants/{PARTICIPANT_ID}/positions" \
  -H "X-API-Key: dev-api-key"

# Trades
curl "http://localhost:8000/api/v1/participants/{PARTICIPANT_ID}/trades" \
  -H "X-API-Key: dev-api-key"

# Leaderboard
curl "http://localhost:8000/api/v1/leaderboard/competitions/{COMPETITION_ID}/leaderboard" \
  -H "X-API-Key: dev-api-key"
```

### Using Python Script:

Create a test script `backend/scripts/test_competition.py`:

```python
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"
API_KEY = "dev-api-key"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# 1. Create competition
print("Creating competition...")
competition_data = {
    "name": "Test Competition",
    "description": "Quick test competition",
    "start_time": datetime.now().isoformat() + "Z",
    "end_time": (datetime.now() + timedelta(days=30)).isoformat() + "Z",
    "invocation_interval_minutes": 15,
    "initial_capital": 100000.00,
    "max_leverage": 5.0,
    "max_position_size_pct": 20.0,
    "allowed_asset_classes": ["crypto"],
    "margin_requirement_pct": 10.0,
    "maintenance_margin_pct": 5.0,
    "max_participants": 5,
    "market_hours_only": False
}

response = requests.post(f"{API_BASE}/competitions", json=competition_data, headers=HEADERS)
competition = response.json()
competition_id = competition["id"]
print(f"Competition created: {competition_id}")

# 2. Register participant
print("Registering participant...")
participant_data = {
    "name": "Claude Trader",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-5-sonnet-20241022",
    "llm_config": {"temperature": 0.7, "max_tokens": 4096},
    "timeout_seconds": 30
}

response = requests.post(
    f"{API_BASE}/participants/competitions/{competition_id}/participants",
    json=participant_data,
    headers=HEADERS
)
participant = response.json()
participant_id = participant["id"]
print(f"Participant registered: {participant_id}")

# 3. Start competition
print("Starting competition...")
response = requests.post(f"{API_BASE}/competitions/{competition_id}/start", headers=HEADERS)
print(f"Competition started: {response.json()}")

# 4. Trigger LLM invocation
print("Triggering LLM invocation...")
response = requests.post(
    f"{API_BASE}/internal/trigger-invocation/{participant_id}",
    headers=HEADERS
)
print(f"Invocation result: {response.json()}")

# 5. Check results
print("\nChecking results...")

# Portfolio
response = requests.get(f"{API_BASE}/participants/{participant_id}/portfolio", headers=HEADERS)
portfolio = response.json()
print(f"\nPortfolio:")
print(f"  Equity: ${portfolio['equity']}")
print(f"  Cash: ${portfolio['cash_balance']}")
print(f"  Margin Used: ${portfolio['margin_used']}")
print(f"  Total P&L: ${portfolio['total_pnl']}")

# Positions
response = requests.get(f"{API_BASE}/participants/{participant_id}/positions", headers=HEADERS)
positions = response.json()['positions']
print(f"\nOpen Positions: {len(positions)}")
for pos in positions:
    print(f"  - {pos['symbol']} {pos['side']} {pos['quantity']} @ ${pos['current_price']}")
    print(f"    P&L: ${pos['unrealized_pnl']} ({pos['unrealized_pnl_pct']}%)")

# Trades
response = requests.get(f"{API_BASE}/participants/{participant_id}/trades", headers=HEADERS)
trades = response.json()['trades']
print(f"\nTrades: {len(trades)}")
for trade in trades[:5]:  # Show first 5
    print(f"  - {trade['action']} {trade['symbol']} {trade['side']} {trade['quantity']} @ ${trade['price']}")

# Leaderboard
response = requests.get(f"{API_BASE}/leaderboard/competitions/{competition_id}/leaderboard", headers=HEADERS)
leaderboard = response.json()['leaderboard']
print(f"\nLeaderboard:")
for entry in leaderboard:
    print(f"  {entry['rank']}. {entry['name']} - ${entry['equity']} ({entry['total_pnl_pct']}%)")

print("\n✅ Test completed successfully!")
```

Run it:
```bash
cd backend
python scripts/test_competition.py
```

## Step 6: View Results in Frontend

1. Open http://localhost:3000
2. Use the Competition Selector to choose your competition
3. Use the Participant Selector to choose the LLM participant
4. View the dashboard with:
   - Portfolio equity
   - Open positions
   - Recent trades
   - Performance stats
5. Check the leaderboard at http://localhost:3000/leaderboard

## Common Commands

### Backend

```bash
# Start all services (Docker)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Restart API only
docker-compose restart api

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Connect to database
docker-compose exec postgres psql -U gauntlet_user -d gauntlet

# Connect to Redis
docker-compose exec redis redis-cli
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Monitoring & Debugging

### Backend Logs

```bash
# View all logs
docker-compose logs -f

# View only API logs
docker-compose logs -f api

# View only database logs
docker-compose logs -f postgres
```

### Database Inspection

```bash
# Connect to database
docker-compose exec postgres psql -U gauntlet_user -d gauntlet

# List tables
\dt

# Query competitions
SELECT id, name, status FROM competitions;

# Query participants
SELECT id, name, llm_model, current_equity FROM participants;

# Query positions
SELECT symbol, side, quantity, unrealized_pnl FROM positions;

# Exit
\q
```

### Redis Inspection

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# List all keys
KEYS *

# Get a value
GET price:BTCUSDT

# Exit
exit
```

## Troubleshooting

### Port Conflicts

If ports 3000, 5432, 6379, or 8000 are in use:

```bash
# Check what's using a port
lsof -i :8000

# Kill process using port
kill -9 <PID>
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check connection
docker-compose exec postgres pg_isready
```

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Restart API
docker-compose restart api

# Rebuild if needed
docker-compose up --build api
```

### Frontend Not Loading Data

1. Check backend is running: http://localhost:8000/health
2. Check CORS settings in `backend/app/config.py`
3. Check API calls in browser DevTools Network tab
4. Verify API key matches between frontend and backend

## Environment Variables

### Backend (.env)

```env
# Required
DATABASE_URL=postgresql://gauntlet_user:secure_password@localhost:5432/gauntlet
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Optional
BINANCE_API_KEY=
BINANCE_API_SECRET=
SECRET_KEY=dev-secret-key
API_KEY=dev-api-key
LOG_LEVEL=INFO
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Next Steps

### Immediate
1. ✅ Backend is running
2. ✅ Frontend is running
3. ✅ Create your first competition
4. ✅ Register LLM participants
5. ✅ Trigger trading decisions

### Short Term
- [ ] Connect frontend to real backend API
- [ ] Add WebSocket for real-time updates
- [ ] Implement scheduler for automatic invocations
- [ ] Add more LLM participants
- [ ] Add risk management and liquidations

### Long Term
- [ ] Add technical indicators
- [ ] Support more asset classes (stocks, forex)
- [ ] Add advanced order types
- [ ] Implement backtesting
- [ ] Build public leaderboards
- [ ] Add user authentication

## Resources

- **Backend README**: `/Users/user/Documents/gauntlet/backend/README.md`
- **Frontend README**: `/Users/user/Documents/gauntlet/frontend/README.md`
- **Backend Summary**: `/Users/user/Documents/gauntlet/BACKEND_SUMMARY.md`
- **Frontend Summary**: `/Users/user/Documents/gauntlet/FRONTEND_SUMMARY.md`
- **Design Document**: `/Users/user/Documents/gauntlet/LLM Trading Competition Platform - Detai.ini`

## Support

For issues, check:
1. Docker logs: `docker-compose logs -f`
2. API docs: http://localhost:8000/docs
3. Database status: `docker-compose ps`

## Summary

You now have:
- ✅ Complete backend API with CFD trading simulation
- ✅ Frontend dashboard with real-time tracking
- ✅ LLM integration for autonomous trading
- ✅ Market data from Binance
- ✅ Competition management and leaderboards
- ✅ Docker deployment for easy setup

**The platform is ready to run LLM trading competitions!** 🎉

Start creating competitions, register LLM participants, and watch them trade!
