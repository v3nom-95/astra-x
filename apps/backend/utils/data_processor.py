"""
Data Processing Utility — CSV validation, parsing, and feature engineering.
"""
import pandas as pd
import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["asset_id", "type", "inventory", "usage_rate", "service_days", "temperature", "repairs"]
OPTIONAL_COLUMNS = ["location", "status"]

COLUMN_TYPES = {
    "asset_id": str,
    "type": str,
    "inventory": float,
    "usage_rate": float,
    "service_days": int,
    "temperature": float,
    "repairs": int,
    "location": str,
    "status": str,
}


def validate_csv(content: bytes | str) -> Tuple[pd.DataFrame, list[str]]:
    """
    Validate and parse CSV content.

    Returns:
        Tuple of (parsed DataFrame, list of validation errors)
    """
    errors = []

    try:
        if isinstance(content, bytes):
            try:
                content_str = content.decode("utf-8")
                df = pd.read_csv(io.StringIO(content_str))
            except UnicodeDecodeError:
                # Likely a binary Excel file
                df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_csv(io.StringIO(content))
    except Exception as e:
        return pd.DataFrame(), [f"File parsing error: {str(e)}"]

    # Normalize column names (strip whitespace, lowercase, replace spaces with underscores)
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    # Check required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return pd.DataFrame(), errors

    # Check for empty dataset
    if len(df) == 0:
        errors.append("Dataset is empty")
        return pd.DataFrame(), errors

    # Check for duplicate asset_ids and deduplicate to prevent db integrity crashes
    duplicates = df[df["asset_id"].duplicated()]["asset_id"].tolist()
    if duplicates:
        errors.append(f"Duplicate asset_ids found: {', '.join(str(d) for d in duplicates[:5])}. Only the last entry for each duplicate will be loaded.")
        df = df.drop_duplicates(subset=["asset_id"], keep="last")

    # Type coercion with error tracking
    for col, dtype in COLUMN_TYPES.items():
        if col in df.columns:
            try:
                if dtype == int:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
                elif dtype == float:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
                else:
                    # Clean string conversion to avoid .0 suffix on numeric values in Excel
                    def clean_str(val):
                        if pd.isna(val) or val is None:
                            return "UNKNOWN"
                        if isinstance(val, float):
                            if val.is_integer():
                                return str(int(val))
                            return str(val)
                        return str(val).strip()
                    df[col] = df[col].apply(clean_str)
            except Exception as e:
                errors.append(f"Type conversion error for column '{col}': {str(e)}")

    # Add optional columns with defaults
    if "location" not in df.columns:
        df["location"] = "UNKNOWN"
    if "status" not in df.columns:
        df["status"] = "ACTIVE"

    # Validate ranges
    if (df["inventory"] < 0).any():
        errors.append("Negative inventory values detected")
        df["inventory"] = df["inventory"].clip(lower=0)

    if (df["usage_rate"] < 0).any():
        errors.append("Negative usage_rate values detected")
        df["usage_rate"] = df["usage_rate"].clip(lower=0)

    logger.info(f"CSV validated: {len(df)} rows, {len(errors)} errors")
    return df, errors


def df_to_assets(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of asset dictionaries."""
    return df.to_dict(orient="records")
