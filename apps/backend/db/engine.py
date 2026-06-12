"""
ASTRA-X Database Engine Configuration.
Supports SQLite (local dev) and PostgreSQL (production/Render).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./astra_x.db")

# Render provides postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
pool_kwargs = {
    "pool_pre_ping": True,
    "echo": False,
}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql"):
    # Render free tier postgres connection limits optimization
    pool_kwargs["pool_size"] = 5
    pool_kwargs["max_overflow"] = 10

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **pool_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
