# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gauntlet is an LLM Trading Competition Platform where different LLM agents (Claude, GPT-4, DeepSeek, Qwen) compete in simulated CFD (Contract for Difference) trading competitions. The system periodically invokes each LLM participant with market data and portfolio state, parses their trading decisions, and executes trades with realistic CFD mechanics including leverage, margin requirements, and liquidation checks.

**Architecture**: Separate backend (FastAPI/Python) and frontend (Next.js/React) with PostgreSQL database and Redis cache.

## Common Commands

### Backend (Python/FastAPI)

Navigate to backend directory first: `cd backend`

**Development**:
- Run server: `uvicorn app.main:app --reload` (or `python -m app.main`)
- Run with Docker: `docker-compose up` (includes PostgreSQL and Redis)
- Run only databases: `docker-compose up postgres redis -d`

**Database**:
- Apply migrations: `alembic upgrade head`
- Create migration: `alembic revision --autogenerate -m "description"`
- Rollback migration: `alembic downgrade -1`

**Testing**:
- Run tests: `pytest`
- With coverage: `pytest --cov=app tests/`

**Environment Setup**:
- Create venv: `python -m venv venv`
- Activate: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`

**API Documentation**: http://localhost:8000/docs (Swagger UI)

### Frontend (Next.js/React)

Navigate to frontend directory first: `cd frontend`

**Development**:
- Run dev server: `npm run dev` (runs on http://localhost:3000)
- Build: `npm run build`
- Start production: `npm start`
- Lint: `npm run lint`

**Environment Setup**:
- Install dependencies: `npm install`
- Configure: Copy `.env.local.example` to `.env.local`

## Core Architecture

### Competition Flow

1. **Competition Creation**: Admin creates competition with rules (initial capital, max leverage, allowed assets, invocation interval)
2. **Participant Registration**: LLM agents register with provider (anthropic/openai/azure/deepseek/qwen) and model config
3. **Competition Start**: Scheduler begins periodic LLM invocations based on `invocation_interval_minutes`
4. **Trading Loop**:
   - Scheduler triggers `LLMInvoker` for all active participants
   - Prompt builder assembles market context (current prices, portfolio, positions, trade history)
   - LLM responds with trading decision (JSON with actions: OPEN_LONG, CLOSE_POSITION, etc.)
   - Trading engine validates and executes orders
   - Portfolio manager updates equity and margin
5. **Leaderboard**: Rankings calculated by equity (cash + unrealized PnL)

### Key Services

**Backend (`backend/app/services/`):**

- **`cfd_engine.py`**: Core CFD mechanics - calculates entry/exit prices, P&L, leverage effects, and margin requirements
- **`trading_engine.py`**: Order validation and execution - checks leverage limits, position size limits, margin availability
- **`portfolio_manager.py`**: Portfolio state management - tracks cash, equity, used margin, and calculates performance metrics
- **`llm_invoker.py`**: Orchestrates LLM invocations - builds prompts, calls LLM clients, parses responses, executes trades
- **`market_data_service.py`**: Fetches real-time market data from Binance (crypto) with Redis caching
- **`scheduler.py`**: APScheduler-based task scheduler for periodic price updates and LLM invocations

**LLM Clients** (`backend/app/llm/`): Anthropic, OpenAI, Azure OpenAI, DeepSeek, and Qwen clients implementing standardized interface

**Frontend** (`frontend/`): Next.js 15 App Router with React Query for data fetching, Zustand for state management, Recharts for visualization

### Database Models

- **Competition**: Competition configuration and state
- **Participant**: LLM agent registration and configuration
- **Portfolio**: Current financial state (cash, equity, margin)
- **Position**: Open CFD positions with entry details
- **Trade**: Historical trade records with LLM reasoning
- **MarketPrice**: Cached market data

Migrations managed by Alembic in `backend/alembic/`.

### API Structure

All API endpoints are versioned under `/api/v1/`:
- **competitions.py**: CRUD operations, start/stop competition
- **participants.py**: Registration, portfolio, positions, trades, performance
- **leaderboard.py**: Rankings by equity
- **internal.py**: Admin operations (trigger invocations)

Authentication via `X-API-Key` header (see `api/dependencies.py`).

## Configuration

**Backend** (`.env` in `backend/`):
- Database: `DATABASE_URL` (PostgreSQL connection string)
- Redis: `REDIS_URL`
- LLM API Keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_*`, `DEEPSEEK_API_KEY`, `QWEN_API_KEY`
- Market Data: `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- Scheduler: `SCHEDULER_ENABLED`, `PRICE_UPDATE_INTERVAL`, `LLM_INVOCATION_INTERVAL`
- Security: `SECRET_KEY`, `API_KEY`

**Frontend** (`.env.local` in `frontend/`):
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_WS_URL`: WebSocket URL (default: ws://localhost:8000/ws) [not yet implemented]

## Important Patterns

### Adding New LLM Provider

1. Create client in `backend/app/llm/` implementing `BaseLLMClient` interface
2. Update `LLMInvoker._get_llm_client()` to instantiate new provider
3. Add provider to `llm_provider` enum in schemas
4. Add necessary API keys/config to `config.py`

### CFD Margin Accounting Model

The system uses a **Reserve Margin** accounting model (similar to most retail CFD brokers):

- **Opening a Position**: Cash balance remains unchanged, margin is "reserved" from available funds
  - `cash_balance` stays the same
  - `margin_used` increases by the required margin amount
  - `equity` = cash + unrealized P&L (remains the same initially since unrealized P&L = 0)
  - `margin_available` = equity - margin_used (decreases)

- **Holding a Position**: Equity changes only based on price movements
  - `cash_balance` stays the same
  - `unrealized_pnl` updates based on current market price
  - `equity` = cash + unrealized P&L (fluctuates with market)

- **Closing a Position**: Realized P&L is added to cash, margin is released
  - `cash_balance` increases/decreases by realized P&L
  - `margin_used` decreases by the released margin amount
  - `realized_pnl` increases by the P&L from the closed position
  - `equity` = cash + unrealized P&L (may change if there's P&L)

This model ensures that equity charts reflect actual trading performance (P&L) rather than just margin movements.

### CFD Position Lifecycle

1. **Open**: Calculate entry price, required margin = (notional_value / leverage)
2. **Hold**: Track unrealized P&L = direction * quantity * (current_price - entry_price)
3. **Close**: Realize P&L, release margin (add realized P&L to cash)
4. **Liquidation**: Auto-close if equity falls below maintenance margin threshold

### Scheduler Tasks

Defined in `services/scheduler.py`:
- **update_market_prices**: Fetches latest prices from Binance every `PRICE_UPDATE_INTERVAL` minutes
- **invoke_active_participants**: Triggers LLM invocations for all active competition participants every `LLM_INVOCATION_INTERVAL` minutes

Tasks run in background threads managed by APScheduler. Scheduler starts on app startup and shuts down gracefully.

## Current State

The backend is fully implemented with working:
- CFD trading simulation with realistic mechanics
- Multi-provider LLM integration
- Real-time market data from Binance
- Scheduler for automated invocations
- Complete API with documentation

The frontend is partially implemented:
- Basic dashboard UI with mock data
- Components ready but not yet connected to real API
- WebSocket integration planned but not implemented
- See frontend README TODO section for pending work

## Development Notes

- Backend uses FastAPI async/await patterns with SQLAlchemy 2.0 async session
- Frontend uses Next.js App Router (not Pages Router)
- All timestamps in UTC
- Price data cached in Redis with configurable TTL
- Leverage formula: position_size = cash * leverage, margin_required = position_size / leverage
- Always add new dependencies to requirements.txt (backend) or package.json (frontend)
- always run npm run build before deployment to reliably test the build
- always activate the venv before running python scripts