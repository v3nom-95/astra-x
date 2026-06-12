"""
Predictive Maintenance Model — XGBoost Classifier.
Predicts failure_probability from temperature, service_days, and repairs.
"""
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import os
import logging

logger = logging.getLogger(__name__)


class MaintenanceModel:
    """XGBoost classifier for predictive maintenance."""

    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = cache_dir
        self.model_path = os.path.join(cache_dir, "maintenance_xgb.joblib")
        self.model: xgb.XGBClassifier | None = None
        self.is_trained = False

    def _generate_labels(self, df: pd.DataFrame) -> np.ndarray:
        """Generate synthetic failure labels based on threshold rules."""
        scores = (
            (df["temperature"].values / 100) * 0.4
            + (df["service_days"].values / 300) * 0.3
            + (df["repairs"].values / 10) * 0.3
        )
        # Add noise for model learning
        noise = np.random.normal(0, 0.05, size=len(df))
        scores = (scores + noise).clip(0, 1)
        labels = (scores > 0.5).astype(int)
        return labels

    def train(self, df: pd.DataFrame) -> dict:
        """Train maintenance model on dataset."""
        os.makedirs(self.cache_dir, exist_ok=True)

        features = df[["temperature", "service_days", "repairs"]].copy()
        labels = self._generate_labels(df)

        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
            eval_metric="logloss",
            use_label_encoder=False,
        )
        self.model.fit(features, labels)
        self.is_trained = True

        joblib.dump(self.model, self.model_path)
        logger.info(f"Maintenance model trained and saved to {self.model_path}")

        return {"status": "trained", "features": ["temperature", "service_days", "repairs"], "samples": len(df)}

    def load(self) -> bool:
        """Load cached model from disk."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info("Maintenance model loaded from cache")
            return True
        return False

    def predict(self, temperature: float, service_days: int, repairs: int) -> dict:
        """Predict failure probability."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("Maintenance model not trained. Call train() first.")

        features = pd.DataFrame([{
            "temperature": temperature,
            "service_days": service_days,
            "repairs": repairs,
        }])

        proba = self.model.predict_proba(features)[0]
        failure_prob = round(float(proba[1]), 2) if len(proba) > 1 else round(float(proba[0]), 2)

        return {
            "failure_probability": failure_prob,
            "needs_service": failure_prob > 0.80,
        }
