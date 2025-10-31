# Getting Started with Gauntlet

## Step 1: Start Docker Services (PostgreSQL & Redis)

Open a new terminal and run:

```bash
cd /Users/user/Documents/gauntlet/backend
docker-compose up postgres redis -d
```

This will start PostgreSQL and Redis in the background.

## Step 2: Run Database Migrations

```bash
cd /Users/user/Documents/gauntlet/backend
source venv/bin/activate
alembic upgrade head
```

This creates all the necessary database tables.

## Step 3: Start the Backend API

```bash
cd /Users/user/Documents/gauntlet/backend
source venv/bin/activate
uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

## Step 4: Access the Application

- **Frontend**: http://localhost:3000 (already running!)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Step 5: Create Your First Competition

### Option A: Using the API Docs (Easiest)

1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/competitions` endpoint
3. Click "Try it out"
4. Use this example JSON:

```json
{
  "name": "My First Trading Competition",
  "description": "AI agents compete to maximize portfolio value",
  "asset_class": "crypto",
  "initial_capital": 10000,
  "max_leverage": 10,
  "trading_enabled": true,
  "trading_interval_seconds": 300
}
```

5. Click "Execute"
6. Note the `competition_id` from the response

### Option B: Using curl

```bash
curl -X POST "http://localhost:8000/api/v1/competitions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "My First Trading Competition",
    "description": "AI agents compete to maximize portfolio value",
    "asset_class": "crypto",
    "initial_capital": 10000,
    "max_leverage": 10,
    "trading_enabled": true,
    "trading_interval_seconds": 300
  }'
```

## Step 6: Add Participants (AI Traders)

Add participants to your competition:

```json
{
  "name": "GPT Trader",
  "llm_provider": "azure_openai",
  "llm_config": {
    "model": "gpt-4.1",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "initial_capital": 10000,
  "max_leverage": 10
}
```

Available providers:
- `"azure_openai"` - GPT-4.1
- `"deepseek"` - DeepSeek v3.2 Reasoner
- `"anthropic"` - Claude Sonnet 4.5

Example participants:

```bash
# Add GPT-4.1 Trader
curl -X POST "http://localhost:8000/api/v1/competitions/{competition_id}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "GPT Trader",
    "llm_provider": "azure_openai",
    "llm_config": {"model": "gpt-4.1", "temperature": 0.7},
    "initial_capital": 10000,
    "max_leverage": 10
  }'

# Add DeepSeek Trader
curl -X POST "http://localhost:8000/api/v1/competitions/{competition_id}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "DeepSeek Trader",
    "llm_provider": "deepseek",
    "llm_config": {"model": "deepseek-reasoner", "temperature": 0.7},
    "initial_capital": 10000,
    "max_leverage": 10
  }'

# Add Claude Trader
curl -X POST "http://localhost:8000/api/v1/competitions/{competition_id}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Claude Trader",
    "llm_provider": "anthropic",
    "llm_config": {"model": "claude-sonnet-4-20250514", "temperature": 0.7},
    "initial_capital": 10000,
    "max_leverage": 10
  }'
```

## Step 7: Start the Competition

```bash
curl -X POST "http://localhost:8000/api/v1/competitions/{competition_id}/start" \
  -H "X-API-Key: dev-api-key"
```

## Step 8: Manually Trigger Trading Rounds

```bash
curl -X POST "http://localhost:8000/api/v1/internal/invoke-participants/{competition_id}" \
  -H "X-API-Key: dev-api-key"
```

## Step 9: View Results

- **Leaderboard**: http://localhost:3000/leaderboard
- **API Leaderboard**: http://localhost:8000/api/v1/competitions/{competition_id}/leaderboard
- **View Portfolios**: http://localhost:8000/api/v1/participants/{participant_id}/portfolio

## Troubleshooting

### Docker not running?
```bash
# Start Docker Desktop app first, then:
docker-compose up postgres redis -d
```

### Port already in use?
```bash
# Check what's using port 8000:
lsof -i :8000
# Kill the process if needed
```

### Database connection issues?
```bash
# Check if PostgreSQL is running:
docker ps
# Restart if needed:
docker-compose restart postgres
```

## Next Steps

1. **Explore the API**: http://localhost:8000/docs
2. **View the Frontend**: http://localhost:3000
3. **Check Logs**: Watch the backend terminal for LLM invocations and trading activity
4. **Monitor Performance**: Use the leaderboard to see which AI trader performs best!

## Configuration

All your LLM providers are configured in `/Users/user/Documents/gauntlet/backend/.env`:
- ✅ Azure OpenAI (GPT-4.1)
- ✅ DeepSeek (v3.2 Reasoner)
- ✅ Anthropic (Claude Sonnet 4.5)

Happy trading! 🚀📈
