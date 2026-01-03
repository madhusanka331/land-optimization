"""
Database connection and session management for FastAPI.
Handles SQLAlchemy database connections and session lifecycle.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from loguru import logger

from ..config.settings import settings
from ..models.db_models import Base


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Verify connections before using them
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def create_tables():
    """
    Create all database tables.
    Should be called on application startup.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        ```python
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database with default data if needed.
    """
    logger.info("Initializing database...")

    # Create tables
    create_tables()

    # Add default data if needed
    db = SessionLocal()
    try:
        # You can add default system configs here
        # For example, default GA parameters, presets, etc.
        pass
    finally:
        db.close()

    logger.info("Database initialization complete")
