from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# Use SQLite for local development if PostgreSQL URL is not available
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recipe_app.db")

# Create engine with appropriate settings for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        # Only treat database-specific errors as 503 errors
        if "database" in str(e).lower() or "connection" in str(e).lower():
            logger.error(f"Database connection failed: {e}")
            raise HTTPException(
                status_code=503, detail="Database connection unavailable."
            )
        else:
            # Re-raise other exceptions (like validation errors) as-is
            raise e
    finally:
        db.close()
