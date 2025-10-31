# Competition Management Scripts

This directory contains utility scripts for managing LLM trading competitions.

## init_competition.py

**Purpose**: Initialize or reset a competition by deleting all existing data and creating a fresh competition with participants.

### What It Does

1. **Deletes all existing data**:
   - Competitions
   - Participants
   - Portfolios
   - Positions
   - Orders
   - Trades
   - LLM Invocations
   - Portfolio History

2. **Creates a new competition** with configurable parameters:
   - Initial capital ($10,000 by default)
   - Max leverage (10x by default)
   - Allowed assets (BTC, ETH, BNB, SOL)
   - Competition duration (7 days by default)
   - Invocation interval (60 minutes by default)

3. **Registers LLM participants**:
   - Claude Sonnet
   - GPT-4o
   - GPT-4o Mini
   - DeepSeek Chat
   - Qwen Max

4. **Initializes portfolios** for each participant with the initial capital

### Prerequisites

1. **PostgreSQL database** must be running
2. **Database migrations** must be applied:
   ```bash
   cd backend
   alembic upgrade head
   ```
3. **Environment variables** must be configured in `backend/.env`:
   - `DATABASE_URL`
   - LLM API keys (optional, but needed for trading)

### Usage

#### From backend directory:
```bash
cd backend
python scripts/init_competition.py
```

#### Or with virtual environment:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/init_competition.py
```

### Configuration

Edit the script to customize competition parameters:

```python
# Competition settings
COMPETITION_CONFIG = {
    "name": "LLM Trading Competition - Battle Royale",
    "initial_capital": Decimal("10000.00"),
    "max_leverage": Decimal("10.0"),
    "duration_days": 7,
    "invocation_interval_minutes": 60,
    # ... more settings
}

# Participant settings
PARTICIPANTS_CONFIG = [
    {
        "name": "claude-sonnet",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20241022",
        # ... more settings
    },
    # ... more participants
]
```

### Expected Output

```
================================================================================
🚀 LLM TRADING COMPETITION - INITIALIZATION SCRIPT
================================================================================

🗑️  Deleting all existing data...
   Deleted:
   - 15 invocations
   - 8 trades
   - 12 orders
   - 3 positions
   - 5 portfolios
   - 5 participants
   - 1 competitions

📊 Creating new competition...
   ✅ Created competition: LLM Trading Competition - Battle Royale
   - ID: 550e8400-e29b-41d4-a716-446655440000
   - Duration: 7 days
   - Initial Capital: $10000.00
   - Max Leverage: 10x
   - Invocation Interval: 60 minutes

👥 Registering 5 participants...
   1. claude-sonnet (anthropic/claude-3-5-sonnet-20241022)
   2. gpt4o (openai/gpt-4o)
   3. gpt4o-mini (openai/gpt-4o-mini)
   4. deepseek-chat (deepseek/deepseek-chat)
   5. qwen-max (qwen/qwen-max)
   ✅ Registered 5 participants

================================================================================
🎉 COMPETITION INITIALIZED SUCCESSFULLY!
================================================================================
```

### After Running

1. **Start the backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**:
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:3000

4. **Monitor the competition**:
   - The scheduler will automatically invoke LLMs based on the configured interval
   - View invocation logs on the dashboard
   - Track performance on the leaderboard

### Safety Notes

⚠️ **WARNING**: This script will **DELETE ALL EXISTING DATA** in the database. Make sure you:
- Have backups if needed
- Are running this on the correct database
- Understand that this is destructive and irreversible

### Troubleshooting

**Error: "No module named 'app'"**
- Make sure you're running from the `backend/` directory
- Or add backend to PYTHONPATH: `PYTHONPATH=. python scripts/init_competition.py`

**Error: "Could not connect to database"**
- Check that PostgreSQL is running
- Verify `DATABASE_URL` in `.env`
- Ensure database exists

**Error: "relation does not exist"**
- Run migrations first: `alembic upgrade head`

### For Collaborators

This script makes it easy to reset the competition environment:

1. Pull latest code: `git pull`
2. Apply any new migrations: `alembic upgrade head`
3. Run initialization: `python scripts/init_competition.py`
4. Start servers and begin testing

You can modify `COMPETITION_CONFIG` and `PARTICIPANTS_CONFIG` at the top of the script to customize your competition setup.
