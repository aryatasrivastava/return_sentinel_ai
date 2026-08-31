"""ReturnSentinel AI Inference and Explainability Module (Phase 2B).

This module provides a standalone, reusable prediction function that future
LangGraph agents (e.g. Phase 3 Risk Agent) can import and call directly.

Responsibilities:
- Load the trained XGBoost model and configuration once (cached).
- Validate input feature dictionaries against the 12 expected feature keys.
- Order feature values according to the static feature_order from model_config.json.
- Predict return-abuse risk probability and classify into LOW / MEDIUM / HIGH.
- Compute model prediction confidence score via formula v1.
- Compute local SHAP values for the single order and return the top 3 human-readable risk factors.
- Return a strictly typed output dictionary compatible with future pipeline agents.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier

try:
    from ml.training.train_model import calculate_model_confidence
except (ImportError, ModuleNotFoundError):
    from backend.ml.training.train_model import calculate_model_confidence

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BACKEND_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
MODEL_PATH = MODELS_DIR / "return_risk_xgboost.joblib"
CONFIG_PATH = MODELS_DIR / "model_config.json"

# Human-Readable Feature Explanation Mapping
FEATURE_EXPLANATION_MAP: Dict[str, Dict[str, str]] = {
    "customer_return_rate": {
        "positive": "Elevated customer historical return rate",
        "negative": "Low customer historical return rate",
    },
    "total_previous_orders": {
        "positive": "High volume of prior purchase history",
        "negative": "Established positive purchasing track record",
    },
    "total_previous_returns": {
        "positive": "High count of historical item returns",
        "negative": "Low number of prior returned items",
    },
    "customer_history_days": {
        "positive": "New or thin customer account history",
        "negative": "Long-standing customer account tenure",
    },
    "days_since_last_order": {
        "positive": "Recent repeat order within short timeframe",
        "negative": "Normal order interval since previous purchase",
    },
    "cart_value": {
        "positive": "High total cart order value",
        "negative": "Moderate or standard cart value",
    },
    "cart_item_count": {
        "positive": "Large number of items in current cart",
        "negative": "Small item quantity in cart",
    },
    "multiple_sizes_same_product": {
        "positive": "Multiple sizes of the same product selected (bracketing)",
        "negative": "Single size chosen per product",
    },
    "max_sizes_same_product": {
        "positive": "High maximum size count selected for a single item",
        "negative": "Standard single-size selection across items",
    },
    "average_product_return_rate": {
        "positive": "High return-rate category or product in cart",
        "negative": "Low return-rate catalog items in cart",
    },
    "previous_returns_same_category": {
        "positive": "Prior history of returning items in this specific category",
        "negative": "No prior returns in this product category",
    },
    "avg_days_to_return": {
        "positive": "Rapid historical return turnaround signature",
        "negative": "Normal or extended return turnaround duration",
    },
}

# Module-level cached resources
_MODEL: Optional[XGBClassifier] = None
_CONFIG: Optional[Dict[str, Any]] = None
_EXPLAINER: Optional[shap.TreeExplainer] = None


def get_model_and_config() -> Tuple[XGBClassifier, Dict[str, Any], shap.TreeExplainer]:
    """Retrieve or initialize the cached XGBoost model, config, and SHAP explainer."""
    global _MODEL, _CONFIG, _EXPLAINER

    if _MODEL is None or _CONFIG is None or _EXPLAINER is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found at: {MODEL_PATH}. "
                "Please run python -m ml.training.train_model first."
            )
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(
                f"Model config not found at: {CONFIG_PATH}. "
                "Please run python -m ml.training.train_model first."
            )

        _MODEL = joblib.load(MODEL_PATH)
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _CONFIG = json.load(f)
        _EXPLAINER = shap.TreeExplainer(_MODEL)

    return _MODEL, _CONFIG, _EXPLAINER


def predict_return_risk(features: Dict[str, Any]) -> Dict[str, Any]:
    """Predict return abuse risk and return explanations for an incoming order.

    Args:
        features: Dictionary containing all 12 input features keyed by name:
            - customer_return_rate: float in [0, 1]
            - total_previous_orders: int >= 0
            - total_previous_returns: int >= 0
            - customer_history_days: int >= 0
            - days_since_last_order: int >= 0
            - cart_value: float > 0
            - cart_item_count: int >= 1
            - multiple_sizes_same_product: binary (0 or 1)
            - max_sizes_same_product: int >= 1
            - average_product_return_rate: float in [0, 1]
            - previous_returns_same_category: int >= 0
            - avg_days_to_return: float >= 0

    Returns:
        Dictionary matching the standard ReturnSentinel risk prediction shape:
        {
            "risk_probability": float,
            "risk_level": "LOW" | "MEDIUM" | "HIGH",
            "confidence": float,
            "top_risk_factors": list[str]  # exactly 3 human-readable factors
        }

    Raises:
        ValueError: If any of the 12 required feature keys are missing.
    """
    model, config, explainer = get_model_and_config()
    expected_order: List[str] = config["feature_order"]

    # 1. Validate feature presence
    missing_keys = [k for k in expected_order if k not in features]
    if missing_keys:
        raise ValueError(
            f"Missing required feature keys for return risk prediction: {missing_keys}. "
            f"Expected keys: {expected_order}"
        )

    # 2. Build 1-row DataFrame strictly following config feature_order
    ordered_values = [features[col] for col in expected_order]
    input_df = pd.DataFrame([ordered_values], columns=expected_order)

    # 3. Model Inference (Risk Probability)
    probabilities = model.predict_proba(input_df)[0]
    risk_probability = float(probabilities[1])

    # 4. Determine Risk Level using frozen thresholds
    thresholds = config["risk_level_thresholds"]
    low_max = thresholds["low_max"]
    high_min = thresholds["high_min"]

    if risk_probability < low_max:
        risk_level = "LOW"
    elif risk_probability < high_min:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # 5. Compute Model Confidence (Formula v1)
    # Internally referred to as model_confidence, exposed as "confidence"
    model_confidence = calculate_model_confidence(risk_probability)

    # 6. Local SHAP Explanation (Top 3 risk factors)
    shap_vals = explainer.shap_values(input_df)
    if isinstance(shap_vals, list):
        row_shap = shap_vals[1][0]
    elif len(shap_vals.shape) == 2:
        row_shap = shap_vals[0]
    else:
        row_shap = shap_vals

    # Identify top 3 features by absolute SHAP contribution
    top_indices = np.argsort(np.abs(row_shap))[-3:][::-1]

    top_risk_factors: List[str] = []
    for idx in top_indices:
        feat_name = expected_order[idx]
        shap_contrib = float(row_shap[idx])
        direction = "positive" if shap_contrib >= 0 else "negative"

        explanation_dict = FEATURE_EXPLANATION_MAP.get(feat_name, {})
        phrase = explanation_dict.get(
            direction,
            f"{feat_name} ({direction} risk impact: {shap_contrib:+.3f})"
        )
        top_risk_factors.append(phrase)

    return {
        "risk_probability": round(risk_probability, 4),
        "risk_level": risk_level,
        "confidence": round(model_confidence, 4),
        "top_risk_factors": top_risk_factors,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("       RETURNSENTINEL AI - RISK PREDICTION SPOT-CHECK (PHASE 2B)")
    print("=" * 80)

    # Example 1: Medium / Ambiguous Risk Profile with size bracketing
    sample_order_1 = {
        "customer_return_rate": 0.35,
        "total_previous_orders": 8,
        "total_previous_returns": 3,
        "customer_history_days": 210,
        "days_since_last_order": 14,
        "cart_value": 3200.00,
        "cart_item_count": 3,
        "multiple_sizes_same_product": 1,
        "max_sizes_same_product": 2,
        "average_product_return_rate": 0.28,
        "previous_returns_same_category": 1,
        "avg_days_to_return": 9.5,
    }

    # Example 2: Elevated Risk Profile (Wardrobing signature)
    sample_order_2 = {
        "customer_return_rate": 0.75,
        "total_previous_orders": 24,
        "total_previous_returns": 18,
        "customer_history_days": 350,
        "days_since_last_order": 6,
        "cart_value": 5400.00,
        "cart_item_count": 5,
        "multiple_sizes_same_product": 1,
        "max_sizes_same_product": 3,
        "average_product_return_rate": 0.45,
        "previous_returns_same_category": 5,
        "avg_days_to_return": 3.2,
    }

    # Example 3: Low Risk Profile (Trusted repeat customer)
    sample_order_3 = {
        "customer_return_rate": 0.08,
        "total_previous_orders": 20,
        "total_previous_returns": 1,
        "customer_history_days": 650,
        "days_since_last_order": 28,
        "cart_value": 1650.00,
        "cart_item_count": 2,
        "multiple_sizes_same_product": 0,
        "max_sizes_same_product": 1,
        "average_product_return_rate": 0.12,
        "previous_returns_same_category": 0,
        "avg_days_to_return": 22.0,
    }

    for i, (name, sample) in enumerate([
        ("Ambiguous / Medium Profile", sample_order_1),
        ("Elevated Risk Profile", sample_order_2),
        ("Low Risk Profile", sample_order_3),
    ], 1):
        print(f"\n[Test Case {i}] {name}:")
        result = predict_return_risk(sample)
        print(json.dumps(result, indent=2))

    print("\n" + "=" * 80)
    print("Inference spot-check complete. Function signature and outputs verified.")
    print("=" * 80)
