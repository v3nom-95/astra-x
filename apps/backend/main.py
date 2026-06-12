"""
ASTRA-X — Autonomous Defence Readiness Intelligence Platform
Main FastAPI Application Entry Point.

Handles:
- App lifecycle (startup, shutdown)
- CORS configuration
- Router registration
- ML model initialization
- Database table creation
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

from db.engine import engine
from models import Base
from services.ml.model_manager import ModelManager
from services.authorization.terminal3_client import Terminal3Client

from api.upload import router as upload_router
from api.predict import router as predict_router
from api.agents import router as agents_router
from api.authorize import router as authorize_router
from api.dashboard import router as dashboard_router
from api.audit import router as audit_router
from api.assets import router as assets_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("astra-x")


def init_db():
    """Create all database tables."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ────────────────────────────────
    logger.info("=" * 60)
    logger.info("  ASTRA-X — Autonomous Defence Readiness Intelligence")
    logger.info("  Starting up...")
    logger.info("=" * 60)

    # Create database tables
    init_db()

    # Initialize ML models (train or load from cache)
    logger.info("Initializing ML models...")
    model_manager = ModelManager.get_instance()
    status = model_manager.initialize()
    logger.info(f"ML model status: {status}")

    # Initialize Terminal3 real-time API client
    logger.info("Initializing Terminal3 API client...")
    Terminal3Client.get_instance()
    logger.info("Terminal3 real-time API client initialized")

    logger.info("=" * 60)
    logger.info("  ASTRA-X is ready")
    logger.info("=" * 60)

    yield

    # ── Shutdown ───────────────────────────────
    logger.info("ASTRA-X shutting down...")


# ── App Configuration ──────────────────────────────

app = FastAPI(
    title="ASTRA-X",
    description="Autonomous Defence Readiness Intelligence Platform — "
                "Multi-agent ML-driven logistics readiness and asset governance.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - Restricted for production
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

# Add wildcard only for development if explicitly set, otherwise use strict origins
if os.getenv("ENVIRONMENT") != "production":
    if "*" not in cors_origins:
        cors_origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Register Routers ──────────────────────────────

app.include_router(upload_router)
app.include_router(predict_router)
app.include_router(agents_router)
app.include_router(authorize_router)
app.include_router(dashboard_router)
app.include_router(audit_router)
app.include_router(assets_router)


# ── Health Check ──────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Render."""
    model_manager = ModelManager.get_instance()
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "connected",
        "ml_models": model_manager.status,
        "version": "1.0.0",
    }


# ── Root ──────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "ASTRA-X",
        "description": "Autonomous Defence Readiness Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
