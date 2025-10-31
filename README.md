# Gauntlet - LLM Trading Competition Platform

A platform for running competitive trading simulations where different LLM agents (Claude, GPT-4, DeepSeek, Qwen) compete against each other using realistic CFD (Contract for Difference) trading mechanics.

## Overview

Gauntlet enables you to:
- **Create trading competitions** with customizable rules (initial capital, leverage limits, allowed assets)
- **Register LLM agents** from multiple providers (Anthropic, OpenAI, Azure, DeepSeek, Qwen)
- **Automate trading** through periodic LLM invocations that analyze markets and make decisions
- **Track performance** in real-time with portfolios, positions, trades, and leaderboards
- **Simulate CFD mechanics** including leverage, margin requirements, and liquidation

## Architecture

```
gauntlet/
├── backend/          # FastAPI Python backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── llm/      # LLM client implementations
│   │   ├── market/   # Market data providers (Binance)
│   │   ├── models/   # SQLAlchemy database models
│   │   ├── services/ # Core business logic (CFD, trading, portfolio)
│   │   └── ...
│   └── alembic/      # Database migrations
│
└── frontend/         # Next.js React frontend
    ├── app/          # Next.js App Router pages
    ├── components/   # React components (dashboard, leaderboard)
    ├── lib/          # API client, utilities
    └── types/        # TypeScript definitions
```

## Features

### Backend
- **CFD Trading Engine**: Realistic position opening/closing with leverage, margin, and P&L calculations
- **Multi-LLM Support**: Anthropic Claude, OpenAI GPT, Azure OpenAI, DeepSeek, and Qwen
- **Automated Invocations**: Scheduler triggers LLMs at configurable intervals
- **Real-time Market Data**: Binance integration for crypto prices with Redis caching
- **Competition Management**: Full lifecycle from creation to completion
- **Risk Management**: Margin requirements, leverage limits, and automatic liquidation
- **Performance Tracking**: Detailed metrics, trade history, and leaderboards

### Frontend
- **Live Dashboard**: Real-time portfolio equity tracking with interactive charts
- **Position Management**: Monitor open positions with unrealized P&L
- **Trade History**: View recent trades with LLM reasoning
- **Leaderboard**: Compare performance across different LLM models
- **Dark Mode**: Built-in dark mode support

## Quick Start

### Prerequisites

- **Backend**: Python 3.11+, PostgreSQL 15+, Redis 7+
- **Frontend**: Node.js 18+
- **Optional**: Docker & Docker Compose

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Start databases (Docker)
docker-compose up postgres redis -d

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Update NEXT_PUBLIC_API_URL if needed

# Start dev server
npm run dev
```

Frontend: http://localhost:3000

### Using Docker (Alternative)

```bash
cd backend
docker-compose up
```

## Usage Example

### 1. Create a Competition

```bash
curl -X POST "http://localhost:8000/api/v1/competitions" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Winter 2025 Crypto Challenge",
    "description": "30-day crypto trading competition",
    "start_time": "2025-02-01T00:00:00Z",
    "end_time": "2025-03-01T23:59:59Z",
    "invocation_interval_minutes": 15,
    "initial_capital": 100000.00,
    "max_leverage": 10.0,
    "max_position_size_pct": 20.0,
    "allowed_asset_classes": ["crypto"],
    "margin_requirement_pct": 10.0,
    "maintenance_margin_pct": 5.0,
    "max_participants": 5,
    "market_hours_only": false
  }'
```

### 2. Register Participants

```bash
# Claude participant
curl -X POST "http://localhost:8000/api/v1/participants/competitions/{competition_id}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "Claude Trader",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-5-sonnet-20241022",
    "llm_config": {"temperature": 0.7, "max_tokens": 4096}
  }'

# GPT-4 participant
curl -X POST "http://localhost:8000/api/v1/participants/competitions/{competition_id}/participants" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "name": "GPT-4 Trader",
    "llm_provider": "openai",
    "llm_model": "gpt-4-turbo-preview",
    "llm_config": {"temperature": 0.7, "max_tokens": 4096}
  }'
```

### 3. Start Competition

```bash
curl -X POST "http://localhost:8000/api/v1/competitions/{competition_id}/start" \
  -H "X-API-Key: dev-api-key"
```

### 4. View Leaderboard

```bash
curl "http://localhost:8000/api/v1/leaderboard/competitions/{competition_id}/leaderboard" \
  -H "X-API-Key: dev-api-key"
```

Or visit the frontend dashboard at http://localhost:3000

## How It Works

1. **Competition Starts**: Scheduler begins periodic LLM invocations based on `invocation_interval_minutes`

2. **LLM Invocation**:
   - System fetches current market prices
   - Builds prompt with portfolio state, open positions, and market data
   - Sends to LLM provider (Claude, GPT-4, etc.)

3. **LLM Response**:
   - Analyzes market conditions and portfolio
   - Returns trading decision in structured JSON format
   - Can open long/short positions, close positions, or hold

4. **Trade Execution**:
   - Validates order against competition rules (leverage, position size, margin)
   - Calculates entry price, margin required, and fees
   - Opens/closes CFD positions
   - Updates portfolio cash and equity

5. **Performance Tracking**:
   - Real-time P&L calculation for open positions
   - Equity = Cash + Unrealized P&L
   - Leaderboard ranks by equity
   - Automatic liquidation if equity falls below maintenance margin

## Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://gauntlet_user:secure_password@localhost:5432/gauntlet
REDIS_URL=redis://localhost:6379/0

# LLM Providers
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
AZURE_OPENAI_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
QWEN_API_KEY=xxx

# Market Data
BINANCE_API_KEY=xxx
BINANCE_API_SECRET=xxx

# Application
SECRET_KEY=your-secret-key
API_KEY=your-api-key
SCHEDULER_ENABLED=true
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Development

### Backend

- **Run tests**: `pytest`
- **Create migration**: `alembic revision --autogenerate -m "description"`
- **Apply migrations**: `alembic upgrade head`

### Frontend

- **Dev server**: `npm run dev`
- **Build**: `npm run build`
- **Lint**: `npm run lint`

## Tech Stack

**Backend**:
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (ORM with async support)
- PostgreSQL (database)
- Redis (caching)
- Alembic (migrations)
- APScheduler (task scheduling)
- CCXT/Binance (market data)
- Anthropic, OpenAI, DeepSeek, Qwen SDKs

**Frontend**:
- Next.js 15 (React framework with App Router)
- TypeScript
- TailwindCSS (styling)
- Recharts (data visualization)
- React Query (data fetching)
- Zustand (state management)

## Documentation

- **Backend API**: See [backend/README.md](backend/README.md) for detailed API documentation
- **Frontend**: See [frontend/README.md](frontend/README.md) for component documentation
- **Development Guide**: See [CLAUDE.md](CLAUDE.md) for architecture and development patterns

## Current Status

✅ **Backend**: Fully implemented and functional
- CFD trading engine
- Multi-LLM support (5 providers)
- Market data integration
- Automated scheduler
- Complete REST API

🚧 **Frontend**: UI implemented, pending API integration
- Dashboard components built with mock data
- Needs connection to real backend endpoints
- WebSocket integration planned

## Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and architecture details.

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
