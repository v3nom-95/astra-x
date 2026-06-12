"""
Assets API — CRUD operations for operational assets.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.engine import get_db
from models import Asset
from schemas import AssetResponse

router = APIRouter(tags=["Assets"])


@router.get("/assets", response_model=list[AssetResponse])
async def get_assets(
    status: str | None = None,
    asset_type: str | None = None,
    location: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all assets with optional filtering."""
    query = db.query(Asset)

    if status:
        query = query.filter(Asset.status == status)
    if asset_type:
        query = query.filter(Asset.type == asset_type)
    if location:
        query = query.filter(Asset.location == location)

    assets = query.order_by(Asset.asset_id).all()
    return assets
