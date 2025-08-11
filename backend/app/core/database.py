"""
Database configuration for Crime Prevention System
PostgreSQL connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./crime_prevention.db"  # Временно SQLite для тестирования
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
    echo=False           # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependency that provides a database session
    Automatically closes the session when done
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection
def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Execute a simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False