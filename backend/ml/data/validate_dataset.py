"""ReturnSentinel AI Dataset Validator (Phase 2A).

This module validates individual batch CSV files and the final combined
synthetic dataset against all business rules, mathematical constraints,
edge-case defaults, schema requirements, and statistical expectations.

Generates a comprehensive report saved to ml/reports/validation_report.txt
and printed to stdout.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BACKEND_DIR / "ml"
DATA_DIR = ML_DIR / "data"
BATCHES_DIR = DATA_DIR / "batches"
REPORTS_DIR = ML_DIR / "reports"
COMBINED_DATASET_PATH = DATA_DIR / "returnsentinel_synthetic_dataset.csv"
PROFILE_BUCKET_DEBUG_PATH = REPORTS_DIR / "profile_bucket_debug.csv"
VALIDATION_REPORT_PATH = REPORTS_DIR / "validation_report.txt"

# Expected Schema
EXPECTED_COLUMNS = [
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
    "return_abuse_label",
]

NUMERIC_COLUMNS = EXPECTED_COLUMNS  # all 13 are numeric/binary


class DatasetValidator:
    """Comprehensive validator for ReturnSentinel AI synthetic dataset."""

    def __init__(self) -> None:
        self.report_lines: List[str] = []
        self.overall_passed = True
        self.violation_counts: Dict[str, int] = {}

    def log(self, message: str = "") -> None:
        """Add a line to the validation report."""
        self.report_lines.append(message)

    def validate_schema(self, df: pd.DataFrame, file_name: str) -> bool:
        """Verify column count, names, and ordering."""
        columns = list(df.columns)
        if columns != EXPECTED_COLUMNS:
            self.log(f"  [FAIL] Schema mismatch in {file_name}:")
            self.log(f"    Expected: {EXPECTED_COLUMNS}")
            self.log(f"    Got:      {columns}")
            self.overall_passed = False
            return False
        self.log(f"  [PASS] Exact 13-column schema verified for {file_name}")
        return True

    def validate_nulls(self, df: pd.DataFrame, file_name: str) -> int:
        """Verify zero missing/null/NaN values across all columns."""
        null_count = int(df.isnull().sum().sum())
        if null_count > 0:
            self.log(f"  [FAIL] Missing values detected in {file_name}: {null_count} nulls found.")
            for col in df.columns:
                col_nulls = df[col].isnull().sum()
                if col_nulls > 0:
                    self.log(f"    - Column '{col}': {col_nulls} nulls")
            self.overall_passed = False
        else:
            self.log(f"  [PASS] Zero missing values in {file_name} (0 nulls / NaNs)")
        return null_count

    def check_duplicates(self, df: pd.DataFrame, file_name: str) -> int:
        """Check for exact duplicate rows and report count."""
        dup_count = int(df.duplicated().sum())
        self.log(f"  [INFO] Duplicate row check for {file_name}: {dup_count} duplicate rows ({dup_count / len(df):.2%})")
        return dup_count

    def validate_logical_rules(self, df: pd.DataFrame, file_name: str) -> Dict[str, int]:
        """Validate all mathematical constraints and logical relationships."""
        violations: Dict[str, int] = {}

        # 1. 0 <= customer_return_rate <= 1
        c1 = ((df["customer_return_rate"] < 0.0) | (df["customer_return_rate"] > 1.0)).sum()
        violations["0 <= customer_return_rate <= 1"] = int(c1)

        # 2. total_previous_returns <= total_previous_orders
        c2 = (df["total_previous_returns"] > df["total_previous_orders"]).sum()
        violations["total_previous_returns <= total_previous_orders"] = int(c2)

        # 3. customer_return_rate consistency with total_previous_returns / total_previous_orders (tolerance 1e-3)
        orders_gt_0 = df[df["total_previous_orders"] > 0]
        expected_rate = orders_gt_0["total_previous_returns"] / orders_gt_0["total_previous_orders"]
        c3 = (np.abs(orders_gt_0["customer_return_rate"] - expected_rate) > 0.001).sum()
        violations["customer_return_rate consistency (returns/orders)"] = int(c3)

        # 4. previous_returns_same_category <= total_previous_returns
        c4 = (df["previous_returns_same_category"] > df["total_previous_returns"]).sum()
        violations["previous_returns_same_category <= total_previous_returns"] = int(c4)

        # 5. multiple_sizes_same_product == 0 -> max_sizes_same_product == 1
        multi_0 = df[df["multiple_sizes_same_product"] == 0]
        c5 = (multi_0["max_sizes_same_product"] != 1).sum()
        violations["multiple_sizes == 0 -> max_sizes == 1"] = int(c5)

        # 6. multiple_sizes_same_product == 1 -> max_sizes_same_product >= 2
        multi_1 = df[df["multiple_sizes_same_product"] == 1]
        c6 = (multi_1["max_sizes_same_product"] < 2).sum()
        violations["multiple_sizes == 1 -> max_sizes >= 2"] = int(c6)

        # 7. max_sizes_same_product <= cart_item_count
        c7 = (df["max_sizes_same_product"] > df["cart_item_count"]).sum()
        violations["max_sizes_same_product <= cart_item_count"] = int(c7)

        # 8. days_since_last_order <= customer_history_days
        c8 = (df["days_since_last_order"] > df["customer_history_days"]).sum()
        violations["days_since_last_order <= customer_history_days"] = int(c8)

        # 9. cart_value > 0
        c9 = (df["cart_value"] <= 0).sum()
        violations["cart_value > 0"] = int(c9)

        # 10. cart_item_count >= 1
        c10 = (df["cart_item_count"] < 1).sum()
        violations["cart_item_count >= 1"] = int(c10)

        # 11. average_product_return_rate in [0, 1]
        c11 = ((df["average_product_return_rate"] < 0.0) | (df["average_product_return_rate"] > 1.0)).sum()
        violations["average_product_return_rate in [0, 1]"] = int(c11)

        # 12. No negative values in any numeric column
        c12 = 0
        for col in NUMERIC_COLUMNS:
            neg_count = (df[col] < 0).sum()
            c12 += int(neg_count)
        violations["no negative values in any column"] = c12

        # 13. Binary return_abuse_label in {0, 1}
        c13 = (~df["return_abuse_label"].isin([0, 1])).sum()
        violations["return_abuse_label is binary (0 or 1)"] = int(c13)

        # Log results
        has_viol = False
        for rule, count in violations.items():
            if count > 0:
                self.log(f"  [FAIL] Rule violation in {file_name}: '{rule}' ({count} rows violated)")
                self.overall_passed = False
                has_viol = True
            else:
                self.log(f"  [PASS] Rule '{rule}': 0 violations")

        return violations

    def validate_edge_case_defaults(self, df: pd.DataFrame, file_name: str) -> Dict[str, int]:
        """Verify the 3 documented edge-case defaults."""
        violations: Dict[str, int] = {}

        # Edge case 1 & 2: total_previous_orders == 0
        zero_orders = df[df["total_previous_orders"] == 0]
        zero_orders_count = len(zero_orders)

        if zero_orders_count > 0:
            # Default 1: customer_return_rate == 0.0
            d1_viol = (zero_orders["customer_return_rate"] != 0.0).sum()
            violations["edge_case: total_previous_orders == 0 -> customer_return_rate == 0.0"] = int(d1_viol)

            # Default 2: days_since_last_order == customer_history_days
            d2_viol = (zero_orders["days_since_last_order"] != zero_orders["customer_history_days"]).sum()
            violations["edge_case: total_previous_orders == 0 -> days_since_last_order == customer_history_days"] = int(d2_viol)
        else:
            violations["edge_case: total_previous_orders == 0 -> customer_return_rate == 0.0"] = 0
            violations["edge_case: total_previous_orders == 0 -> days_since_last_order == customer_history_days"] = 0

        # Edge case 3: total_previous_returns == 0 -> avg_days_to_return == 0.0
        zero_returns = df[df["total_previous_returns"] == 0]
        zero_returns_count = len(zero_returns)

        if zero_returns_count > 0:
            d3_viol = (zero_returns["avg_days_to_return"] != 0.0).sum()
            violations["edge_case: total_previous_returns == 0 -> avg_days_to_return == 0.0"] = int(d3_viol)
        else:
            violations["edge_case: total_previous_returns == 0 -> avg_days_to_return == 0.0"] = 0

        for rule, count in violations.items():
            if count > 0:
                self.log(f"  [FAIL] Edge-case default violation in {file_name}: '{rule}' ({count} rows violated)")
                self.overall_passed = False
            else:
                self.log(f"  [PASS] Edge-case default '{rule}': 0 violations")

        self.log(f"  [INFO] Edge-case frequency in {file_name}: {zero_orders_count} rows with 0 orders, {zero_returns_count} rows with 0 returns")
        return violations

    def compute_summary_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute comprehensive summary statistics for all columns."""
        stats = df.describe(percentiles=[0.25, 0.50, 0.75]).T
        stats = stats[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
        return stats

    def run_full_validation(self) -> bool:
        """Execute validation across all batches and the combined dataset."""
        self.report_lines.clear()
        self.overall_passed = True

        self.log("=" * 80)
        self.log("           RETURNSENTINEL AI - DATASET VALIDATION REPORT (PHASE 2A)")
        self.log("=" * 80)
        self.log()

        # 1. Validate Batch Files
        self.log("SECTION 1: BATCH-LEVEL VALIDATIONS (8 Batches x 1,000 Rows)")
        self.log("-" * 80)

        batch_dfs: List[pd.DataFrame] = []
        for b_idx in range(1, 9):
            batch_name = f"batch_{b_idx:02d}.csv"
            batch_path = BATCHES_DIR / batch_name

            if not batch_path.exists():
                self.log(f"[FAIL] Batch file not found: {batch_path}")
                self.overall_passed = False
                continue

            b_df = pd.read_csv(batch_path)
            batch_dfs.append(b_df)

            self.log(f"\n--- Validating {batch_name} ({len(b_df)} rows) ---")
            if len(b_df) != 1000:
                self.log(f"  [FAIL] Batch row count expected 1000, got {len(b_df)}")
                self.overall_passed = False
            else:
                self.log(f"  [PASS] Row count: {len(b_df)} rows")

            self.validate_schema(b_df, batch_name)
            self.validate_nulls(b_df, batch_name)
            self.check_duplicates(b_df, batch_name)
            self.validate_logical_rules(b_df, batch_name)
            self.validate_edge_case_defaults(b_df, batch_name)

            b_pos = int(b_df["return_abuse_label"].sum())
            self.log(f"  [INFO] Positive label rate: {b_pos / len(b_df):.2%} ({b_pos}/{len(b_df)})")

        # 2. Validate Combined Dataset
        self.log("\n" + "=" * 80)
        self.log("SECTION 2: COMBINED DATASET VALIDATION (returnsentinel_synthetic_dataset.csv)")
        self.log("-" * 80)

        if not COMBINED_DATASET_PATH.exists():
            self.log(f"[FAIL] Combined dataset file not found: {COMBINED_DATASET_PATH}")
            self.overall_passed = False
            self.save_and_print_report()
            return False

        combined_df = pd.read_csv(COMBINED_DATASET_PATH)
        self.log(f"\nTotal Rows: {len(combined_df)}")
        self.log(f"Total Columns: {len(combined_df.columns)}")

        if len(combined_df) != 8000:
            self.log(f"  [FAIL] Combined row count expected 8000, got {len(combined_df)}")
            self.overall_passed = False
        else:
            self.log(f"  [PASS] Combined row count: {len(combined_df)} rows")

        self.validate_schema(combined_df, "Combined Dataset")
        self.validate_nulls(combined_df, "Combined Dataset")
        self.check_duplicates(combined_df, "Combined Dataset")
        self.validate_logical_rules(combined_df, "Combined Dataset")
        self.validate_edge_case_defaults(combined_df, "Combined Dataset")

        # 3. Summary Statistics
        self.log("\n" + "=" * 80)
        self.log("SECTION 3: SUMMARY STATISTICS (COMBINED DATASET)")
        self.log("-" * 80)
        stats_df = self.compute_summary_statistics(combined_df)
        self.log(stats_df.to_string())

        # 4. Label Distribution Analysis
        self.log("\n" + "=" * 80)
        self.log("SECTION 4: LABEL DISTRIBUTION ANALYSIS")
        self.log("-" * 80)

        overall_pos = int(combined_df["return_abuse_label"].sum())
        overall_rate = overall_pos / len(combined_df)
        self.log(f"Overall return_abuse_label positive rate: {overall_rate:.2%} ({overall_pos}/{len(combined_df)})")
        self.log(f"Target overall range: 28.00% - 37.00% (ideal: 30.00% - 35.00%)")
        if 0.28 <= overall_rate <= 0.37:
            self.log(f"  [PASS] Overall positive rate meets target calibration criteria.")
        else:
            self.log(f"  [WARN/FAIL] Overall positive rate {overall_rate:.2%} is outside target range [28%, 37%]")
            self.overall_passed = False

        # Profile bucket breakdown if debug tracking file exists
        if PROFILE_BUCKET_DEBUG_PATH.exists():
            debug_df = pd.read_csv(PROFILE_BUCKET_DEBUG_PATH)
            self.log("\nLabel Breakdown by Behavioral Profile Bucket:")
            self.log("-" * 60)

            debug_df["profile_group"] = debug_df["profile_bucket"].apply(
                lambda x: "ambiguous" if x.startswith("ambiguous") else x
            )

            # High-level group rates
            group_targets = {
                "low_risk": "~10% (expected 7%-15%)",
                "ambiguous": "~40% (expected 32%-48%)",
                "elevated_risk": "~60% (expected 52%-68%)",
            }

            for grp, grp_df in debug_df.groupby("profile_group"):
                grp_pos = int(grp_df["return_abuse_label"].sum())
                grp_rate = grp_pos / len(grp_df)
                tgt = group_targets.get(grp, "N/A")
                self.log(f"  - {grp:15s}: {grp_rate:6.2%} ({grp_pos:4d}/{len(grp_df):4d}) | Target: {tgt}")

            # Sub-population breakdown
            self.log("\nSub-Population Breakdown (Ambiguous Profile):")
            for sub_grp in ["ambiguous_established", "ambiguous_thin_history"]:
                sub_df = debug_df[debug_df["profile_bucket"] == sub_grp]
                if len(sub_df) > 0:
                    s_pos = int(sub_df["return_abuse_label"].sum())
                    s_rate = s_pos / len(sub_df)
                    self.log(f"    * {sub_grp:25s}: {s_rate:6.2%} ({s_pos:4d}/{len(sub_df):4d})")

        # 5. Overlap & Feature Overlap Verification
        self.log("\n" + "=" * 80)
        self.log("SECTION 5: PROFILE OVERLAP ANALYSIS")
        self.log("-" * 80)
        self.log("Verifying continuous distributions and absence of hard-clipped boundaries:")
        if PROFILE_BUCKET_DEBUG_PATH.exists():
            debug_df = pd.read_csv(PROFILE_BUCKET_DEBUG_PATH)
            merged = combined_df.copy()
            merged["profile_bucket"] = debug_df["profile_bucket"]

            for col in ["customer_return_rate", "cart_value", "avg_days_to_return"]:
                self.log(f"\nDistribution Overlap for '{col}':")
                for p_grp in ["low_risk", "ambiguous_established", "ambiguous_thin_history", "elevated_risk"]:
                    sub = merged[merged["profile_bucket"] == p_grp][col]
                    self.log(f"  - {p_grp:25s}: min={sub.min():.2f}, mean={sub.mean():.2f}, max={sub.max():.2f}")

        # 6. Final Status
        self.log("\n" + "=" * 80)
        self.log("SECTION 6: FINAL PASS / FAIL SUMMARY")
        self.log("-" * 80)
        if self.overall_passed:
            self.log(">>> OVERALL VALIDATION STATUS: PASSED <<<")
            self.log("All schema, missing value, relational logic, edge cases, and calibration targets PASSED.")
        else:
            self.log(">>> OVERALL VALIDATION STATUS: FAILED <<<")
            self.log("One or more validation checks failed. See details above.")
        self.log("=" * 80)

        self.save_and_print_report()
        return self.overall_passed

    def save_and_print_report(self) -> None:
        """Write report to file and print to stdout."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_text = "\n".join(self.report_lines)
        with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(report_text)


def validate() -> bool:
    """Run validation standalone."""
    validator = DatasetValidator()
    success = validator.run_full_validation()
    return success


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
