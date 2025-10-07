from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import HTTPException
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

# Create database engine with connection pooling and error handling
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL debugging
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        yield db
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        db.rollback()
        raise HTTPException(status_code=503, detail="Database connection failed")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()

async def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered
    from app.models import user, quest, participant, input, pool, reward, leaderboard, bonus, message, wallet, admin, daily_ai_message, credits, global_leaderboard, ads, notification, spin_wheel
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
