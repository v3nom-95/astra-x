"""
Audit API — Query and filter audit logs.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.engine import get_db
from models import AuditLog
from schemas import AuditResponse, AuditEntry

router = APIRouter(tags=["Audit"])


@router.get("/audit", response_model=AuditResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    asset_id: str | None = None,
    agent_name: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Query audit logs with optional filtering by asset, agent, or severity.
    """
    query = db.query(AuditLog)

    if asset_id:
        query = query.filter(AuditLog.asset_id == asset_id)
    if agent_name:
        query = query.filter(AuditLog.agent_name == agent_name)
    if severity:
        query = query.filter(AuditLog.severity == severity)

    total = query.count()
    entries = (
        query.order_by(desc(AuditLog.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AuditResponse(
        entries=[
            AuditEntry(
                id=e.id,
                agent_name=e.agent_name,
                action=e.action,
                asset_id=e.asset_id,
                authorized=e.authorized,
                reason=e.reason or "",
                details=e.details,
                severity=e.severity or "INFO",
                created_at=e.created_at,
            )
            for e in entries
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
