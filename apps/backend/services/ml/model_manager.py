"""
ML Model Manager — Orchestrates training, caching, and prediction for all models.
Implements lazy loading and train-if-missing pattern for fast startup.
"""
import os
import pandas as pd
import logging
from typing import Optional

from services.ml.inventory_model import InventoryModel
from services.ml.maintenance_model import MaintenanceModel
from services.ml.risk_model import RiskModel

logger = logging.getLogger(__name__)


class ModelManager:
    """Central manager for all ML models. Handles lifecycle, caching, and predictions."""

    _instance: Optional["ModelManager"] = None

    def __init__(self, cache_dir: str | None = None):
        self.cache_dir = cache_dir or os.getenv("MODEL_CACHE_DIR", "./model_cache")
        self.inventory_model = InventoryModel(self.cache_dir)
        self.maintenance_model = MaintenanceModel(self.cache_dir)
        self.risk_model = RiskModel(self.cache_dir)
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "ModelManager":
        """Singleton pattern for model manager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def status(self) -> dict:
        """Return training status of all models."""
        return {
            "inventory": "ready" if self.inventory_model.is_trained else "not_trained",
            "maintenance": "ready" if self.maintenance_model.is_trained else "not_trained",
            "risk": "ready" if self.risk_model.is_trained else "not_trained",
        }

    def initialize(self, data_path: str | None = None) -> dict:
        """
        Initialize all models — load from cache or train from data.
        Called at application startup.
        """
        if self._initialized:
            return self.status

        results = {}

        # Try loading cached models first
        inv_loaded = self.inventory_model.load()
        maint_loaded = self.maintenance_model.load()
        risk_loaded = self.risk_model.load()

        if inv_loaded and maint_loaded and risk_loaded:
            logger.info("All models loaded from cache")
            self._initialized = True
            return self.status

        # Need to train — find data
        if data_path is None:
            # Search common paths
            search_paths = [
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "assets.csv"),
                os.path.join(os.path.dirname(__file__), "..", "..", "data", "assets.csv"),
                "./data/assets.csv",
                "../../data/assets.csv",
            ]
            for p in search_paths:
                resolved = os.path.abspath(p)
                if os.path.exists(resolved):
                    data_path = resolved
                    break

        if data_path is None or not os.path.exists(data_path):
            logger.warning("No training data found. Models will be trained on first upload.")
            return self.status

        logger.info(f"Training models from {data_path}")
        df = pd.read_csv(data_path)
        results = self.train_all(df)
        self._initialized = True
        return results

    def train_all(self, df: pd.DataFrame) -> dict:
        """Train all models on the provided dataset."""
        results = {}

        try:
            results["inventory"] = self.inventory_model.train(df)
        except Exception as e:
            logger.error(f"Inventory model training failed: {e}")
            results["inventory"] = {"status": "error", "error": str(e)}

        try:
            results["maintenance"] = self.maintenance_model.train(df)
        except Exception as e:
            logger.error(f"Maintenance model training failed: {e}")
            results["maintenance"] = {"status": "error", "error": str(e)}

        try:
            results["risk"] = self.risk_model.train(df)
        except Exception as e:
            logger.error(f"Risk model training failed: {e}")
            results["risk"] = {"status": "error", "error": str(e)}

        return results

    def predict_inventory(self, inventory: float, usage_rate: float) -> dict:
        """Get inventory forecast prediction."""
        return self.inventory_model.predict(inventory, usage_rate)

    def predict_maintenance(self, temperature: float, service_days: int, repairs: int) -> dict:
        """Get maintenance prediction."""
        return self.maintenance_model.predict(temperature, service_days, repairs)

    def predict_risk(self, usage_rate: float, service_days: int, repairs: int) -> dict:
        """Get risk detection prediction."""
        return self.risk_model.predict(usage_rate, service_days, repairs)

    def predict_all(self, asset: dict) -> dict:
        """Run all predictions for a single asset."""
        result = {"asset_id": asset.get("asset_id", "UNKNOWN")}

        try:
            result["inventory"] = self.predict_inventory(
                asset["inventory"], asset["usage_rate"]
            )
        except Exception as e:
            result["inventory"] = {"error": str(e)}

        try:
            result["maintenance"] = self.predict_maintenance(
                asset["temperature"], asset["service_days"], asset["repairs"]
            )
        except Exception as e:
            result["maintenance"] = {"error": str(e)}

        try:
            result["risk"] = self.predict_risk(
                asset["usage_rate"], asset["service_days"], asset["repairs"]
            )
        except Exception as e:
            result["risk"] = {"error": str(e)}

        return result
