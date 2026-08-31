"""Diagnostic Script: Confidence Threshold Recalibration Analysis.

Computes distribution statistics across the Phase 2B validation set, evaluates
tail asymmetry, assesses candidate thresholds, and tests the 7 operational scenarios.
"""

from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = BACKEND_DIR / "ml" / "data" / "returnsentinel_synthetic_dataset.csv"
MODEL_PATH = BACKEND_DIR / "ml" / "models" / "return_risk_xgboost.joblib"


def run_analysis():
    df = pd.read_csv(DATA_PATH)
    FEATURE_COLUMNS = [c for c in df.columns if c != "return_abuse_label"]
    X = df[FEATURE_COLUMNS]
    y = df["return_abuse_label"]

    # Identical stratified split (random_state=42, 70/15/15)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    model = joblib.load(MODEL_PATH)
    val_probs = model.predict_proba(X_val)[:, 1]
    val_conf = 2.0 * np.abs(val_probs - 0.5)

    low_mask = val_probs < 0.5
    high_mask = val_probs >= 0.5

    low_tier_mask = val_probs < 0.30        # N=735
    med_tier_mask = (val_probs >= 0.30) & (val_probs < 0.65)  # N=281
    high_tier_mask = val_probs >= 0.65      # N=184

    def get_stats(arr: np.ndarray) -> dict:
        return {
            "count": len(arr),
            "min": float(np.min(arr)),
            "p10": float(np.percentile(arr, 10)),
            "p25": float(np.percentile(arr, 25)),
            "median": float(np.percentile(arr, 50)),
            "mean": float(np.mean(arr)),
            "p75": float(np.percentile(arr, 75)),
            "p90": float(np.percentile(arr, 90)),
            "max": float(np.max(arr)),
        }

    print("=" * 90)
    print("1. VALIDATION SET DISTRIBUTION STATISTICS (N=1200)")
    print("=" * 90)
    print(f"Overall Probabilities : min={np.min(val_probs):.4f}, max={np.max(val_probs):.4f}, mean={np.mean(val_probs):.4f}")
    print(f"Overall Confidence    : min={np.min(val_conf):.4f}, max={np.max(val_conf):.4f}, mean={np.mean(val_conf):.4f}")

    print("\n--- Low Tail (prob < 0.5, N=895 / 74.6%) ---")
    print(f"Prob range: [{np.min(val_probs[low_mask]):.4f}, {np.max(val_probs[low_mask]):.4f}]")
    for k, v in get_stats(val_conf[low_mask]).items():
        print(f"  {k:<10}: {v:.4f}" if isinstance(v, float) else f"  {k:<10}: {v}")

    print("\n--- High Tail (prob >= 0.5, N=305 / 25.4%) ---")
    print(f"Prob range: [{np.min(val_probs[high_mask]):.4f}, {np.max(val_probs[high_mask]):.4f}]")
    for k, v in get_stats(val_conf[high_mask]).items():
        print(f"  {k:<10}: {v:.4f}" if isinstance(v, float) else f"  {k:<10}: {v}")

    DEBUG_PATH = BACKEND_DIR / "ml" / "reports" / "profile_bucket_debug.csv"
    if DEBUG_PATH.exists():
        debug_df = pd.read_csv(DEBUG_PATH)
        val_profiles = debug_df.iloc[X_val.index]["profile_bucket"]

        print("\n" + "=" * 90)
        print("--- DISTRIBUTION BY SYNTHETIC PROFILE BUCKET (N=1200) ---")
        print("=" * 90)
        df_val_summary = pd.DataFrame({
            "profile": val_profiles,
            "prob": val_probs,
            "conf": val_conf,
        })
        for prof, grp in df_val_summary.groupby("profile"):
            print(f"\nProfile: {prof} (N={len(grp)})")
            print(f"  Prob : mean={grp['prob'].mean():.4f}, min={grp['prob'].min():.4f}, max={grp['prob'].max():.4f}")
            print(f"  Conf : mean={grp['conf'].mean():.4f}, min={grp['conf'].min():.4f}, max={grp['conf'].max():.4f}")
            print(f"  Conf >= 0.60: {(grp['conf'] >= 0.60).mean():.1%} ({int((grp['conf'] >= 0.60).sum())}/{len(grp)})")
            print(f"  Conf >= 0.45: {(grp['conf'] >= 0.45).mean():.1%} ({int((grp['conf'] >= 0.45).sum())}/{len(grp)})")
            print(f"  Conf >= 0.40: {(grp['conf'] >= 0.40).mean():.1%} ({int((grp['conf'] >= 0.40).sum())}/{len(grp)})")
            print(f"  Conf >= 0.35: {(grp['conf'] >= 0.35).mean():.1%} ({int((grp['conf'] >= 0.35).sum())}/{len(grp)})")


    # 3 Candidate Thresholds: Baseline 0.60, Candidate A 0.45, Candidate B 0.40, Candidate C 0.35
    candidates = [0.60, 0.45, 0.40, 0.35]

    print("\n" + "=" * 90)
    print("2. CANDIDATE THRESHOLD TRADEOFF ANALYSIS ON VALIDATION SET")
    print("=" * 90)
    print(f"{'Threshold':<12} | {'Total R0 Pass':<16} | {'Total Investigate':<18} | {'High-Tier (>=0.65) Reachable':<28} | {'Low-Tier (<0.30) Pass'}")
    print("-" * 90)
    for t in candidates:
        tot_pass = (val_conf >= t).mean()
        tot_inv = 1.0 - tot_pass
        high_pass = (val_conf[high_tier_mask] >= t).mean()
        low_pass = (val_conf[low_tier_mask] >= t).mean()
        print(f"{t:<12.2f} | {tot_pass*100:5.1f}% ({int(tot_pass*1200):4d}/1200) | {tot_inv*100:5.1f}% ({int(tot_inv*1200):4d}/1200) | {high_pass*100:5.1f}% ({int(high_pass*184):3d}/184)           | {low_pass*100:5.1f}% ({int(low_pass*735):3d}/735)")

    # 7 Scenarios Simulation
    scenarios = [
        {"id": "Scenario 1", "name": "Customer A (Low Risk)", "r0_p": 0.1745, "r0_c": 0.6510, "r1_c": 0.6510},
        {"id": "Scenario 2", "name": "Customer B (High Risk)", "r0_p": 0.5258, "r0_c": 0.0515, "r1_c": 0.3127},
        {"id": "Scenario 3", "name": "Customer C (Uncertain/New)", "r0_p": 0.2640, "r0_c": 0.4721, "r1_c": 0.4091},
        {"id": "Scenario 4", "name": "Customer D (Borderline Low)", "r0_p": 0.1785, "r0_c": 0.6431, "r1_c": 0.6431},
        {"id": "Scenario 5", "name": "Customer E (Strong High Risk)", "r0_p": 0.5620, "r0_c": 0.1240, "r1_c": 0.4688},
        {"id": "Scenario 6", "name": "Customer F (Clean Repeat)", "r0_p": 0.2317, "r0_c": 0.5367, "r1_c": 0.6199},
        {"id": "Scenario 7", "name": "Test Case 2 Repro (High Risk)", "r0_p": 0.7391, "r0_c": 0.4781, "r1_c": 0.3127},
    ]

    print("\n" + "=" * 90)
    print("3. 7 DEMO SCENARIOS BEHAVIOR UNDER CANDIDATE THRESHOLDS")
    print("=" * 90)
    for t in candidates:
        print(f"\n--- Evaluation Under CONFIDENCE_THRESHOLD = {t:.2f} ---")
        for sc in scenarios:
            r0 = sc["r0_c"]
            r1 = sc["r1_c"]
            if r0 >= t:
                status = f"Round 0 Exit (R0 Conf: {r0:.4f} >= {t:.2f})"
            elif r1 >= t:
                status = f"Round 1 Resolution (R0 Conf: {r0:.4f} < {t:.2f} -> R1 Conf: {r1:.4f} >= {t:.2f})"
            else:
                status = f"Exhausted to Low-Confidence (Final Conf: {r1:.4f} < {t:.2f})"
            print(f"  {sc['id']:<11} | {sc['name']:<28} | {status}")


if __name__ == "__main__":
    run_analysis()
