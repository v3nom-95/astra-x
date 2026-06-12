"""
ASTRA-X ML Services Package.
Provides model training, caching, and prediction for:
- Inventory forecasting (LightGBM)
- Predictive maintenance (XGBoost)
- Risk detection (Isolation Forest)
"""
from services.ml.model_manager import ModelManager

__all__ = ["ModelManager"]
