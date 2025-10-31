"""API dependencies"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.config import settings


def verify_api_key(x_api_key: str = Header(...)) -> str:
    """Verify API key from header"""
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def get_db_session() -> Session:
    """Get database session"""
    return next(get_db())
