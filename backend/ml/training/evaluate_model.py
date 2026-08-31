"""ReturnSentinel AI Model Evaluation and Explainability (Phase 2B).

This module evaluates the trained XGBoost return-risk classification model across
stratified train, validation, and test splits, runs SHAP TreeExplainer global
explainability analysis, checks for overfitting/suspicious performance flags,
and exports comprehensive metrics and summaries.

Outputs:
- ml/reports/model_metrics.json
- ml/reports/feature_importance.csv
- ml/reports/evaluation_summary.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

try:
    from ml.training.train_model import (
        DATA_PATH,
        FEATURE_COLUMNS,
        RANDOM_STATE,
        TARGET_COLUMN,
        load_and_validate_dataset,
        split_data,
    )
except (ImportError, ModuleNotFoundError):
    from backend.ml.training.train_model import (
        DATA_PATH,
        FEATURE_COLUMNS,
        RANDOM_STATE,
        TARGET_COLUMN,
        load_and_validate_dataset,
        split_data,
    )

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BACKEND_DIR / "ml"
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"
MODEL_PATH = MODELS_DIR / "return_risk_xgboost.joblib"
CONFIG_PATH = MODELS_DIR / "model_config.json"
METRICS_SAVE_PATH = REPORTS_DIR / "model_metrics.json"
FEATURE_IMPORTANCE_SAVE_PATH = REPORTS_DIR / "feature_importance.csv"
EVAL_SUMMARY_PATH = REPORTS_DIR / "evaluation_summary.md"


def compute_split_metrics(
    y_true: pd.Series,
    y_probs: np.ndarray,
    operational_threshold: float = 0.65,
) -> Dict[str, Any]:
    """Compute comprehensive evaluation metrics for a single data split."""
    y_pred_default = (y_probs >= 0.50).astype(int)
    y_pred_operational = (y_probs >= operational_threshold).astype(int)

    roc_auc = float(roc_auc_score(y_true, y_probs))
    pr_auc = float(average_precision_score(y_true, y_probs))
    accuracy = float(accuracy_score(y_true, y_pred_default))
    precision = float(precision_score(y_true, y_pred_default, zero_division=0))
    recall = float(recall_score(y_true, y_pred_default, zero_division=0))
    f1 = float(f1_score(y_true, y_pred_default, zero_division=0))

    cm_default = confusion_matrix(y_true, y_pred_default).tolist()
    cm_operational = confusion_matrix(y_true, y_pred_operational).tolist()

    prec_operational = float(precision_score(y_true, y_pred_operational, zero_division=0))
    rec_operational = float(recall_score(y_true, y_pred_operational, zero_division=0))
    f1_operational = float(f1_score(y_true, y_pred_operational, zero_division=0))

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "accuracy": accuracy,
        "precision_at_0_50": precision,
        "recall_at_0_50": recall,
        "f1_at_0_50": f1,
        "confusion_matrix_at_0_50": cm_default,
        "operational_threshold": operational_threshold,
        "precision_at_operational": prec_operational,
        "recall_at_operational": rec_operational,
        "f1_at_operational": f1_operational,
        "confusion_matrix_at_operational": cm_operational,
    }


def compute_shap_importance(
    model: Any, X_test: pd.DataFrame
) -> Tuple[pd.DataFrame, np.ndarray]:
    """Compute global feature importances using SHAP TreeExplainer on test set."""
    print("  - Initializing shap.TreeExplainer on trained model...")
    explainer = shap.TreeExplainer(model)
    print(f"  - Computing SHAP values on test set ({len(X_test)} instances)...")
    shap_values = explainer.shap_values(X_test)

    # In binary XGBoost with recent shap versions, shap_values is a 2D ndarray of shape (N, D)
    if isinstance(shap_values, list):
        # If returned as list [class_0, class_1]
        shap_matrix = shap_values[1]
    else:
        shap_matrix = shap_values

    # Mean absolute SHAP contribution per feature
    mean_abs_shap = np.abs(shap_matrix).mean(axis=0)
    importance_df = pd.DataFrame({
        "feature": X_test.columns,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)

    return importance_df, shap_matrix


def generate_evaluation_summary(
    metrics: Dict[str, Any],
    importance_df: pd.DataFrame,
    config: Dict[str, Any],
) -> str:
    """Generate human-readable markdown evaluation summary."""
    train_m = metrics["train"]
    val_m = metrics["validation"]
    test_m = metrics["test"]
    gap = metrics["overfitting_check"]["train_val_auc_gap"]
    overfitting_flag = metrics["overfitting_check"]["overfitting_warning"]
    suspicious_flag = metrics["suspicious_data_check"]["suspiciously_easy_data_warning"]

    overfitting_verdict = (
        f"**FLAGGED**: Train-Val ROC-AUC gap ({gap:.4f}) exceeds the 0.08 threshold."
        if overfitting_flag
        else f"**PASSED**: Train-Val ROC-AUC gap is {gap:.4f} (<= 0.08 threshold). Generalization is strong."
    )

    suspicious_verdict = (
        f"**FLAGGED**: Test ROC-AUC ({test_m['roc_auc']:.4f}) exceeds 0.95. Synthetic feature noise may be too low."
        if suspicious_flag
        else f"**PASSED**: Test ROC-AUC is {test_m['roc_auc']:.4f} (<= 0.95). Data shows realistic behavioral overlap."
    )

    top5_rows = "\n".join([
        f"| {i+1} | `{row['feature']}` | {row['mean_abs_shap']:.4f} |"
        for i, row in importance_df.head(5).iterrows()
    ])

    summary_md = f"""# ReturnSentinel AI — XGBoost Risk Model Evaluation Summary (Phase 2B)

## Executive Summary
This report summarizes the performance and explainability of the ReturnSentinel AI pre-payment return-abuse XGBoost classification model trained on the Phase 2A synthetic dataset (8,000 orders).

---

## 1. Train / Validation / Test Performance Comparison

| Metric | Train Split (70% / 5,600 rows) | Validation Split (15% / 1,200 rows) | Test Split (15% / 1,200 rows) |
| :--- | :---: | :---: | :---: |
| **ROC-AUC** | **{train_m['roc_auc']:.4f}** | **{val_m['roc_auc']:.4f}** | **{test_m['roc_auc']:.4f}** |
| **PR-AUC (Avg Precision)** | **{train_m['pr_auc']:.4f}** | **{val_m['pr_auc']:.4f}** | **{test_m['pr_auc']:.4f}** |
| **Accuracy (at 0.50)** | {train_m['accuracy']:.4f} | {val_m['accuracy']:.4f} | {test_m['accuracy']:.4f} |
| **Precision (at 0.50)** | {train_m['precision_at_0_50']:.4f} | {val_m['precision_at_0_50']:.4f} | {test_m['precision_at_0_50']:.4f} |
| **Recall (at 0.50)** | {train_m['recall_at_0_50']:.4f} | {val_m['recall_at_0_50']:.4f} | {test_m['recall_at_0_50']:.4f} |
| **F1 Score (at 0.50)** | {train_m['f1_at_0_50']:.4f} | {val_m['f1_at_0_50']:.4f} | {test_m['f1_at_0_50']:.4f} |
| **Precision (at High-Risk Cutoff {val_m['operational_threshold']:.2f})** | {train_m['precision_at_operational']:.4f} | {val_m['precision_at_operational']:.4f} | {test_m['precision_at_operational']:.4f} |
| **Recall (at High-Risk Cutoff {val_m['operational_threshold']:.2f})** | {train_m['recall_at_operational']:.4f} | {val_m['recall_at_operational']:.4f} | {test_m['recall_at_operational']:.4f} |

### Confusion Matrices (Test Split, N=1,200)
- **Standard Threshold (0.50)**:
  - True Negatives: `{test_m['confusion_matrix_at_0_50'][0][0]}` | False Positives: `{test_m['confusion_matrix_at_0_50'][0][1]}`
  - False Negatives: `{test_m['confusion_matrix_at_0_50'][1][0]}` | True Positives: `{test_m['confusion_matrix_at_0_50'][1][1]}`

- **Operational High-Risk Threshold ({test_m['operational_threshold']:.2f})**:
  - True Negatives: `{test_m['confusion_matrix_at_operational'][0][0]}` | False Positives: `{test_m['confusion_matrix_at_operational'][0][1]}`
  - False Negatives: `{test_m['confusion_matrix_at_operational'][1][0]}` | True Positives: `{test_m['confusion_matrix_at_operational'][1][1]}`

---

## 2. Integrity and Health Checks

- **Overfitting Gap (Train vs Validation ROC-AUC)**: `{gap:.4f}`
  - Verdict: {overfitting_verdict}
- **Suspiciously Easy Data Check (Test ROC-AUC > 0.95)**:
  - Verdict: {suspicious_verdict}
- **Early Stopping Status**:
  - Best Iteration: `{config.get('xgboost_config', {}).get('best_iteration', 'N/A')}` / `{config.get('xgboost_config', {}).get('n_estimators', 150)}`
  - Best Validation AUC: `{config.get('xgboost_config', {}).get('best_val_auc', 0.0):.4f}`

---

## 3. Operational Risk-Level Thresholds

- **LOW Risk**: `probability < {config['risk_level_thresholds']['low_max']:.2f}` (Standard checkout / trusted customer path)
- **MEDIUM Risk**: `{config['risk_level_thresholds']['low_max']:.2f} <= probability < {config['risk_level_thresholds']['high_min']:.2f}` (Ambiguous / thin history, triggers gentle sizing guide or deposit requirement)
- **HIGH Risk**: `probability >= {config['risk_level_thresholds']['high_min']:.2f}` (Elevated abuse risk, restrictive return policy or fee applied)

**Threshold Justification**:
> {config.get('threshold_justification', 'Evaluated against validation set probability distribution.')}

---

## 4. SHAP Global Feature Importance (Top 5 on Test Set)

| Rank | Feature | Mean Absolute SHAP Value |
| :---: | :--- | :---: |
{top5_rows}

Full feature rankings are saved in `ml/reports/feature_importance.csv`.
"""
    return summary_md


def evaluate_model() -> None:
    """Execute complete model evaluation and reporting workflow."""
    print("=" * 80)
    print("          RETURNSENTINEL AI - MODEL EVALUATION & EXPLAINABILITY")
    print("=" * 80)

    # 1. Load Model and Config
    print(f"\n[1/5] Loading model artifact and config...")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}. Run train_model.py first.")
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Model config not found at: {CONFIG_PATH}. Run train_model.py first.")

    model = joblib.load(MODEL_PATH)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 2. Re-create Stratified Splits
    print(f"\n[2/5] Reproducing stratified 70/15/15 splits from: {DATA_PATH}...")
    X, y = load_and_validate_dataset(DATA_PATH)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(X, y)

    # 3. Compute Predictions & Metrics
    print(f"\n[3/5] Computing predictions and classification metrics across all splits...")
    operational_threshold = config["risk_level_thresholds"]["high_min"]

    train_probs = model.predict_proba(X_train)[:, 1]
    val_probs = model.predict_proba(X_val)[:, 1]
    test_probs = model.predict_proba(X_test)[:, 1]

    train_metrics = compute_split_metrics(y_train, train_probs, operational_threshold)
    val_metrics = compute_split_metrics(y_val, val_probs, operational_threshold)
    test_metrics = compute_split_metrics(y_test, test_probs, operational_threshold)

    # Overfitting check
    gap = float(train_metrics["roc_auc"] - val_metrics["roc_auc"])
    overfitting_warning = gap > 0.08

    # Suspicious data check
    suspicious_warning = test_metrics["roc_auc"] > 0.95

    metrics_payload = {
        "train": train_metrics,
        "validation": val_metrics,
        "test": test_metrics,
        "overfitting_check": {
            "train_val_auc_gap": gap,
            "threshold_max": 0.08,
            "overfitting_warning": overfitting_warning,
        },
        "suspicious_data_check": {
            "test_roc_auc": test_metrics["roc_auc"],
            "threshold_max": 0.95,
            "suspiciously_easy_data_warning": suspicious_warning,
        },
    }

    # 4. SHAP Global Feature Importance
    print(f"\n[4/5] Computing SHAP TreeExplainer global feature importance on Test Set...")
    importance_df, _ = compute_shap_importance(model, X_test)

    # Save feature_importance.csv
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    importance_df.to_csv(FEATURE_IMPORTANCE_SAVE_PATH, index=False)
    print(f"  [OK] Saved feature importance rankings to: {FEATURE_IMPORTANCE_SAVE_PATH}")

    # Save model_metrics.json
    with open(METRICS_SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)
    print(f"  [OK] Saved detailed metrics to: {METRICS_SAVE_PATH}")

    # 5. Generate and Save evaluation_summary.md
    print(f"\n[5/5] Generating evaluation summary report...")
    summary_md = generate_evaluation_summary(metrics_payload, importance_df, config)
    with open(EVAL_SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"  [OK] Saved evaluation summary to: {EVAL_SUMMARY_PATH}")

    # Console display of results
    print("\n" + "=" * 80)
    print("                      EVALUATION RESULTS SUMMARY")
    print("=" * 80)
    print(f"Train ROC-AUC:      {train_metrics['roc_auc']:.4f} | PR-AUC: {train_metrics['pr_auc']:.4f}")
    print(f"Validation ROC-AUC: {val_metrics['roc_auc']:.4f} | PR-AUC: {val_metrics['pr_auc']:.4f}")
    print(f"Test ROC-AUC:       {test_metrics['roc_auc']:.4f} | PR-AUC: {test_metrics['pr_auc']:.4f}")
    print(f"Train-Val AUC Gap:  {gap:.4f} -> Overfitting Warning: {overfitting_warning}")
    print(f"Suspicious Performance Warning (>0.95): {suspicious_warning}")
    print("\nTop 5 SHAP Important Features (Test Set):")
    for i, r in importance_df.head(5).iterrows():
        print(f"  {i+1}. {r['feature']:32s}: {r['mean_abs_shap']:.4f}")
    print("=" * 80)


if __name__ == "__main__":
    evaluate_model()
