# ReturnSentinel AI

**Track:** AI Risk Manager (Razorpay AI Buildathon 2026)  
**One-line summary:** A return-risk scorer that predicts elevated return-abuse risk on an order before checkout and dynamically applies a merchant-approved return policy — defense-only, explainable, and bounded to what the merchant has approved.

> 📖 **Architecture & Deep Dive:** See [ARCHITECTURE.md](./ARCHITECTURE.md) for full design decisions, ML evaluation metrics, and failure-recovery case studies.

---

## What This Is

Retailers lost $103B to fraudulent and abusive returns in 2024, with wardrobing and size-bracketing cited most frequently. Existing solutions either block suspicious orders outright or tighten return policies universally, punishing legitimate shoppers along with abusive ones.

ReturnSentinel AI scores return-abuse risk **per order**, before payment, and responds with a **graduated, non-blocking** policy adjustment (Standard Return → Exchange First → Store Credit → Restocking Fee) instead of a binary allow/deny. It protects merchant margins while preserving a seamless, low-friction checkout experience for genuine customers.

---

## Tech Stack

| Layer | Choice |
|---|---|
| **Backend API** | FastAPI (Python 3.10+) |
| **Database** | PostgreSQL (Supabase-compatible, SQLAlchemy ORM) |
| **Agent Orchestration** | LangGraph (Stateful multi-round investigation) |
| **ML Risk Model** | XGBoost (Multi-signal tabular classifier) |
| **Explainability** | SHAP (TreeExplainer per-order factor attribution) |
| **Audit Trail LLM** | Google Gemini (Flash tier via async background tasks) |
| **Frontend** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS |

---

## Quickstart & Local Setup

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** 18+ (Node 20+ recommended)
- **PostgreSQL:** Local PostgreSQL instance or remote Supabase database URL
- **Google Gemini API Key:** For async audit trail narration ([Google AI Studio](https://aistudio.google.com/))

---

### 1. Backend Setup (FastAPI + LangGraph)

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\activate
# macOS/Linux:
# python3 -m venv venv && source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `backend/.env` with your database and API credentials:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/return_sentinel
GEMINI_API_KEY=your_gemini_api_key_here
```

*(Optional) Populate synthetic demonstration data (100 historical orders, products, and customers):*
```bash
python -m app.seed.seed_data
```

Start the backend server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```
- The backend will start on **`http://localhost:8000`**
- Interactive Swagger docs: **`http://localhost:8000/docs`**
- Health check: **`http://localhost:8000/health`**

---

### 2. Frontend Setup (Next.js + Tailwind CSS)

Open a second terminal window:

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Configure frontend environment variables
cp .env.local.example .env.local
```

`frontend/.env.local` should point to your local FastAPI backend:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Start the frontend development server:
```bash
npm run dev
```
- The frontend will start on **`http://localhost:3000`**

---

## Application Navigation

| Route | View | Description |
|---|---|---|
| **`/dashboard`** | **Merchant Dashboard** | Executive overview of evaluated orders, risk distributions, and margin protection metrics. |
| **`/orders`** | **Orders & Risk Feed** | Live audit table of cart assessments, risk levels, and applied return policies. |
| **`/risk-analysis`** | **Risk Deep Dive** | Granular inspection of XGBoost SHAP factor attributions and LangGraph investigation rounds. |
| **`/policies`** | **Policy Configuration** | Merchant controls to configure defensive policies for Low, Medium, and High risk tiers. |
| **`/analytics`** | **Margin Analytics** | Return rate trends, abuse mitigation savings, and policy breakdown charts. |
| **`/settings`** | **System Settings** | Merchant store profile and sensitivity thresholds. |
| **`/storefront`** | **Demo Storefront** | *Atelier Sentinel* boutique experience to test customer checkout, multi-size bracketing, and live policy assessments. |

---

## Testing the ReturnSentinel Flow

1. Open **`http://localhost:3000/storefront`** (Demo customer persona selector is in the top bar).
2. Add items to your bag. To test **Size Bracketing**, add the same product in two different sizes (e.g. Size M + Size L).
3. Open the Bag (**`/storefront/cart`**) and click **Proceed to Checkout**.
4. Observe the **Pre-Checkout Return Policy Assessment** generated in real time by the backend risk pipeline.
5. Switch to the **Merchant Dashboard** (**`/dashboard`** or **`/orders`**) to inspect the order's risk score, SHAP explanation factors, and agent investigation trace.
