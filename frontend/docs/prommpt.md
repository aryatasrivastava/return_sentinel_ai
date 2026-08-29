ROLE

You are implementing the frontend foundation only for a project called ReturnSentinel AI. Act as a senior frontend engineer building a real B2B SaaS/fintech-grade product, not a demo or landing page.

PROJECT CONTEXT

ReturnSentinel AI is an agentic AI system for e-commerce merchants that predicts return-fraud risk (serial returners, "wardrobing") before checkout and applies a defensive-but-non-blocking return policy (Standard Return / Exchange First / Store Credit / Restocking Fee). Under the hood (not part of this milestone): a LangGraph-orchestrated Risk Agent gathers evidence via tools, an XGBoost model scores the risk, a confidence router decides if more investigation is needed, and a Policy Agent recommends a policy that a deterministic Policy Engine validates against merchant rules. An LLM then writes a plain-language audit trail.

Tagline: "Protecting e-commerce margins from return abuse — before checkout."

This milestone builds ONLY the Next.js frontend, with mock data. No backend, no API routes, no database, no LangGraph, no ML, no Razorpay code. Structure everything so a real API can replace the mock data layer later without touching component code.

TECH STACK
Next.js (App Router) + TypeScript
Tailwind CSS
No component libraries, no chart libraries, no state-management libraries. If you believe one genuinely necessary, stop and explain why before adding it — default answer is no.
Fonts via next/font: Inter (UI/body/headings) and IBM Plex Mono (all numeric/data readouts — risk scores, confidence %, currency, order IDs, timestamps, function-call names in the trace). This pairing is deliberate: mono numerals signal "this value came from a model/computation," distinguishing machine output from human-authored copy throughout the UI. Don't substitute other fonts.
DESIGN SYSTEM (implement exactly — do not default to generic Tailwind/shadcn styling)

Brand direction: premium, restrained, enterprise, trustworthy risk-intelligence tool. Light content area, dark ink sidebar. Crisp corners (not bubbly/playful), mostly flat cards with hairline borders rather than heavy drop shadows, one disciplined accent color used sparingly. No robot/AI cliché imagery, no gradients-as-decoration, no neon.

Color tokens (define as CSS variables in globals.css):

--bg: #F6F7F9              /* app background */
--surface: #FFFFFF          /* cards, table rows */
--surface-sunken: #EEF0F4   /* subtle wells, striped rows, code/mono blocks */
--border: #E2E5EB
--ink-900: #0E1526          /* primary text; also sidebar background */
--ink-600: #4B5568          /* secondary text */
--ink-400: #8992A3          /* muted/placeholder text */

--accent: #3B4C9E           /* "Sentinel Indigo" — primary brand + interactive color */
--accent-soft: #EEF0FB      /* accent tint background (active nav item, selected states) */

--success: #1E8A6E
--success-soft: #E7F5F0
--warning: #B8842B
--warning-soft: #FBF2E2
--danger: #B3413A
--danger-soft: #FBEAE8

--focus-ring: rgba(59, 76, 158, 0.45)

Risk levels map to these semantics: Low → success, Medium → warning, High → danger. Never rely on color alone — always pair with text label and, where relevant, an icon (accessibility requirement below).

Typography scale (Tailwind config, in rem, Inter unless noted mono):

display: 1.75rem / 2.25rem line-height, weight 600 — page-level hero numbers only (e.g. dashboard "Orders Analyzed" isn't this big; reserve for empty-state or a rare hero moment)
h1: 1.375rem / 1.75rem, weight 600 — page titles
h2: 1.125rem / 1.5rem, weight 600 — section headers, card titles
body: 0.875rem / 1.25rem, weight 400 — default UI text
caption: 0.75rem / 1rem, weight 500, --ink-400 — labels, table headers, meta text
data-lg (mono): 2rem / 2.25rem, weight 500, tabular-nums — big stat numbers, risk score readouts
data-md (mono): 1.25rem / 1.5rem, weight 500, tabular-nums — inline risk/confidence values
data-sm (mono): 0.8125rem / 1.125rem, weight 400, tabular-nums — table cells (Order ID, Cart Value, timestamps, function call names)

Radius: cards/panels 8px, inputs/buttons/badges 6px, small chips 4px. No rounded-full except status dots and avatar circles.

Shadow: flat cards use 1px solid var(--border) only, no shadow. Reserve a single soft shadow (0 4px 16px rgba(14,21,38,0.08)) for truly elevated surfaces: dropdown menus, modals, popovers. Never stack shadow + border decoratively.

Spacing: 4px base unit; use 8/12/16/24/32/48 consistently for padding/gaps. Page content max-width ~1280px, side padding 24px (32px on large screens).

Signature element — the Agent Decision Trace: this is the one place to spend visual boldness; keep everything else quiet. Render it as a vertical connected timeline where each step is a distinct node shape encoding its category (this distinction is the whole point — it's what proves the system is agentic, not a lookup table):

Agent decision node → filled indigo circle, body-weight label (e.g. "Risk Agent")
Tool call node → slate square marker, label rendered in mono exactly as a function call, e.g. get_customer_history()
ML prediction node → amber diamond marker, mono value readout (e.g. Risk Score: 81/100)
Routing decision node → the connecting line itself forks/dashes to show a branch (e.g. confidence check routing to further investigation vs. Policy Agent)
Final policy node → green pill/badge, e.g. EXCHANGE_FIRST

Connector: a thin vertical line (--border, 2px) running through all nodes, dashed for not-yet-reached steps in any future "live" state, solid for completed ones. Keep it a single component so it can later stream real steps.

ROUTES (App Router)
/dashboard — primary landing page
/orders
/risk-analysis
/policies
/analytics
/settings

All non-dashboard pages must be fully styled with realistic mock content and the shared layout chrome — not blank placeholders.

LAYOUT SHELL
Sidebar (--ink-900 background, fixed width ~240px desktop): logo/wordmark "ReturnSentinel AI" at top, nav items (Dashboard, Orders, Risk Analysis, Policies, Analytics, Settings) each with an icon + label, active item gets --accent-soft-tinted pill background with indigo text/icon. Collapses to icon-only rail under 1024px, and to an off-canvas drawer (hamburger-triggered) under 768px.
Header (sticky, --surface background, bottom border): page title (h1) + short description on the left; right side has a merchant/org name placeholder and a notification bell icon (non-functional).
PageContainer: consistent max-width, padding, and vertical rhythm wrapper used by every route.
PAGE SPECS
/dashboard
4-up stat card row: Orders Analyzed (127), High-Risk Orders (18), Estimated Margin Protected (₹8,420), False Positive Rate (3.2%) — each a StatCard with caption label, data-lg mono value, and a small trend/context line. Add a subtle "demo data" caption under the row so it's never mistaken for live figures.
Recent AI Decisions: a compact DecisionTable (Order ID, Customer, Risk badge, Policy badge, Confidence) linking conceptually to /orders.
One full Agent Decision Trace example card (the signature component above) using the get_customer_history → analyze_cart → get_product_stats → XGBoost → Risk Score 81/100 → Confidence 91% → Policy Agent → Exchange First sequence from the brief.
Risk Distribution and Policy Distribution: two side-by-side cards with simple static bar/segmented visualizations (plain divs with proportional widths — no chart library) showing counts across Low/Medium/High and across the four policies.
Merchant Protection Summary card: short block contrasting margin protected vs. estimated customer friction, in prose + two mono stat readouts.
/orders

OrdersTable with columns: Order ID, Customer, Cart Value, Risk Score, Confidence, Policy, Status. Risk uses a RiskBadge (Low/Medium/High, color + label, never color-only). Policy uses a PolicyBadge (Standard Return / Exchange First / Store Credit / Restocking Fee). Include a search input and filter-by-risk/policy dropdowns above the table — styled and interactive-looking but wired to no-op handlers for now (comment clearly marking where real filtering logic goes). ~10–15 mock rows spanning all risk levels and policies.

/risk-analysis

Detail-page layout (assume navigated to from an order): Risk overview header (score + level + confidence, using RiskScore/ConfidenceIndicator), then sectioned SignalList panels for Customer Behavior, Cart Signals, Product Signals, ML Prediction output, and an "Agent Investigation History" section reusing the Agent Decision Trace component. Design this page so a real Risk Agent execution can later populate every section 1:1.

/policies

Grid/list of PolicyCards for Standard Return, Exchange First, Store Credit, Restocking Fee — each showing name, one-line description, Enabled/Disabled toggle (visual, non-functional), a customer-friction indicator, and a merchant-protection-level indicator (both as small labeled meters, not just color).

/analytics

Stat cards for Orders Analyzed, Return Abuse Rate, High-Risk Orders, False Positives, Estimated Margin Protected, plus a Policy Distribution section (reuse the dashboard's static visualization pattern, not a duplicate implementation).

/settings

Sectioned form-style UI (non-functional inputs) for: Merchant Profile, Return Policy Configuration, Risk Thresholds, Notification Preferences. Use Card sections with clear headers; no submit logic needed yet.

COMPONENTS TO BUILD (single source of truth — no duplicated UI across pages)
components/
  layout/
    Sidebar.tsx
    Header.tsx
    PageContainer.tsx
  dashboard/
    StatCard.tsx
    DecisionTable.tsx
    AgentTrace.tsx          // the signature component, reused on /risk-analysis too
    RiskDistribution.tsx
    PolicyDistribution.tsx
  risk/
    RiskBadge.tsx
    RiskScore.tsx
    ConfidenceIndicator.tsx
    SignalList.tsx
  policies/
    PolicyCard.tsx
    PolicyBadge.tsx
  ui/
    Button.tsx
    Badge.tsx
    Card.tsx
    Table.tsx
    EmptyState.tsx
    LoadingState.tsx

AgentTrace must accept a steps: AgentStep[] prop (typed below) so it's identical whether fed mock data now or a real LangGraph trace later.

TYPESCRIPT TYPES (lib/types.ts or types/index.ts)

Define and export:

RiskLevel = "low" | "medium" | "high"
PolicyType = "STANDARD_RETURN" | "EXCHANGE_FIRST" | "STORE_CREDIT" | "RESTOCKING_FEE"
Customer { id, name, email, returnRate, previousReturns, ... }
Order { id, customer: Customer, cartValue, riskScore, confidence, policy: PolicyType, status, createdAt }
RiskAssessment { orderId, riskScore, riskLevel: RiskLevel, confidence, signals: {...}, mlPrediction: {...} }
PolicyDecision { orderId, policy: PolicyType, rationale, protectedMargin }
AgentStep { id, type: "agent" | "tool" | "ml" | "routing" | "policy", label, detail?, status: "complete" | "pending" }
DashboardStats { ordersAnalyzed, highRiskOrders, marginProtected, falsePositiveRate }

Keep these purely as data shapes — no UI logic in this file.

MOCK DATA

Central location: lib/mock-data/ with separate files (customers.ts, orders.ts, riskAssessments.ts, policyDecisions.ts, agentTraces.ts, dashboardStats.ts), each exporting typed, realistic arrays/objects matching the types above. Components must import from here — never inline large arrays in JSX. Include enough variety to cover Low/Medium/High risk and all four policies across the mock orders.

LOADING / EMPTY / ERROR STATES

Build generic LoadingState (skeleton-style, using --surface-sunken blocks, no spinner-only) and EmptyState (icon + short message + optional action) components used consistently. Error states reuse EmptyState with a danger-tinted variant. None need real triggering logic yet — just build and demonstrate each once (e.g. on /orders show what an empty filtered state would look like, gated behind a hardcoded boolean you leave commented for easy toggling during development).

RESPONSIVE & ACCESSIBILITY
Desktop-first, but verify tablet and mobile: sidebar collapses as specified above; tables scroll horizontally within a bounded container on small screens rather than breaking layout.
Semantic HTML (<nav>, <table>, <button> — never <div onClick> for interactive elements).
Visible keyboard focus using --focus-ring on all interactive elements.
Every risk/policy badge carries a text label, not color alone.
Sufficient contrast: verify body text on --bg/--surface and white text on --ink-900 both meet WCAG AA.
GLOBAL CSS / CONFIG CHANGES
src/app/globals.css → modify: define all CSS variables above under :root, base element resets, font-feature-settings: "tnum" applied wherever mono data classes are used for consistent tabular alignment.
tailwind.config.ts → modify: extend colors to reference the CSS variables, extend fontFamily with sans (Inter) and mono (IBM Plex Mono), extend fontSize with the display/h1/h2/body/caption/data-lg/data-md/data-sm scale, extend borderRadius (card: 8px, control: 6px, chip: 4px).
src/app/layout.tsx → modify: load both fonts via next/font/google, set metadata (title "ReturnSentinel AI", description = the tagline), wrap children in the base shell (Sidebar + Header + content slot) — but only for authenticated-style app routes; keep it simple, no route groups unless the existing project already has a marketing/app split.
IMPLEMENTATION SAFETY
Inspect the existing project structure first; do not overwrite working config unnecessarily.
Do not add any package beyond what's already implied (Next.js, TypeScript, Tailwind, next/font). If something else feels necessary, stop and explain before adding it.
Do not create backend code, API routes, database code, LangGraph code, ML code, or Razorpay code — frontend only, this milestone.
After implementing, run the dev build and npm run build, fix all TypeScript/build errors, and manually verify all six routes render without console errors.
DELIVERABLE FOR THIS MILESTONE

A working Next.js app with the shell, all six routes fully styled with mock data, the full component/type/mock-data structure above, and a passing npm run build. Report back what was created/modified, file by file, and flag any deviation from this spec before making it.