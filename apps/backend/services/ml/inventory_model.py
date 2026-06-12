"""
Inventory Forecast Model — LightGBM Regressor.
Predicts days_remaining from inventory and usage_rate.
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import os
import logging

logger = logging.getLogger(__name__)


class InventoryModel:
    """LightGBM regressor for inventory days-remaining prediction."""

    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = cache_dir
        self.model_path = os.path.join(cache_dir, "inventory_lgbm.joblib")
        self.model: lgb.LGBMRegressor | None = None
        self.is_trained = False

    def _generate_target(self, df: pd.DataFrame) -> np.ndarray:
        """Generate synthetic target: days_remaining based on inventory/usage_rate."""
        noise = np.random.normal(0, 2, size=len(df))
        usage = df["usage_rate"].values.clip(min=1)
        days = (df["inventory"].values / usage) * 10 + noise
        return days.clip(min=0)

    def train(self, df: pd.DataFrame) -> dict:
        """Train inventory model on dataset."""
        os.makedirs(self.cache_dir, exist_ok=True)

        features = df[["inventory", "usage_rate"]].copy()
        target = self._generate_target(df)

        self.model = lgb.LGBMRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            verbose=-1,
            force_col_wise=True,
        )
        self.model.fit(features, target)
        self.is_trained = True

        joblib.dump(self.model, self.model_path)
        logger.info(f"Inventory model trained and saved to {self.model_path}")

        return {"status": "trained", "features": ["inventory", "usage_rate"], "samples": len(df)}

    def load(self) -> bool:
        """Load cached model from disk."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info("Inventory model loaded from cache")
            return True
        return False

    def predict(self, inventory: float, usage_rate: float) -> dict:
        """Predict days remaining for given inventory/usage_rate."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("Inventory model not trained. Call train() first.")

        features = pd.DataFrame([{"inventory": inventory, "usage_rate": usage_rate}])
        prediction = self.model.predict(features)[0]
        days_remaining = max(0.0, round(float(prediction), 1))

        return {
            "days_remaining": days_remaining,
            "needs_restock": days_remaining < 20,
        }
