# Simplified Setup Guide - Just One API Key!

Good news! You only need **ONE API key** to get started.

## ✅ What Works Out of the Box (No Setup)

1. **Binance Market Data** - Uses free public API
   - ✅ Real-time crypto prices (BTC, ETH, SOL, BNB, etc.)
   - ✅ No account needed
   - ✅ No API key needed
   - ✅ Completely free
   - ✅ 1200 requests/minute (way more than we need)

2. **PostgreSQL & Redis** - Via Docker
   - ✅ One command to start
   - ✅ No configuration needed

## 🔑 What You Need: Just Anthropic API Key

**Only one thing to set up**: Anthropic Claude API key

### Quick Steps (5 minutes)

1. **Go to Anthropic Console**
   ```
   https://console.anthropic.com/
   ```

2. **Sign up** with your email

3. **Add Credits**
   - Click "Billing"
   - Add credit card
   - Add $10-20 to start (enough for testing)

4. **Generate API Key**
   - Click "API Keys"
   - Click "Create Key"
   - Name it "Gauntlet"
   - **Copy the key** (starts with `sk-ant-`)

5. **Add to .env file**
   ```bash
   cd /Users/user/Documents/gauntlet/backend
   nano .env
   ```

   Change this line:
   ```env
   ANTHROPIC_API_KEY=sk-ant-xxx
   ```

   To your actual key:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

   Save and exit (Ctrl+X, then Y, then Enter)

## 🧪 Test Everything Works

### Test 1: Binance Public API (No Keys)

```bash
cd /Users/user/Documents/gauntlet/backend

# Install dependencies first (if not done)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Test Binance public API
python scripts/test_binance_public.py
```

Expected output:
```
✅ Binance: Using public API (no API keys needed)
✅ BTC/USDT    $  67,234.50
✅ ETH/USDT    $   3,456.78
✅ SOL/USDT    $     234.56
✅ BNB/USDT    $     567.89

🎉 Success! Binance public API is working perfectly!
```

### Test 2: Start Backend

```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Wait 10 seconds for databases to start
sleep 10

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/docs

You should see the API documentation!

### Test 3: Create Competition & Test LLM

Use the API docs or curl:

```bash
# Create a competition
curl -X POST "http://localhost:8000/api/v1/competitions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Test Competition",
    "start_time": "2025-02-01T00:00:00Z",
    "end_time": "2025-03-01T00:00:00Z",
    "invocation_interval_minutes": 15,
    "initial_capital": 100000.00,
    "max_leverage": 5.0,
    "allowed_asset_classes": ["crypto"]
  }'

# Save the competition_id from response

# Register Claude participant
curl -X POST "http://localhost:8000/api/v1/participants/competitions/{COMPETITION_ID}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Claude Trader",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-5-sonnet-20241022"
  }'

# Save the participant_id from response

# Start competition
curl -X POST "http://localhost:8000/api/v1/competitions/{COMPETITION_ID}/start" \
  -H "X-API-Key: dev-api-key"

# Trigger LLM trading decision (this will use your API key!)
curl -X POST "http://localhost:8000/api/v1/internal/trigger-invocation/{PARTICIPANT_ID}" \
  -H "X-API-Key: dev-api-key"

# Check results
curl "http://localhost:8000/api/v1/participants/{PARTICIPANT_ID}/portfolio" \
  -H "X-API-Key: dev-api-key"
```

## 💰 Costs

- **Binance**: FREE (public API)
- **PostgreSQL/Redis**: FREE (local Docker)
- **Anthropic Claude**: ~$0.05-$0.15 per trading decision

### Testing Budget
- 10 test invocations: ~$1-2
- Initial testing: $5-10 should be plenty

### Running a Competition
- 15-minute intervals (96 invocations/day): ~$5-15/day
- For testing, use 1-hour intervals: ~$1-4/day

## 🎯 Summary

**What you need:**
- ✅ Anthropic API key (5 minutes to get, $10-20 to start)

**What works automatically:**
- ✅ Binance market data (no setup, free)
- ✅ PostgreSQL (Docker, free)
- ✅ Redis (Docker, free)

**Total setup time:** 5-10 minutes
**Total cost to start:** $10-20 (Anthropic credits)

## 🚀 Quick Commands Reference

```bash
# Start databases
docker-compose up postgres redis -d

# Run migrations (first time only)
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Start frontend (separate terminal)
cd ../frontend
npm run dev

# Test Binance public API
python scripts/test_binance_public.py
```

## ❓ Common Questions

**Q: Do I need a Binance account?**
A: No! We use their free public API.

**Q: Do I need OpenAI API key?**
A: No, only if you want GPT agents too. Start with just Claude.

**Q: How much will this cost?**
A: $10-20 for Anthropic is enough to test thoroughly. Running costs depend on how often you invoke the LLMs.

**Q: Can I test without spending money?**
A: Not really - Claude needs an API key. But $10 gives you ~100-200 trading decisions for testing.

**Q: What if I hit rate limits?**
A: Binance public API allows 1200 req/min - way more than needed. Anthropic has high limits with paid accounts.

## 🆘 Troubleshooting

**"Binance API not working"**
- Run `python scripts/test_binance_public.py` to diagnose
- Check internet connection
- Binance might be temporarily down (rare)

**"Invalid Anthropic API key"**
- Make sure you copied the entire key including `sk-ant-`
- Check for extra spaces in .env file
- Verify in Anthropic console that key is active

**"Database connection error"**
- Run `docker-compose ps` - both should be "healthy"
- Try `docker-compose restart postgres redis`
- Check logs: `docker-compose logs postgres`

**"Module not found errors"**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

## 📚 More Resources

- **Full API Keys Guide**: `API_KEYS_GUIDE.md`
- **Backend Documentation**: `backend/README.md`
- **Quick Start Guide**: `QUICKSTART.md`

## ✅ Ready to Go!

Once you have your Anthropic API key:

1. Add it to `backend/.env`
2. Start Docker services
3. Run migrations
4. Start the backend
5. Create your first competition!

That's it! Have fun with your LLM trading competition! 🎉
