# ReturnSentinel AI — XGBoost Risk Model Evaluation Summary (Phase 2B)

## Executive Summary
This report summarizes the performance and explainability of the ReturnSentinel AI pre-payment return-abuse XGBoost classification model trained on the Phase 2A synthetic dataset (8,000 orders).

---

## 1. Train / Validation / Test Performance Comparison

| Metric | Train Split (70% / 5,600 rows) | Validation Split (15% / 1,200 rows) | Test Split (15% / 1,200 rows) |
| :--- | :---: | :---: | :---: |
| **ROC-AUC** | **0.8367** | **0.8305** | **0.8466** |
| **PR-AUC (Avg Precision)** | **0.7439** | **0.7217** | **0.7492** |
| **Accuracy (at 0.50)** | 0.8032 | 0.8158 | 0.7942 |
| **Precision (at 0.50)** | 0.7779 | 0.7803 | 0.7562 |
| **Recall (at 0.50)** | 0.5568 | 0.6071 | 0.5459 |
| **F1 Score (at 0.50)** | 0.6490 | 0.6829 | 0.6341 |
| **Precision (at High-Risk Cutoff 0.65)** | 0.8670 | 0.8478 | 0.8779 |
| **Recall (at High-Risk Cutoff 0.65)** | 0.3350 | 0.3980 | 0.3852 |

### Confusion Matrices (Test Split, N=1,200)
- **Standard Threshold (0.50)**:
  - True Negatives: `739` | False Positives: `69`
  - False Negatives: `178` | True Positives: `214`

- **Operational High-Risk Threshold (0.65)**:
  - True Negatives: `787` | False Positives: `21`
  - False Negatives: `241` | True Positives: `151`

---

## 2. Integrity and Health Checks

- **Overfitting Gap (Train vs Validation ROC-AUC)**: `0.0062`
  - Verdict: **PASSED**: Train-Val ROC-AUC gap is 0.0062 (<= 0.08 threshold). Generalization is strong.
- **Suspiciously Easy Data Check (Test ROC-AUC > 0.95)**:
  - Verdict: **PASSED**: Test ROC-AUC is 0.8466 (<= 0.95). Data shows realistic behavioral overlap.
- **Early Stopping Status**:
  - Best Iteration: `17` / `150`
  - Best Validation AUC: `0.8305`

---

## 3. Operational Risk-Level Thresholds

- **LOW Risk**: `probability < 0.30` (Standard checkout / trusted customer path)
- **MEDIUM Risk**: `0.30 <= probability < 0.65` (Ambiguous / thin history, triggers gentle sizing guide or deposit requirement)
- **HIGH Risk**: `probability >= 0.65` (Elevated abuse risk, restrictive return policy or fee applied)

**Threshold Justification**:
> Provisional thresholds [low < 0.30, medium 0.30-0.65, high >= 0.65] confirmed on validation set: Low=735 (61.3%), Med=281 (23.4%), High=184 (15.3%) with High-tier Precision=84.8%, Recall=39.8%.

---

## 4. SHAP Global Feature Importance (Top 5 on Test Set)

| Rank | Feature | Mean Absolute SHAP Value |
| :---: | :--- | :---: |
| 1 | `customer_return_rate` | 0.3253 |
| 2 | `previous_returns_same_category` | 0.2711 |
| 3 | `multiple_sizes_same_product` | 0.2485 |
| 4 | `average_product_return_rate` | 0.1649 |
| 5 | `avg_days_to_return` | 0.1420 |

Full feature rankings are saved in `ml/reports/feature_importance.csv`.
