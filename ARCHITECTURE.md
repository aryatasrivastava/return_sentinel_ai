# ReturnSentinel AI — Architecture Documentation

**Track:** AI Risk Manager (Razorpay AI Buildathon 2026)
**One-line summary:** A return-risk scorer that predicts elevated return-abuse risk on an order before checkout and dynamically applies a merchant-approved return policy — defense-only, explainable, and bounded to what the merchant has approved.

---

## 1. The Problem

Retailers lost $103B to fraudulent and abusive returns in 2024, up from $101B in 2023. Wardrobing and size-bracketing are the tactics cited most often — but bracketing (ordering multiple sizes of the same item) is frequently *legitimate* shopping behavior, since sizing is inconsistent across brands. Existing tools mostly do one of two things: block suspicious orders outright, or tighten return policy for every customer. Both punish legitimate shoppers along with abusive ones.

ReturnSentinel AI scores return-abuse risk **per order**, before payment, and responds with a **graduated, non-blocking** policy adjustment (Standard Return → Exchange First → Store Credit → Restocking Fee) instead of a binary allow/deny — protecting merchant margin while minimizing friction for the customers who don't deserve it.

---

## 2. Architecture Overview

```
CUSTOMER SIDE (demo storefront)         MERCHANT SIDE (dashboard)
        |                                        |
   Add to Cart                          Orders / Risk Analysis /
        |                                Policies / Analytics
        v                                        ^
   Checkout ---> POST /api/assess-order ---------|
                        |
                        v
        +---------------------------------------------+
        |        ReturnSentinel AI Pipeline            |
        |      (FastAPI + LangGraph, Python)           |
        +-----------------------------------------------+
        | 1. Feature Builder                            |
        |    - Round 0: cached customer/product signals |
        |    - Round 1-2: live DB query (bypasses cache)|
        | 2. XGBoost Risk Model                         |
        |    -> risk_probability, risk_level,           |
        |       model_confidence, SHAP top factors      |
        | 3. Confidence Router (LangGraph)              |
        |    - confidence >= 0.40 -> proceed            |
        |    - else -> investigate (max 2 rounds)       |
        |    - HIGH-risk always gets 1 mandatory        |
        |      live-data verification round             |
        |    - exhausted -> is_low_confidence=True       |
        | 4. Policy Agent (deterministic, NOT an LLM)   |
        |    - categorizes SHAP factors: Bracketing /   |
        |      Repeat-Behavior / Product-Driven          |
        |    - scores each merchant-allowed policy       |
        |    - cart value breaks ties only                |
        |    - is_low_confidence -> merchant fallback     |
        | 5. Policy Engine (deterministic validator)     |
        |    - re-fetches live policy_config independently|
        |    - rejects anything outside the allowed set  |
        +-----------------------------------------------+
                        |
                        v
        PostgreSQL: orders, risk_predictions,
        policy_decisions, agent_traces, policy_config,
        customer_risk_cache, product_risk_cache
                        |
                        v (async, non-blocking BackgroundTask)
              Google Gemini -> audit_explanation
              (written back to policy_decisions after
               the HTTP response has already returned)
```

---

## 3. Tech Stack

| Layer | Choice |
|---|---|
| Backend API | FastAPI (Python) |
| Database | PostgreSQL (Supabase-compatible) |
| Agent orchestration | LangGraph |
| ML model | XGBoost |
| Explainability | SHAP (TreeExplainer) |
| Audit trail LLM | Google Gemini (flash tier) |
| Frontend | Next.js, TypeScript, Tailwind CSS |

---

## 4. Key Design Decisions

**Why XGBoost, not a deep model.** Tabular, structured features (return rate, cart composition, timing) — XGBoost is fast, well-understood, and produces feature importances (via SHAP) that are directly usable for per-order explainability. A deep model would add complexity without a corresponding accuracy benefit on this data shape.

**Why the Policy Agent is deterministic, not an LLM.** We deliberately chose rule-based, reproducible scoring (SHAP-category weights -> policy selection) over letting an LLM pick the policy. For a defense-only system whose actions are money-adjacent, "the same input always produces the same output" is a stronger, more auditable guarantee than LLM flexibility — and it's independently unit-testable in a way that LLM output isn't. The system is still genuinely agentic where it matters: the Confidence Router's investigation loop dynamically decides whether to pull more evidence based on what it already knows, which is the actual adaptive part of the architecture.

**Why the audit trail is async and LLM-based.** The LLM's only job is narrating an already-final decision in plain English for merchant/support use — it cannot alter the score, invent evidence, or override the Policy Engine. It runs after the HTTP response returns via a background task, so a customer's checkout is never slowed down by an LLM call; average end-to-end pipeline latency is 40-170ms without it.

**Why the Policy Engine is a separate component from the Policy Agent.** The Agent *recommends* using SHAP evidence; the Engine independently re-fetches the merchant's live configuration and *validates* the recommendation is actually within it — this means the system cannot act outside merchant-approved bounds even if a future bug caused the Agent's scoring to somehow escape its own constraints.

**Why no real payment gateway integration.** ReturnSentinel is intentionally gateway-agnostic middleware — it sits between "cart" and "checkout confirmed," decides a return policy, and gets out of the way. It never touches payment processing, which is why no Razorpay (or other gateway) API key is required. This is a scope decision, not a missing feature.

**Why no multi-tenant merchant auth.** Out of scope for this MVP by design — `policy_config` is a single-row table. Extending to multi-tenant is a small, well-understood migration (add a `merchant_id` column), deliberately deferred to keep focus on the risk/policy decision logic itself.

---

## 5. Metrics — Measured, Not Asserted

- **Model (held-out test set, never used in training or threshold tuning):** ROC-AUC 0.8466, plus PR-AUC, precision, recall, F1, and confusion matrices computed at multiple thresholds.
- **Confidence threshold (0.40) was chosen empirically** from the real distribution of `model_confidence` over the validation set — not picked arbitrarily. At the original threshold (0.60), 0% of high-risk validation rows could ever cross it, due to the model's real probability ceiling (~0.76). At 0.40, ~73% become reachable, while the deliberately-ambiguous MEDIUM band still correctly requires investigation on effectively 100% of live orders — a direct, expected consequence of MEDIUM being defined as the probability range closest to maximum model uncertainty.
- **Live pipeline latency:** 40-172ms end-to-end (feature building + model inference + routing + policy decision + validation), measured across real API calls, not estimated.
- **False-positive rate is reported as `null`, not zero or fabricated** — computing it honestly requires a real-world feedback loop (knowing which flagged orders were later confirmed legitimate) that doesn't exist yet. We consider showing this as unmeasured, rather than inventing a number, part of the "honest metrics" bar this track evaluates against.

---

## 6. Failure Recovery — What Broke, and How We Fixed It

### 6.1 The confidence threshold made high-risk decisions structurally unreachable
Our Confidence Router used `model_confidence = 2 x |probability - 0.5|` with a threshold of 0.60. By computing the actual probability distribution over our validation set — rather than assuming the threshold was reasonable — we found the model's maximum achievable probability was ~0.76, capping achievable confidence for any HIGH-risk prediction at ~0.48. Every high-risk order was mathematically guaranteed to exhaust its investigation budget regardless of evidence quality. We recalibrated to 0.40 using the same empirical-distribution method already used for our risk-level bands, verified against three candidate thresholds' real tradeoffs before choosing, and confirmed the fix by re-running our test scenarios: HIGH-risk orders with genuinely weak evidence (e.g. our "Test Case 2" scenario) still correctly fail, while orders with strong evidence (e.g. an 85.7% historical return rate) now correctly resolve.

### 6.2 Fixing #1 opened a new gap, which we closed with a targeted rule
After recalibrating, a HIGH-risk order could clear the new 0.40 bar using only cached data, before any live-data verification — undermining the entire point of the investigation loop for our highest-stakes decisions. We added one small, targeted rule: a HIGH-risk classification always triggers one mandatory live-data verification round, even if cached-data confidence already clears the threshold. Verified with a live test case: an order that previously would have resolved instantly on stale cached data now correctly gets investigated, and its confidence appropriately drops when live data reveals weaker evidence than the cache suggested.

### 6.3 A dashboard aggregation bug produced impossible arithmetic
Our `risk_distribution` dashboard stat summed to 73 when `orders_analyzed` was 62 — a direct sign of a real bug, not rounding noise. Root cause: `risk_predictions` intentionally allows multiple rows per order (to track investigation rounds), but our aggregation query wasn't filtering to the latest row per order, unlike `policy_decisions`, which already had upsert logic keeping it 1:1. Fixed with a windowed subquery selecting only the latest prediction per order; verified the corrected numbers summed exactly (19+9+11=39, matching `orders_analyzed`) rather than approximately.

---

## 7. Running Locally

```bash
# Backend
cd backend
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt
# set DATABASE_URL and GEMINI_API_KEY in .env (see .env.example)
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
# set NEXT_PUBLIC_API_BASE_URL in .env.local (see .env.local.example)
npm run dev
```
Merchant dashboard: `/dashboard`. Demo storefront: `/storefront`.

---

## 8. Scope Boundaries (Intentional, Not Gaps)

- No payment gateway integration (Razorpay or otherwise) — gateway-agnostic middleware by design.
- No multi-tenant merchant authentication — single-tenant MVP; `merchant_id` is a small, deferred extension.
- No real-world false-positive feedback loop — would require production return-outcome data this MVP doesn't have.
- No live deployment — per the buildathon's stated submission requirements, this repo, the pitch video, and this document are the complete deliverable.
