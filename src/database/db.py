"""Database connection and initialization"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.models.base import Base

# Default database path
DEFAULT_DB_PATH = "./data/aid_service.db"

# Global engine and session factory
_engine = None
_SessionLocal = None


def init_db(db_path: str = None) -> None:
    """Initialize database connection and create tables"""
    global _engine, _SessionLocal
    
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Create engine with SQLite
    _engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create session factory
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=_engine)


def get_engine():
    """Get SQLAlchemy engine"""
    if _engine is None:
        init_db()
    return _engine


def get_session() -> Session:
    """Get a new database session"""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for FastAPI endpoints"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions"""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
