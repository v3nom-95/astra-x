"""
ASTRA-X ORM Models.
All SQLAlchemy models for the platform.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase
import enum


class Base(DeclarativeBase):
    """Declarative base for all ASTRA-X models."""
    pass


# ── Enums ──────────────────────────────────────────

class AssetStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    STANDBY = "STANDBY"
    FROZEN = "FROZEN"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActionType(str, enum.Enum):
    APPROVE_RESTOCK = "approve_restock"
    DELAY_RESTOCK = "delay_restock"
    SCHEDULE_SERVICE = "schedule_service"
    CONTINUE_OPERATION = "continue_operation"
    FREEZE_OPERATION = "freeze_operation"
    MONITOR = "monitor"
    PAUSE_OPERATION = "pause_operation"
    APPROVE_DISPATCH = "approve_dispatch"


# ── Models ─────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="operator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)
    inventory = Column(Integer, default=0)
    usage_rate = Column(Float, default=0.0)
    service_days = Column(Integer, default=0)
    temperature = Column(Float, default=0.0)
    repairs = Column(Integer, default=0)
    location = Column(String(100), default="UNKNOWN")
    status = Column(String(20), default=AssetStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(50), nullable=False, index=True)
    prediction_type = Column(String(50), nullable=False)  # inventory, maintenance, risk
    input_data = Column(Text)  # JSON string of inputs
    result = Column(Text)  # JSON string of prediction result
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50), nullable=True, index=True)


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False)
    asset_id = Column(String(50), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    reason = Column(Text)
    input_predictions = Column(Text)  # JSON string
    status = Column(String(20), default="pending")  # pending, authorized, rejected, executed
    created_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50), nullable=True, index=True)


class AuthorizationLog(Base):
    __tablename__ = "authorization_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    asset_id = Column(String(50), nullable=False, index=True)
    authorized = Column(Boolean, nullable=False)
    policy_applied = Column(String(100))
    reason = Column(Text)
    delegated_by = Column(String(50), nullable=True)
    execution_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50), nullable=True, index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    asset_id = Column(String(50), nullable=False, index=True)
    authorized = Column(Boolean, nullable=False)
    reason = Column(Text)
    details = Column(Text)  # JSON string with full context
    severity = Column(String(20), default="INFO")  # INFO, WARNING, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)
    batch_id = Column(String(50), nullable=True, index=True)
