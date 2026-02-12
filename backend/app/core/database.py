"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import get_settings
from app.models.database import Base

logger = logging.getLogger(__name__)

settings = get_settings()

# Use SQLite for development/testing instead of PostgreSQL
# Change to PostgreSQL URL in .env for production
DATABASE_URL = settings.DATABASE_URL or "sqlite:///./attrition_db.db"

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DATABASE_ECHO,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
