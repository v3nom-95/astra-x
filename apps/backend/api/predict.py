"""
Predict API — ML prediction endpoints for inventory, maintenance, and risk.
"""
import uuid
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from db.engine import get_db
from models import Asset, Prediction
from schemas import (
    InventoryPredictionInput, InventoryPredictionResult,
    MaintenancePredictionInput, MaintenancePredictionResult,
    RiskPredictionInput, RiskPredictionResult,
    BatchPredictionResponse, PredictionResponse,
)
from services.ml.model_manager import ModelManager

router = APIRouter(tags=["Predictions"])


@router.post("/predict/inventory", response_model=InventoryPredictionResult)
async def predict_inventory(input_data: InventoryPredictionInput):
    """Predict days remaining for a single asset."""
    model_manager = ModelManager.get_instance()
    result = model_manager.predict_inventory(input_data.inventory, input_data.usage_rate)
    return InventoryPredictionResult(asset_id=input_data.asset_id, **result)


@router.post("/predict/maintenance", response_model=MaintenancePredictionResult)
async def predict_maintenance(input_data: MaintenancePredictionInput):
    """Predict failure probability for a single asset."""
    model_manager = ModelManager.get_instance()
    result = model_manager.predict_maintenance(
        input_data.temperature, input_data.service_days, input_data.repairs
    )
    return MaintenancePredictionResult(asset_id=input_data.asset_id, **result)


@router.post("/predict/risk", response_model=RiskPredictionResult)
async def predict_risk(input_data: RiskPredictionInput):
    """Detect risk level for a single asset."""
    model_manager = ModelManager.get_instance()
    result = model_manager.predict_risk(
        input_data.usage_rate, input_data.service_days, input_data.repairs
    )
    return RiskPredictionResult(asset_id=input_data.asset_id, **result)


@router.post("/predict", response_model=BatchPredictionResponse)
async def predict_all(
    asset_ids: Optional[list[str]] = None,
    db: Session = Depends(get_db),
):
    """
    Run all predictions for assets in the database.
    Optionally filter by asset_ids.
    """
    query = db.query(Asset)
    if asset_ids:
        query = query.filter(Asset.asset_id.in_(asset_ids))
    assets = query.all()

    if not assets:
        return BatchPredictionResponse(
            batch_id="empty",
            predictions=[],
            total_assets=0,
            high_risk_count=0,
            needs_service_count=0,
            needs_restock_count=0,
        )

    model_manager = ModelManager.get_instance()
    batch_id = str(uuid.uuid4())[:8]
    predictions = []

    for asset in assets:
        asset_dict = {
            "asset_id": asset.asset_id,
            "inventory": asset.inventory,
            "usage_rate": asset.usage_rate,
            "temperature": asset.temperature,
            "service_days": asset.service_days,
            "repairs": asset.repairs,
        }
        pred = model_manager.predict_all(asset_dict)

        # Save to DB
        for pred_type in ["inventory", "maintenance", "risk"]:
            if pred_type in pred and "error" not in pred[pred_type]:
                db_pred = Prediction(
                    asset_id=asset.asset_id,
                    prediction_type=pred_type,
                    input_data=json.dumps(asset_dict),
                    result=json.dumps(pred[pred_type]),
                    batch_id=batch_id,
                )
                db.add(db_pred)

        inv = pred.get("inventory", {})
        maint = pred.get("maintenance", {})
        risk = pred.get("risk", {})

        predictions.append(PredictionResponse(
            asset_id=asset.asset_id,
            inventory=InventoryPredictionResult(
                asset_id=asset.asset_id,
                days_remaining=inv.get("days_remaining", 0),
                needs_restock=inv.get("needs_restock", False),
            ) if "error" not in inv else None,
            maintenance=MaintenancePredictionResult(
                asset_id=asset.asset_id,
                failure_probability=maint.get("failure_probability", 0),
                needs_service=maint.get("needs_service", False),
            ) if "error" not in maint else None,
            risk=RiskPredictionResult(
                asset_id=asset.asset_id,
                risk=risk.get("risk", "LOW"),
                anomaly_score=risk.get("anomaly_score", 0),
            ) if "error" not in risk else None,
        ))

    db.commit()

    high_risk = sum(1 for p in predictions if p.risk and p.risk.risk == "HIGH")
    needs_service = sum(1 for p in predictions if p.maintenance and p.maintenance.needs_service)
    needs_restock = sum(1 for p in predictions if p.inventory and p.inventory.needs_restock)

    return BatchPredictionResponse(
        batch_id=batch_id,
        predictions=predictions,
        total_assets=len(predictions),
        high_risk_count=high_risk,
        needs_service_count=needs_service,
        needs_restock_count=needs_restock,
    )
