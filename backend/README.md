# Gauntlet Backend - LLM Trading Competition Platform

Backend API for running LLM trading competitions with simulated CFD trading.

## Features

- **CFD Trading Simulation**: Realistic CFD mechanics with leverage, margin, and P&L calculations
- **Multiple LLM Support**: Anthropic Claude, OpenAI GPT, and custom agents
- **Competition Management**: Create and manage trading competitions with configurable rules
- **Real-time Market Data**: Binance integration for crypto prices
- **Portfolio Tracking**: Real-time portfolio, position, and trade tracking
- **Leaderboard**: Competitive rankings based on equity and performance
- **Risk Management**: Margin requirements, leverage limits, and liquidation checks

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

1. **Clone and navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Start PostgreSQL and Redis** (using Docker):
```bash
docker-compose up postgres redis -d
```

6. **Run database migrations**:
```bash
alembic upgrade head
```

7. **Start the API server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Using Docker Compose

Alternatively, run everything with Docker Compose:

```bash
docker-compose up
```

## API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Key API Endpoints

### Competitions
- `POST /api/v1/competitions` - Create competition
- `GET /api/v1/competitions` - List competitions
- `GET /api/v1/competitions/{id}` - Get competition details
- `POST /api/v1/competitions/{id}/start` - Start competition
- `POST /api/v1/competitions/{id}/stop` - Stop competition

### Participants
- `POST /api/v1/participants/competitions/{competition_id}/participants` - Register participant
- `GET /api/v1/participants/{id}` - Get participant details
- `GET /api/v1/participants/{id}/portfolio` - Get portfolio
- `GET /api/v1/participants/{id}/positions` - Get open positions
- `GET /api/v1/participants/{id}/trades` - Get trade history
- `GET /api/v1/participants/{id}/performance` - Get performance metrics

### Leaderboard
- `GET /api/v1/leaderboard/competitions/{competition_id}/leaderboard` - Get leaderboard

### Internal (Admin)
- `POST /api/v1/internal/invoke-participants` - Trigger LLM invocations for all participants
- `POST /api/v1/internal/trigger-invocation/{participant_id}` - Trigger single invocation

## Example Usage

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

### 2. Register a Participant

```bash
curl -X POST "http://localhost:8000/api/v1/participants/competitions/{competition_id}/participants" \
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
```

### 3. Trigger LLM Invocation

```bash
curl -X POST "http://localhost:8000/api/v1/internal/trigger-invocation/{participant_id}" \
  -H "X-API-Key: dev-api-key"
```

### 4. Get Leaderboard

```bash
curl "http://localhost:8000/api/v1/leaderboard/competitions/{competition_id}/leaderboard" \
  -H "X-API-Key: dev-api-key"
```

## Project Structure

```
backend/
├── app/
│   ├── api/               # API endpoints
│   │   └── v1/
│   │       ├── competitions.py
│   │       ├── participants.py
│   │       ├── leaderboard.py
│   │       └── internal.py
│   ├── llm/               # LLM clients
│   │   ├── anthropic_client.py
│   │   ├── openai_client.py
│   │   └── prompt_builder.py
│   ├── market/            # Market data providers
│   │   └── binance.py
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── cfd_engine.py
│   │   ├── portfolio_manager.py
│   │   ├── trading_engine.py
│   │   ├── market_data_service.py
│   │   └── llm_invoker.py
│   ├── utils/             # Utilities
│   │   ├── calculations.py
│   │   └── cache.py
│   ├── config.py          # Configuration
│   └── main.py            # FastAPI app
├── alembic/               # Database migrations
├── tests/                 # Tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Core Components

### CFD Engine
Handles position opening, closing, and P&L calculations with proper leverage and margin mechanics.

### Portfolio Manager
Manages portfolio state, equity calculations, margin allocation, and risk metrics.

### Trading Engine
Validates and executes orders, checking leverage limits, position sizes, and margin requirements.

### LLM Invoker
Orchestrates LLM invocations by building prompts with market data and portfolio state, parsing responses, and executing trading decisions.

### Market Data Service
Fetches real-time prices and market data from Binance (crypto) with Redis caching.

## Configuration

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://gauntlet_user:secure_password@localhost:5432/gauntlet
REDIS_URL=redis://localhost:6379/0

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
BINANCE_API_KEY=xxx
BINANCE_API_SECRET=xxx

# Application
SECRET_KEY=your-secret-key
API_KEY=your-api-key
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Development

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Adding a New LLM Provider

1. Create a new client in `app/llm/` implementing `BaseLLMClient`
2. Update `LLMInvoker._get_llm_client()` to support the new provider
3. Document the provider in the API schema

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Use strong passwords and API keys
3. Enable HTTPS/TLS
4. Set up proper logging and monitoring
5. Configure database backups
6. Use a production WSGI server (gunicorn)

## Troubleshooting

### Common Issues

**Database connection error**:
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify network connectivity

**Redis connection error**:
- Ensure Redis is running
- Check REDIS_URL in .env

**LLM API errors**:
- Verify API keys are correct
- Check API rate limits
- Ensure sufficient API credits

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
