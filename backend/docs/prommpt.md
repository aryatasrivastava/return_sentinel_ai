# Antigravity Prompt — ReturnSentinel AI: Phase 1, PostgreSQL Database Foundation

Copy everything below the line into Antigravity.

---

## ROLE

You are extending an **existing, already-working FastAPI backend** for a hackathon project called **ReturnSentinel AI**. This task is strictly scoped to database foundation work. Do not implement anything outside this scope, even if it seems like a natural next step.

## PROJECT CONTEXT

ReturnSentinel AI is an agentic system that predicts return-fraud/wardrobing risk on an order **before payment**, then (in future phases) applies a merchant-approved, non-blocking return policy (Standard Return / Exchange First / Store Credit / Restocking Fee) instead of denying the sale. It evaluates signals like customer return history, cart contents (e.g. multiple sizes of the same product), product-level return patterns, and purchase timing.

**Full eventual architecture** (not being built now — provided only so you understand what the database must support later):

```
Next.js Frontend → FastAPI Backend → LangGraph Orchestration → Risk Agent
→ Dynamic Tool Calls → PostgreSQL Database → XGBoost Risk Model
→ Risk Score + Confidence → Confidence Router
→ (insufficient confidence → investigate further, capped rounds)
→ (sufficient confidence → Policy Agent) → Policy Engine
→ Final Merchant-Approved Policy → Async Audit Explanation (LLM-written,
   generated after the policy is already returned — never blocks checkout)
→ Razorpay Test Mode Checkout
```

A key performance requirement that shapes this schema: customer-level and product-level risk signals (return rate, previous returns, order count, days since last order, product return rate) are **precomputed and cached**, not recalculated live at checkout — only cart-specific signals are computed in realtime. This is why two small cache tables are included below in addition to the core entities.

## CURRENT BACKEND STATUS — DO NOT BREAK THIS

Existing, working structure:
```
backend/
├── venv/
└── app/
    └── main.py
```
- Python 3.13, virtual environment already created and working.
- Installed packages: `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`.
- Server runs via `uvicorn app.main:app --reload`.
- Working endpoints: `GET /` and `GET /health` (returns `{"status": "healthy"}`).

**Before making any change, inspect `backend/app/main.py` and the existing project structure.** Do not recreate the FastAPI project from scratch, do not delete or unnecessarily rewrite `main.py`, and do not break `GET /` or `GET /health` — verify both still work at the end.

## CURRENT TASK — SCOPE

This project follows a 4-phase backend roadmap:
```
PHASE 1 — Backend + Database Foundation   ← FastAPI part done; DB part is THIS task
PHASE 2 — Risk Intelligence + XGBoost
PHASE 3 — Agentic AI System
PHASE 4 — Full Integration + Audit + Razorpay Demo
```

**Implement ONLY the remaining part of Phase 1: the PostgreSQL database foundation.** Do not begin Phase 2, 3, or 4.

### Explicitly DO NOT implement in this task
LangGraph, Risk Agent, Policy Agent, agent tool calling, any LLM integration, XGBoost or any ML training, Confidence Router, Policy Engine, Razorpay, frontend changes, authentication, Redis, Celery, Docker, or microservices. If you find yourself about to write logic that computes a risk score or calls an LLM, stop — that's out of scope for this task.

## TARGET DATABASE

**PostgreSQL**, preferably **Supabase-hosted PostgreSQL**. Design the schema so future tools can cleanly query: customer history, order history, return history, product statistics, and cart/order behavior — without implementing any of those tools now.

## SCHEMA — ENTITIES

Implement exactly these 9 tables (7 core entities + 2 small, genuinely necessary cache tables — do not add others, do not over-engineer):

### 1. `customers`
- `id` (UUID or SERIAL, PK)
- `name` (VARCHAR, not null)
- `email` (VARCHAR, unique, not null)
- `created_at` (TIMESTAMP, default now)

### 2. `products`
- `id` (PK)
- `name` (VARCHAR, not null)
- `sku` (VARCHAR, unique)
- `category` (VARCHAR)
- `price` (NUMERIC(10,2))
- `created_at` (TIMESTAMP, default now)

### 3. `orders`
- `id` (PK)
- `customer_id` (FK → customers, not null, indexed)
- `order_value` (NUMERIC(10,2))
- `status` (VARCHAR or enum: `pending`, `completed`, `cancelled`)
- `created_at` (TIMESTAMP, default now)

### 4. `order_items`
- `id` (PK)
- `order_id` (FK → orders, not null, indexed)
- `product_id` (FK → products, not null, indexed)
- `size` (VARCHAR, nullable — needed to later detect "multiple sizes of same product" signal)
- `quantity` (INT, default 1)
- `unit_price` (NUMERIC(10,2))

### 5. `returns`
- `id` (PK)
- `order_id` (FK → orders, not null, indexed)
- `order_item_id` (FK → order_items, nullable — a return can reference a specific item or the whole order)
- `reason` (TEXT, nullable)
- `condition` (VARCHAR, nullable — e.g. `unused`, `worn`, `defective` — useful signal for future wardrobing detection)
- `created_at` (TIMESTAMP, default now)

### 6. `risk_predictions`
- `id` (PK)
- `order_id` (FK → orders, not null, indexed)
- `risk_score` (NUMERIC(5,2))
- `risk_level` (VARCHAR or enum: `low`, `medium`, `high`)
- `confidence` (NUMERIC(4,3))
- `model_version` (VARCHAR, nullable — placeholder for future ML versioning)
- `investigation_round` (INT, default 0 — supports the future confidence-router re-investigation loop; multiple rows per order are allowed, one per round)
- `is_final` (BOOLEAN, default false)
- `created_at` (TIMESTAMP, default now)

### 7. `policy_decisions`
- `id` (PK)
- `order_id` (FK → orders, not null, unique, indexed — one final policy per order)
- `policy_type` (VARCHAR or enum: `STANDARD_RETURN`, `EXCHANGE_FIRST`, `STORE_CREDIT`, `RESTOCKING_FEE`)
- `audit_explanation` (TEXT, nullable — populated later, asynchronously, by the future audit-trail LLM step; must stay nullable so it can be empty immediately after the policy decision and filled in afterward without blocking anything)
- `audit_generated_at` (TIMESTAMP, nullable)
- `created_at` (TIMESTAMP, default now)

### 8. `customer_risk_cache` (supporting table — precomputed customer-level signals)
- `customer_id` (FK → customers, PK/unique)
- `return_rate` (NUMERIC(5,4))
- `previous_returns` (INT, default 0)
- `order_count` (INT, default 0)
- `days_since_last_order` (INT, nullable)
- `behavior_flags` (JSONB, nullable — flexible slot for future signals without a migration)
- `updated_at` (TIMESTAMP, default now)

### 9. `product_risk_cache` (supporting table — precomputed product-level signals)
- `product_id` (FK → products, PK/unique)
- `return_rate` (NUMERIC(5,4))
- `category_return_rate` (NUMERIC(5,4), nullable)
- `updated_at` (TIMESTAMP, default now)

Do **not** implement the logic that populates or refreshes these two cache tables in realtime — that's Phase 2/3 work. For this phase, just create the tables and seed them with static demo values (see below) as if a background job had already run once.

## RELATIONSHIPS

```
customers 1──* orders
orders    1──* order_items ──* products
orders    1──* returns  (returns may also reference a specific order_item)
orders    1──* risk_predictions
orders    1──1 policy_decisions
customers 1──1 customer_risk_cache
products  1──1 product_risk_cache
```

Use proper primary keys, foreign keys with `ON DELETE` behavior that makes sense (e.g. `CASCADE` from orders to order_items/returns/risk_predictions/policy_decisions), appropriate PostgreSQL types, `NOT NULL` where specified above, and indexes on all foreign key columns plus `orders.customer_id`, `order_items.order_id`, `returns.order_id`, `risk_predictions.order_id`, `policy_decisions.order_id`.

## BACKEND STRUCTURE

Inspect the existing project first, then create only what's needed. Suggested structure (adapt if the existing project already implies something slightly different — explain any deviation):

```
backend/
├── app/
│   ├── main.py            (MODIFY minimally if at all — e.g. lifespan hook to
│   │                        verify DB connectivity on startup; do not restructure
│   │                        existing routes)
│   ├── core/
│   │   └── config.py       (CREATE — loads env vars via python-dotenv/pydantic settings)
│   ├── db/
│   │   ├── session.py       (CREATE — SQLAlchemy engine/session setup)
│   │   └── base.py          (CREATE — declarative base, imports all models so
│   │                          migrations/create_all can find them)
│   ├── models/
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── return_.py       (avoid the reserved word `return` as a filename/identifier)
│   │   ├── risk_prediction.py
│   │   ├── policy_decision.py
│   │   ├── customer_risk_cache.py
│   │   └── product_risk_cache.py
│   └── seed/
│       └── seed_data.py     (CREATE — deterministic demo data script, see below)
├── venv/                    (existing — do not touch)
├── .env                     (CREATE locally — must NOT be committed)
├── .env.example              (CREATE — committed, no real values)
├── .gitignore                (CREATE or MODIFY)
└── requirements.txt          (CREATE or MODIFY)
```

Use **SQLAlchemy** (with `psycopg2-binary` or `psycopg`) as the ORM/driver — no other ORM, no raw migration framework needed for a one-week MVP; a simple `Base.metadata.create_all()` bootstrap script is sufficient instead of a full Alembic setup. If you believe Alembic is genuinely necessary, explain why before adding it.

## ENVIRONMENT VARIABLES

Create `.env.example` with placeholders (no real values) for at least:
```
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
```
In the prompt output/README notes, explain clearly that these values come from the user's **Supabase project settings → Database → Connection string** (specifically the "Connection Pooling" or direct connection string, whichever the implementation uses), and that the user must never commit their real `.env`.

Update `.gitignore` to include at minimum:
```
venv/
.env
__pycache__/
*.pyc
```

## DEPENDENCIES

Add only what's required for this phase to `requirements.txt`: `sqlalchemy`, `psycopg2-binary` (or `psycopg[binary]`), plus whatever's already installed (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`). Do not add anything beyond database connectivity needs.

## DETERMINISTIC SEED DATA

Create `app/seed/seed_data.py` (runnable as a standalone script) that inserts three demo customers with data supporting these fixed scenarios:

**Customer A — Low Risk**
- ~10 previous orders, ~1 return → low historical return rate
- Normal cart behavior on orders (no unusual multi-size patterns)
- `customer_risk_cache` row reflecting a low `return_rate` and low `previous_returns`

**Customer B — High Risk**
- ~20 previous orders, ~15 returns → high historical return rate
- At least one order with multiple order_items referencing the *same product* in different `size` values (to later support the "multiple sizes of same product" cart signal)
- At least one higher-value order
- `customer_risk_cache` row reflecting a high `return_rate` and high `previous_returns`

**Customer C — Uncertain**
- A new/recent customer with very few orders and little/no return history
- `customer_risk_cache` row with low `order_count` and mostly null/near-zero fields, deliberately representing "insufficient evidence" for future confidence calculations

Also seed a small, reasonable set of `products` (e.g. 10–15 across a couple categories) with corresponding `product_risk_cache` rows (mix of low- and high-return-rate products), and enough `order_items`/`returns` rows tying everything together consistently with the above per-customer scenarios.

Keep the seed script idempotent or at least clearly re-runnable (e.g. clear relevant tables first, or check for existing data) so it can be run repeatedly during development without erroring.

## IMPLEMENTATION STEPS FOR ANTIGRAVITY

1. Inspect the existing `backend/` project structure and `main.py` before changing anything.
2. Install only the required new dependencies into the existing venv; update `requirements.txt`.
3. Create the config/env-loading layer.
4. Create the SQLAlchemy engine/session/base setup.
5. Create the 9 SQLAlchemy models exactly as specified above, with correct types, constraints, relationships, and indexes.
6. Add a way to create all tables against the connected database (a bootstrap script or a startup hook — keep it simple; no Alembic unless you justify it first).
7. Write the deterministic seed script for Customers A, B, C plus supporting products.
8. Create `.env.example` and update `.gitignore`.
9. Verify: FastAPI still starts successfully via `uvicorn app.main:app --reload`.
10. Verify: `GET /health` still returns `{"status": "healthy"}`.
11. Verify: the app can connect to PostgreSQL/Supabase using the `DATABASE_URL` from `.env`.
12. Verify: all 9 tables are created with correct relationships.
13. Verify: seed data inserts cleanly and represents the three demo scenarios.
14. Fix any Python, import, dependency, or database errors encountered.
15. Do not proceed to Phase 2, 3, or 4.
16. Report back file-by-file what was created/modified and why, and flag any deviation from this spec before making it.

## ACCEPTANCE CRITERIA

- [ ] FastAPI starts successfully with no errors.
- [ ] `GET /health` still returns `{"status": "healthy"}`.
- [ ] Backend successfully connects to PostgreSQL/Supabase using env-var credentials only (no hardcoded credentials anywhere).
- [ ] All 9 tables exist with correct columns, types, foreign keys, and indexes.
- [ ] Relationships work correctly (e.g. querying an order's items, a customer's orders, an order's returns).
- [ ] Seed data exists and clearly represents Customer A (low risk), Customer B (high risk), Customer C (uncertain).
- [ ] `customer_risk_cache` and `product_risk_cache` are populated with static demo values for all seeded customers/products.
- [ ] Project structure is clean, minimal, and beginner-readable.
- [ ] No LangGraph, agent, LLM, XGBoost, Confidence Router, Policy Engine, Razorpay, auth, Redis, Celery, Docker, or microservice code has been introduced.