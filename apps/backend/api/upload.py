"""
Upload API — CSV file upload, validation, and asset ingestion.
"""
import uuid
import json
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from db.engine import get_db
from models import Asset
from schemas import UploadResponse
from utils.data_processor import validate_csv, df_to_assets
from services.ml.model_manager import ModelManager

router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV dataset of operational assets.
    Validates the data, stores assets in DB, and retrains ML models.
    """
    content = await file.read()
    df, errors = validate_csv(content)

    if df.empty:
        return UploadResponse(
            message="Upload failed — invalid CSV",
            assets_loaded=0,
            batch_id="",
            validation_errors=errors,
        )

    batch_id = str(uuid.uuid4())[:8]
    assets = df_to_assets(df)
    loaded_count = 0

    for asset_data in assets:
        # Upsert: update existing or create new
        existing = db.query(Asset).filter(Asset.asset_id == asset_data["asset_id"]).first()
        if existing:
            for key, value in asset_data.items():
                if key != "asset_id" and hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            db_asset = Asset(**{k: v for k, v in asset_data.items() if hasattr(Asset, k)})
            db.add(db_asset)
        loaded_count += 1

    db.commit()

    # Retrain ML models with new data
    try:
        model_manager = ModelManager.get_instance()
        model_manager.train_all(df)
    except Exception as e:
        errors.append(f"Model training warning: {str(e)}")

    return UploadResponse(
        message=f"Successfully loaded {loaded_count} assets",
        assets_loaded=loaded_count,
        batch_id=batch_id,
        validation_errors=errors,
    )
