"""Application configuration management"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://gauntlet_user:secure_password@localhost:5432/gauntlet"
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # AWS Bedrock Configuration
    AWS_BEARER_TOKEN_BEDROCK: str = ""

    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4.1"

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Qwen Configuration
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    QWEN_MODEL: str = "qwen-max"  # qwen-max = Qwen 3 Max, qwen-max-latest, qwen-turbo, qwen-plus

    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""

    # Application
    SECRET_KEY: str = "change-me-in-production"
    API_KEY: str = "dev-api-key"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    # Scheduler
    SCHEDULER_ENABLED: bool = True
    TIMEZONE: str = "UTC"

    # Scheduler Intervals (in minutes)
    PRICE_UPDATE_INTERVAL: int = 1  # Update prices every 1 minute
    LLM_INVOCATION_INTERVAL: int = 5  # Invoke LLMs every 5 minutes

    # Redis Cache TTL
    PRICE_CACHE_TTL: int = 60
    LEADERBOARD_CACHE_TTL: int = 300

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_ORIGIN_REGEX: str = r"https://.*\.railway\.app"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
