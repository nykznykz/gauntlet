FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations, initialization, and start server
CMD alembic upgrade head && python scripts/railway_init.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
