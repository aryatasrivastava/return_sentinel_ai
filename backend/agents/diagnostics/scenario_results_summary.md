# ReturnSentinel AI — Phase 3A: 7-Scenario Confidence Router Validation Summary

This document summarizes the final execution results of the **Phase 3A LangGraph Confidence Router & Investigation Loop** under the recalibrated threshold `CONFIDENCE_THRESHOLD = 0.40` with the **Mandatory HIGH-Risk Verification Safeguard** active.

---

## 1. 7-Scenario Validation Summary Table

| Scenario | Customer / Profile Description | Round 0 (Prob / Conf) | Final (Prob / Conf) | Rounds | LowConf | Risk Level | Final Routing Flow |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Scenario 1** | **Customer A** (Low Risk) | `0.1745 / 0.6510` | `0.1745 / 0.6510` | **0** | `False` | **LOW** | **Clean Exit (Round 0)**: Confidence $\ge 0.40$ from cache. |
| **Scenario 2** | **Customer B** (High Risk) | `0.5258 / 0.0515` | `0.6564 / 0.3127` | **2** | `True` | **HIGH** | **Exhausted (Round 2)**: Live audit detected 15 category returns; confidence caps at 0.3127, flags low-confidence. |
| **Scenario 3** | **Customer C** (Uncertain/New) | `0.2640 / 0.4721` | `0.2640 / 0.4721` | **0** | `False` | **LOW** | **Clean Exit (Round 0)**: Low risk confidence ($0.4721 \ge 0.40$) resolves immediately. |
| **Scenario 4** | **Customer D** (Borderline Low) | `0.1785 / 0.6431` | `0.1785 / 0.6431` | **0** | `False` | **LOW** | **Clean Exit (Round 0)**: Moderate history achieves high confidence ($0.6431 \ge 0.40$). |
| **Scenario 5** | **Customer E** (Strong High Risk) | `0.5620 / 0.1240` | `0.7344 / 0.4688` | **1** | `False` | **HIGH** | **Live Resolution (Round 1)**: Live table audit confirms 24/28 returns (85.7%); confidence lifts to $0.4688 \ge 0.40$ and resolves cleanly! |
| **Scenario 6** | **Customer F** (Clean Repeat) | `0.2317 / 0.5367` | `0.2317 / 0.5367` | **0** | `False` | **LOW** | **Clean Exit (Round 0)**: 35 orders, 5.7% return rate resolves at Round 0 ($0.5367 \ge 0.40$). |
| **Scenario 7** | **Test Case 2 Repro** | `0.7391 / 0.4781` | `0.6564 / 0.3127` | **2** | `True` | **HIGH** | **Safeguard Interception**: Round 0 cached HIGH risk forced into mandatory verification. Live tables revealed true confidence is 0.3127, correctly exhausting with `is_low_confidence = True`. |

---

## 2. Safeguard Verification Analysis

```python
# Mandatory HIGH-Risk Verification Safeguard in router.py
if investigation_round == 0 and risk_level == "HIGH" and model_confidence >= CONFIDENCE_THRESHOLD:
    return "investigate"
```

1. **Mandatory Live Verification for HIGH-Risk Orders**:
   - In Scenario 7 (Test Case 2 reproduction), the injected Round 0 prediction had `risk_level == "HIGH"` and `model_confidence: 0.4781 >= 0.40`.
   - Instead of prematurely exiting at Round 0 on cached data alone, the safeguard **intercepted the order and forced a mandatory live verification round**.
   - Live database recomputation updated the feature vector, revealing a true confidence of `0.3127 < 0.40`, which consumed the round budget and correctly **exhausted to `is_low_confidence = True`**.
2. **Zero Interference with LOW/MEDIUM Decisions**:
   - Scenarios 1, 3, 4, and 6 (all `LOW` risk) exited at Round 0 without being routed into unnecessary investigation rounds.
