# ReturnSentinel AI — Phase 3A: Confidence Threshold Recalibration Analysis Report
**Status**: Read-Only Diagnostic & Calibration Report (No Threshold or Code Changes Applied)  
**Dataset**: Phase 2B Validation Set ($N = 1,200$ rows, stratified 70/15/15 split, `random_state=42`)  
**Model**: `return_risk_xgboost.joblib` (17 trees, `learning_rate=0.08`, `best_val_auc=0.8305`)  
**Formula Under Evaluation**: `model_confidence = 2 * abs(risk_probability - 0.5)`  

---

## 1. Executive Summary & Core Finding

Prior diagnostic testing revealed that high-risk orders (e.g. Customer B, Customer E, Test Case 2) consistently exhausted their 2-round investigation budget and finished with `is_low_confidence = True`.

This empirical validation analysis confirms that **this is a structural asymmetry in the model confidence distribution**:
1. **Low Tail ($p < 0.5$)**: Probabilities drop as low as **`0.1367`**, yielding confidence scores up to **`0.7266`**. Over **83.8%** of clean low-risk customers easily cross the `0.60` threshold.
2. **High Tail ($p \ge 0.5$)**: Probabilities peak at **`0.7631`** on the validation set (and $\sim 0.7391$ on extreme synthetic feature space), capping maximum confidence at **`0.5262`**.
3. **The 0.60 Threshold Ceiling**: Because $2 \times |p - 0.5| \ge 0.60$ requires either $p \le 0.20$ or $p \ge 0.80$, and the model ceiling is $0.7631 < 0.80$, **exactly 0.0% (0 / 184) of HIGH-risk tier orders can EVER meet the current `0.60` confidence threshold.**

Under `CONFIDENCE_THRESHOLD = 0.60`, **every single elevated-risk customer is mathematically guaranteed to fail confidence checks and exhaust investigation rounds**, regardless of how much evidence is gathered.

---

## 2. Validation Set Distribution Statistics ($N = 1,200$)

The Phase 2B validation set was partitioned using the exact stratified split logic from `train_model.py` (`random_state=42`, $N=1,200$). Direct inference was run via `model.predict_proba()`:

### A. Overall & Tail Breakdown

| Metric | Full Validation Set ($N=1,200$) | Low-Leaning Tail ($p < 0.5$, $N=895$, 74.6%) | High-Leaning Tail ($p \ge 0.5$, $N=305$, 25.4%) | High-Risk Tier ($p \ge 0.65$, $N=184$, 15.3%) |
| :--- | :---: | :---: | :---: | :---: |
| **Probability Min** | `0.1367` | `0.1367` | `0.5001` | `0.6513` |
| **Probability Max** | `0.7631` | `0.4999` | `0.7631` | `0.7631` |
| **Probability Mean**| `0.3371` | `0.2272` | `0.6599` | `0.7233` |
| **Confidence Min** | `0.0001` | `0.0002` | `0.0001` | `0.3026` |
| **10th Percentile (P10)** | `0.1182` | `0.1792` | `0.0431` | `0.3284` |
| **25th Percentile (P25)** | `0.3628` | `0.4928` | `0.1425` | `0.3880` |
| **Median (P50)** | `0.5649` | `0.6239` | `0.3456` | `0.4711` |
| **Mean Confidence** | `0.4879` | `0.5455` | `0.3187` | `0.4466` |
| **75th Percentile (P75)** | `0.6510` | `0.6802` | `0.4895` | `0.5048` |
| **90th Percentile (P90)** | `0.7028` | `0.7086` | `0.5183` | `0.5262` |
| **Confidence Max** | `0.7266` | **`0.7266`** | **`0.5262`** | **`0.5262`** |

### B. Distribution by Synthetic Behavioral Profile Bucket

| Profile Bucket | Sample Count | Mean Probability | Mean Confidence | $\% \ge 0.60$ | $\% \ge 0.45$ | $\% \ge 0.40$ | $\% \ge 0.35$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Low-Risk Profile** | 556 | `0.1763` | `0.6474` | **83.8%** | 98.2% | 98.9% | 99.3% |
| **Ambiguous (Established)** | 125 | `0.2642` | `0.4789` | **29.6%** | 66.4% | 75.2% | 80.0% |
| **Ambiguous (Thin History)**| 130 | `0.2889` | `0.4342` | **0.8%** | 55.4% | 62.3% | 71.5% |
| **Elevated-Risk Profile** | 389 | `0.6063` | `0.2808` | **0.0%** | 30.1% | 37.0% | 41.4% |

---

## 3. Mathematical Proof of Tail Asymmetry

Why does the asymmetry exist?
1. **Prevalence & Tree Depth**: The synthetic dataset has $\sim 32.6\%$ positive labels. During XGBoost training, early stopping halted at iteration 17 to prevent overfitting. As a result, the ensemble sigmoid output naturally compresses high probabilities into $[0.65, 0.76]$, while low probabilities extend down to $0.13$.
2. **Confidence Margin Disparity**:
   - Distance from $0.50$ decision boundary to lower floor: $|0.1367 - 0.50| = 0.3633 \implies \text{Confidence} = 2 \times 0.3633 = \mathbf{0.7266}$.
   - Distance from $0.50$ decision boundary to upper ceiling: $|0.7631 - 0.50| = 0.2631 \implies \text{Confidence} = 2 \times 0.2631 = \mathbf{0.5262}$.
3. **Threshold Reachability**:
   - A threshold of $0.60$ requires a distance $\ge 0.30$ ($p \le 0.20$ or $p \ge 0.80$).
   - The lower tail exceeds this ($0.1367 \le 0.20$).
   - The upper tail **never reaches $0.80$** ($0.7631 < 0.80$).

---

## 4. Candidate Threshold Tradeoff Analysis

We evaluate 3 data-driven candidate thresholds against the baseline $0.60$:

### A. Tradeoff Table Across Validation Set ($N = 1,200$)

| Threshold Candidate | Rationale & Focus | Total Round 0 Pass Rate | Total Requiring Investigation | High-Risk Tier ($p \ge 0.65$, $N=184$) Reachable | Medium-Risk Ambiguous ($0.30 \le p < 0.65$, $N=281$) Pass Rate | Low-Risk Tier ($p < 0.30$, $N=735$) Pass Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline: `0.60`** | Current configuration | 42.0% (504/1200) | 58.0% (696/1200) | **0.0% (0/184)** *(Unreachable)* | **0.0% (0/281)** | 68.6% (504/735) |
| **Candidate 1: `0.45`** | *Conservative High-Tier Calibration* (Sits below High-Tier Median 0.4711) | 68.2% (818/1200) | 31.8% (382/1200) | **60.3% (111/184)** | **0.0% (0/281)** | 96.2% (707/735) |
| **Candidate 2: `0.40`** | *Optimal Balanced Calibration* (Encompasses 72.8% of High Tier, 0% Medium leakage) | 72.4% (869/1200) | 27.6% (331/1200) | **72.8% (134/184)** | **0.0% (0/281)** | 100.0% (735/735) |
| **Candidate 3: `0.35`** | *Permissive Calibration* (Encompasses 82.1% of High Tier, allows 7.1% Medium pass) | 75.5% (906/1200) | 24.5% (294/1200) | **82.1% (151/184)** | **7.1% (20/281)** | 100.0% (735/735) |

---

## 5. Behavior on the 7 Operational Demo Scenarios

We evaluated the exact confidence values recorded from the 7 demo scenarios under each candidate threshold:

| Scenario | Customer / Profile | Round 0 Conf | Post-Investigation Conf | Under `0.60` (Current) | Under `0.45` (Candidate 1) | Under `0.40` (Candidate 2) | Under `0.35` (Candidate 3) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario 1** | **Customer A** (Low Risk) | `0.6510` | `0.6510` | Round 0 Exit | Round 0 Exit | Round 0 Exit | Round 0 Exit |
| **Scenario 2** | **Customer B** (High Risk) | `0.0515` | `0.3127` | Exhausted (LowConf) | Exhausted (LowConf) | Exhausted (LowConf) | Exhausted (LowConf) |
| **Scenario 3** | **Customer C** (Uncertain / New) | `0.4721` | `0.4091` | Exhausted (LowConf) | Round 0 Exit | Round 0 Exit | Round 0 Exit |
| **Scenario 4** | **Customer D** (Borderline Low) | `0.6431` | `0.6431` | Round 0 Exit | Round 0 Exit | Round 0 Exit | Round 0 Exit |
| **Scenario 5** | **Customer E** (Strong High Risk) | `0.1240` | `0.4688` | Exhausted (LowConf) | **Round 1 Resolution** | **Round 1 Resolution** | **Round 1 Resolution** |
| **Scenario 6** | **Customer F** (Clean Repeat) | `0.5367` | `0.6199` | Round 1 Resolution | Round 0 Exit | Round 0 Exit | Round 0 Exit |
| **Scenario 7** | **Test Case 2 Repro** | `0.4781` | `0.3127` | Exhausted (LowConf) | Round 0 Exit | Round 0 Exit | Round 0 Exit |

### Key Scenario Observations:
1. **Customer E (High Risk, Strong Signal)**:
   - Under `0.60`, Customer E fails and exhausts.
   - Under `0.45` or `0.40`, Customer E enters Round 1 with low cached confidence (`0.1240`), gathers live transactional data (24 returns, 2.0d turnaround), reaches `confidence = 0.4688`, and **successfully resolves in Round 1 without exhausting to low-confidence**!
2. **Customer B (High Risk with Mixed Features)**:
   - Reaches post-investigation confidence `0.3127`. Under all candidates $\ge 0.35$, Customer B continues to correctly exhaust to `is_low_confidence = True`, preserving investigation safeguards on ambiguous high-risk profiles.

---

## 6. Recommendation

### **Recommended Candidate: `CONFIDENCE_THRESHOLD = 0.45` (Candidate 1)**

#### Rationale:
1. **Fixes the High-Risk Structural Blindspot**:
   - At `0.45`, **60.3%** of genuine high-risk orders ($p \ge 0.725$) are reachable and can resolve cleanly when strong evidence is present (as seen in Customer E resolving at Round 1 with `0.4688`).
2. **Zero Ambiguity Leakage**:
   - **0.0% (0 / 281)** of the Medium-risk ambiguous tier ($0.30 \le p < 0.65$) can pass at Round 0. 100% of genuinely ambiguous orders remain routed into the investigation loop.
3. **Preserves Investigation Trigger on Low-Confidence High-Risk Cases**:
   - Orders with marginal or ambiguous high-risk signals (like Customer B at `0.3127`) still fail the threshold and exhaust to `is_low_confidence = True`.
4. **Conservative & Defensible**:
   - `0.45` sits just below the high-risk tier median (`0.4711`), ensuring that only above-average strong high-risk signals bypass low-confidence tagging.

*(Note: In accordance with task boundaries, no code or constant changes have been applied. This analysis is submitted for review and approval.)*
