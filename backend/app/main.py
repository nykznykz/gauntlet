"""FastAPI application entry point"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import competitions, participants, leaderboard, internal
from app.services.scheduler import scheduler_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up Gauntlet API...")
    scheduler_service.start()
    yield
    # Shutdown
    logger.info("Shutting down Gauntlet API...")
    scheduler_service.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Gauntlet - LLM Trading Competition Platform",
    description="API for LLM trading competitions with CFD simulation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(competitions.router, prefix="/api/v1")
app.include_router(participants.router, prefix="/api/v1")
app.include_router(leaderboard.router, prefix="/api/v1")
app.include_router(internal.router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Gauntlet API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
