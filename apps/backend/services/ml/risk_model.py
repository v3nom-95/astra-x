"""
Risk Detection Model — Isolation Forest (Anomaly Detection).
Detects anomalous asset behavior from usage_rate, service_days, and repairs.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import logging

logger = logging.getLogger(__name__)


class RiskModel:
    """Isolation Forest for unsupervised risk/anomaly detection."""

    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = cache_dir
        self.model_path = os.path.join(cache_dir, "risk_iforest.joblib")
        self.model: IsolationForest | None = None
        self.is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        """Train risk detection model on dataset."""
        os.makedirs(self.cache_dir, exist_ok=True)

        features = df[["usage_rate", "service_days", "repairs"]].copy()

        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.2,  # Expect ~20% anomalies
            random_state=42,
        )
        self.model.fit(features)
        self.is_trained = True

        joblib.dump(self.model, self.model_path)
        logger.info(f"Risk model trained and saved to {self.model_path}")

        return {"status": "trained", "features": ["usage_rate", "service_days", "repairs"], "samples": len(df)}

    def load(self) -> bool:
        """Load cached model from disk."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info("Risk model loaded from cache")
            return True
        return False

    def predict(self, usage_rate: float, service_days: int, repairs: int) -> dict:
        """Detect risk level for given asset metrics."""
        if not self.is_trained or self.model is None:
            raise RuntimeError("Risk model not trained. Call train() first.")

        features = pd.DataFrame([{
            "usage_rate": usage_rate,
            "service_days": service_days,
            "repairs": repairs,
        }])

        # Isolation Forest: -1 = anomaly, 1 = normal
        prediction = self.model.predict(features)[0]
        anomaly_score = -float(self.model.score_samples(features)[0])

        if prediction == -1:
            risk = "HIGH"
        elif anomaly_score > 0.3:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "risk": risk,
            "anomaly_score": round(anomaly_score, 3),
        }
