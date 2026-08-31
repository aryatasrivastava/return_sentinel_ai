"""ReturnSentinel AI Model Training (Phase 2B).

This module trains an XGBoost binary classification model to predict return-abuse
risk on e-commerce orders prior to payment, using the validated synthetic dataset.

Responsibilities:
- Load and strictly validate the 13-column dataset schema.
- Perform a reproducible stratified 70/15/15 train/validation/test split (seed=42).
- Train an XGBClassifier with fixed hyperparameters and early stopping on validation AUC.
- Determine operational risk-level thresholds from the validation set probability distribution.
- Implement model confidence computation (formula v1).
- Export trained model to ml/models/return_risk_xgboost.joblib.
- Export full configuration metadata to ml/models/model_config.json.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
import sklearn
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split

# ==============================================================================
# Hyperparameters and Configuration Constants (No magic numbers inline)
# ==============================================================================
RANDOM_STATE = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# XGBoost Hyperparameters
N_ESTIMATORS = 150
MAX_DEPTH = 4
LEARNING_RATE = 0.08
SUBSAMPLE = 0.8
COLSAMPLE_BYTREE = 0.8
EVAL_METRIC = "auc"
EARLY_STOPPING_ROUNDS = 15

# Provisional Risk-Level Thresholds
PROVISIONAL_LOW_MAX = 0.30
PROVISIONAL_HIGH_MIN = 0.65

# Exact 12 input features in required order + 1 target
FEATURE_COLUMNS: List[str] = [
    "customer_return_rate",
    "total_previous_orders",
    "total_previous_returns",
    "customer_history_days",
    "days_since_last_order",
    "cart_value",
    "cart_item_count",
    "multiple_sizes_same_product",
    "max_sizes_same_product",
    "average_product_return_rate",
    "previous_returns_same_category",
    "avg_days_to_return",
]
TARGET_COLUMN = "return_abuse_label"
EXPECTED_COLUMNS: List[str] = FEATURE_COLUMNS + [TARGET_COLUMN]

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BACKEND_DIR / "ml"
DATA_PATH = ML_DIR / "data" / "returnsentinel_synthetic_dataset.csv"
MODELS_DIR = ML_DIR / "models"
MODEL_SAVE_PATH = MODELS_DIR / "return_risk_xgboost.joblib"
CONFIG_SAVE_PATH = MODELS_DIR / "model_config.json"


def calculate_model_confidence(risk_probability: float) -> float:
    """Calculate prediction confidence score for a model probability output.

    Formula:
        model_confidence = 2 * abs(risk_probability - 0.5)

    Notes:
        This measures the model's intrinsic confidence in its classification
        based on the margin from the 0.5 decision boundary (ranging from 0.0 at
        maximum uncertainty p=0.5 to 1.0 at certain p=0.0 or p=1.0).
        This is distinct from, and must not be confused with, the future LangGraph
        Confidence Router's composite confidence score (which will later combine
        this value with evidence-completeness and data-freshness signals).
    """
    return float(2.0 * abs(risk_probability - 0.5))


def load_and_validate_dataset(data_path: Path) -> Tuple[pd.DataFrame, pd.Series]:
    """Load dataset from disk and strictly validate column schema."""
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {data_path}")

    df = pd.read_csv(data_path)

    # Validate exact column count and column names
    actual_columns = list(df.columns)
    if actual_columns != EXPECTED_COLUMNS:
        raise ValueError(
            f"Dataset schema mismatch! Expected {len(EXPECTED_COLUMNS)} columns:\n"
            f"  Expected: {EXPECTED_COLUMNS}\n"
            f"  Actual:   {actual_columns}"
        )

    # Validate row count
    if len(df) != 8000:
        raise ValueError(f"Expected exactly 8,000 rows in dataset, got {len(df)}")

    # Validate zero nulls
    null_count = int(df.isnull().sum().sum())
    if null_count > 0:
        raise ValueError(f"Dataset contains {null_count} null/missing values.")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    return X, y


def split_data(
    X: pd.DataFrame, y: pd.Series
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """Perform a stratified 70/15/15 train/validation/test split using fixed seed."""
    # First split: 70% train, 30% temp
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=(VAL_RATIO + TEST_RATIO),
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Second split: 50/50 of temp -> 15% val, 15% test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    return X_train, X_val, X_test, y_train, y_val, y_test


def evaluate_risk_thresholds(
    y_val: pd.Series, val_probs: np.ndarray
) -> Tuple[Dict[str, float], str]:
    """Evaluate and freeze risk thresholds using the validation set only."""
    low_mask = val_probs < PROVISIONAL_LOW_MAX
    med_mask = (val_probs >= PROVISIONAL_LOW_MAX) & (val_probs < PROVISIONAL_HIGH_MIN)
    high_mask = val_probs >= PROVISIONAL_HIGH_MIN

    low_count = int(low_mask.sum())
    med_count = int(med_mask.sum())
    high_count = int(high_mask.sum())
    total_val = len(val_probs)

    # Check precision on high-risk bucket
    high_actual_pos = int(y_val[high_mask].sum())
    high_precision = high_actual_pos / high_count if high_count > 0 else 0.0

    # Check true positive capture rate in high bucket
    total_pos = int(y_val.sum())
    high_recall = high_actual_pos / total_pos if total_pos > 0 else 0.0

    justification = (
        f"Provisional thresholds [low < {PROVISIONAL_LOW_MAX:.2f}, "
        f"medium {PROVISIONAL_LOW_MAX:.2f}-{PROVISIONAL_HIGH_MIN:.2f}, "
        f"high >= {PROVISIONAL_HIGH_MIN:.2f}] confirmed on validation set: "
        f"Low={low_count} ({low_count/total_val:.1%}), "
        f"Med={med_count} ({med_count/total_val:.1%}), "
        f"High={high_count} ({high_count/total_val:.1%}) with "
        f"High-tier Precision={high_precision:.1%}, Recall={high_recall:.1%}."
    )

    thresholds = {
        "low_max": PROVISIONAL_LOW_MAX,
        "high_min": PROVISIONAL_HIGH_MIN,
    }

    return thresholds, justification


def train_and_save_model() -> None:
    """Execute complete model training and artifact persistence workflow."""
    print("=" * 80)
    print("          RETURNSENTINEL AI - XGBOOST MODEL TRAINING (PHASE 2B)")
    print("=" * 80)

    # 1. Load and validate dataset
    print(f"\n[1/5] Loading dataset from: {DATA_PATH}")
    X, y = load_and_validate_dataset(DATA_PATH)
    print(f"  [OK] Dataset validated: {len(X)} rows, {len(FEATURE_COLUMNS)} feature columns.")
    print(f"  [OK] Target distribution: {y.value_counts().to_dict()} (positive rate: {y.mean():.2%})")

    # 2. Stratified 70/15/15 Train/Validation/Test Split
    print(f"\n[2/5] Partitioning data into Stratified 70/15/15 splits (random_state={RANDOM_STATE})...")
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)
    print(f"  - Train split:      {len(X_train)} rows ({len(X_train)/len(X):.1%}), pos rate: {y_train.mean():.2%}")
    print(f"  - Validation split: {len(X_val)} rows ({len(X_val)/len(X):.1%}), pos rate: {y_val.mean():.2%}")
    print(f"  - Test split:       {len(X_test)} rows ({len(X_test)/len(X):.1%}), pos rate: {y_test.mean():.2%}")

    # 3. Train XGBoost Classifier
    print(f"\n[3/5] Initializing and training XGBClassifier...")
    print(f"  - Hyperparameters: n_estimators={N_ESTIMATORS}, max_depth={MAX_DEPTH}, learning_rate={LEARNING_RATE}")
    print(f"  - Subsample={SUBSAMPLE}, colsample_bytree={COLSAMPLE_BYTREE}, early_stopping_rounds={EARLY_STOPPING_ROUNDS}")

    model = xgb.XGBClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        learning_rate=LEARNING_RATE,
        subsample=SUBSAMPLE,
        colsample_bytree=COLSAMPLE_BYTREE,
        eval_metric=EVAL_METRIC,
        random_state=RANDOM_STATE,
        early_stopping_rounds=EARLY_STOPPING_ROUNDS,
    )

    # Train with early stopping monitored strictly on validation set
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=15,
    )

    best_iter = model.best_iteration if hasattr(model, "best_iteration") else N_ESTIMATORS
    best_score = model.best_score if hasattr(model, "best_score") else 0.0
    print(f"  [OK] Training completed. Best iteration: {best_iter}, Best Validation AUC: {best_score:.4f}")

    # 4. Determine and Freeze Risk Thresholds
    print(f"\n[4/5] Evaluating risk thresholds on validation set...")
    val_probs = model.predict_proba(X_val)[:, 1]
    thresholds, threshold_justification = evaluate_risk_thresholds(y_val, val_probs)
    print(f"  [OK] {threshold_justification}")

    # 5. Export Model and Config Artifacts
    print(f"\n[5/5] Saving model and configuration artifacts...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Save model via joblib
    joblib.dump(model, MODEL_SAVE_PATH)
    print(f"  [OK] Model artifact saved to: {MODEL_SAVE_PATH}")

    # Build model_config.json
    model_config = {
        "feature_order": FEATURE_COLUMNS,
        "risk_level_thresholds": thresholds,
        "threshold_justification": threshold_justification,
        "confidence_formula_version": "model_confidence_v1",
        "random_seed": RANDOM_STATE,
        "split_ratio": {
            "train": TRAIN_RATIO,
            "validation": VAL_RATIO,
            "test": TEST_RATIO,
        },
        "xgboost_config": {
            "n_estimators": N_ESTIMATORS,
            "max_depth": MAX_DEPTH,
            "learning_rate": LEARNING_RATE,
            "subsample": SUBSAMPLE,
            "colsample_bytree": COLSAMPLE_BYTREE,
            "eval_metric": EVAL_METRIC,
            "early_stopping_rounds": EARLY_STOPPING_ROUNDS,
            "best_iteration": int(best_iter) if best_iter is not None else N_ESTIMATORS,
            "best_val_auc": float(best_score),
        },
        "training_date": datetime.now(timezone.utc).isoformat(),
        "library_versions": {
            "xgboost": xgb.__version__,
            "scikit-learn": sklearn.__version__,
            "shap": shap.__version__,
            "joblib": joblib.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }

    with open(CONFIG_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)
    print(f"  [OK] Configuration metadata saved to: {CONFIG_SAVE_PATH}")

    print("\n" + "=" * 80)
    print("Training phase complete. Ready for evaluation via ml.training.evaluate_model.")
    print("=" * 80)


if __name__ == "__main__":
    train_and_save_model()
