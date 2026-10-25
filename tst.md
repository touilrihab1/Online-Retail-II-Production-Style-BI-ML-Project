# Online Retail II — Production-Style BI/ML Project

**Owner:** Rihab Touil
**Purpose:** A portfolio project for the German data/ML job market that demonstrates end-to-end ownership — data modeling, statistically grounded analysis, an ML model tuned with methods from my thesis (Bayesian Optimization), a served API, and a dashboard. The goal is a project I can defend line-by-line in an interview, not a tutorial I followed.

**Core business question:** *Where are we making money, where are we losing money, and which customers should we worry about?*

**Stack:** Python, SQLite, FastAPI, Streamlit, XGBoost, BoTorch/scikit-optimize, Docker, Git.

---

## 0. Guiding Principles

These are the things that separate this project from a standard RFM/churn tutorial, and what I should be able to explain unprompted in an interview:

1. **Every modeling choice is derived, not assumed.** Churn cutoffs, RFM bucket boundaries, and the guest-customer rule all come from looking at the data, not from convention.
2. **Time matters.** Any train/test split respects the calendar — I never let the model see the future.
3. **Architecture mirrors a real system.** The dashboard talks to an API, not to the database directly.
4. **The thesis connects to the portfolio.** Bayesian Optimization isn't just for the thesis — it's the tuning method here too, and I can explain *why* it's a better fit than grid/random search for this problem.
5. **Documentation is part of the deliverable**, not an afterthought written in the last hour.

---

## 1. Business Questions This Project Answers

| Theme | Questions |
|---|---|
| **Revenue Leakage** | What % of gross revenue is lost to returns/cancellations? Which products and countries drive the most leakage? |
| **Customer Value** | How does Guest vs. Registered revenue compare? Who are the highest-value customers by net revenue? |
| **Product & Market Performance** | Which products have the highest gross/net revenue? Which have high gross revenue but disproportionately low net revenue due to returns? |
| **Churn Risk** | Who are the highest-value customers by RFM profile? Which previously valuable customers look at risk of churn? |

---

## Phase 0 — Data Foundation

**Status: mostly done.** Remaining work turns a working script into a defensible data layer.

- [x] Load and merge the `2009-2010` and `2010-2011` sheets
- [x] Encode missing `Customer ID` as guest customers (`0`) — **not dropped**, because guest transactions are real revenue and excluding them would understate total sales
- [x] Flag (not drop) duplicates and negative quantities — negatives are returns, not data errors
- [x] Compute `revenue = quantity * price`
- [x] Clean column names
- [x] Load into SQLite
- [ ] Normalize the schema into three tables instead of one flat file:
  - `transactions(invoice_no, stock_code, customer_id FK, invoice_date, quantity, price, revenue)`
  - `customers(customer_id, country, first_seen, last_seen)`
  - `products(stock_code, description, avg_price)`
- [ ] Add indexes on `customer_id`, `invoice_date`, `stock_code`
- [ ] Write `data_dictionary.md`: every column, its type, and every business assumption baked into the pipeline (guest encoding, negative-quantity meaning, etc.)

**Done when:** a stranger can open the SQLite file, understand the schema from the data dictionary alone, and every assumption is written down rather than implied by code.

---

## Phase 1 — SQL Business Questions

For each question below: write the SQL, persist the output as a table/view, and write 2–3 sentences of interpretation. These interpretations become the "Key Findings" section of the README later — write them as you go, not retroactively.

- **Q1 — Revenue Leakage** *(in progress)*
  Total refunded value and leakage as a % of gross revenue; leakage by month, country, and top returned products. Where possible, match negative-quantity rows to a prior positive invoice to distinguish a "true return" from a standalone negative-quantity entry.

- **Q2 — RFM Segmentation**
  Compute Recency, Frequency, Monetary per customer. Bucket into segments using quantile-based binning (justify the number of buckets — don't default to quartiles without checking the distribution). Exclude `customer_id = 0` from per-customer analysis, and say why in the interpretation.

- **Q3 — Churn Definition (statistically derived)**
  Plot the distribution of inter-purchase gaps across all customers. Pick the churn cutoff as a percentile of that distribution instead of a round number like "90 days." Run a sensitivity check: how does the churned-customer count change if the cutoff shifts ±30 days? Document this as a modeling decision.

- **Q4 — Cohort Retention**
  Monthly acquisition cohorts by first purchase date; retention curve (% still active) per cohort by month N.

- **Q5 — Customer Lifetime Value**
  Historical CLV = total revenue per customer over the observed window. Stretch: break CLV down by RFM tier or cohort.

**Done when:** five questions, each with a saved output table and a written interpretation — not just a query result sitting in a notebook.

---

## Phase 2 — Feature Engineering & Churn Model

- [ ] Build a feature table: RFM + cohort features + product-diversity features (distinct categories bought, average order value, days since first purchase)
- [ ] **Time-aware split**: train on behavior through month *T*, predict churn in *T+1*. No random split — that would leak future purchase behavior into the training labels.
- [ ] Baseline: Logistic Regression
- [ ] Main model: XGBoost
- [ ] **Tune XGBoost with Bayesian Optimization**, not grid/random search. Write a short paragraph on *why* BO is more sample-efficient for this search space — this is the direct, honest bridge to the thesis work, and the one thing I most want an interviewer to ask about.
- [ ] Evaluate with precision/recall/F1/PR-AUC, and explain explicitly why raw accuracy is misleading under class imbalance
- [ ] Add a calibration check (reliability curve or Brier score) on the predicted churn probabilities — another natural tie-back to the Bayesian background
- [ ] Feature importance / SHAP for interpretability

**Done when:** the churn model is documented end-to-end with a justified tuning method and an honest evaluation — not a single accuracy number — plus an interpretability step.

---

## Phase 3 — Serving Layer (FastAPI)

- [ ] `GET /customers/{id}/rfm` — RFM values + segment
- [ ] `GET /customers/{id}/churn-risk` — churn probability from the trained model
- [ ] `GET /revenue-leakage/summary` — leakage KPIs from Q1
- [ ] `GET /cohorts/retention` — retention curve data
- [ ] Input validation via Pydantic models; explicit error handling for unknown `customer_id`
- [ ] A handful of `pytest` unit tests covering the endpoints and the feature-engineering functions

**Done when:** the API runs locally with auto-generated docs and has real test coverage — this is the layer most portfolio projects skip entirely, which is exactly why it's worth doing well.

---

## Phase 4 — Dashboard (Streamlit)

- [ ] Dashboard consumes the FastAPI endpoints — never queries SQLite directly. This is the realistic client/server split a reviewer will notice.
- [ ] Pages: Revenue Leakage overview · RFM/segment explorer · Churn risk lookup · Cohort retention chart
- [ ] Keep it clean and interpretable — this is the first thing a reviewer opens, so it should read like a decision-support tool, not a scratchpad.

**Done when:** the dashboard works end-to-end against the API layer with zero duplicated query logic.

---

## Phase 5 — Packaging & Documentation

- [ ] `requirements.txt` / environment file
- [ ] Dockerfile (API + dashboard, or API first if time is tight)
- [ ] README containing:
  - Problem framing and architecture diagram
  - Key findings **with numbers** ("identified €X in leakage," "Y% churn risk in the top RFM segment")
  - How to run it locally and in Docker
  - The methodological choices and why: time-aware split, BO tuning, data-derived churn cutoff
- [ ] Incremental, meaningful Git commits — the commit history should tell the story of the project, not arrive as one final dump

**Done when:** a stranger can clone the repo, read the README, and understand both *what* the project does and *why* the choices were made.

---

## Interview Defense Checklist

Be ready to explain each of these in your own words, unprompted:

1. Why guest customers (`customer_id = 0`) are handled separately rather than dropped
2. Why the churn train/test split is time-aware rather than random
3. How the churn cutoff was derived from the data rather than chosen by convention
4. Why Bayesian Optimization was used for tuning, and what it bought over grid search
5. Why accuracy alone doesn't tell you whether the churn model is good
6. What the API/dashboard split buys architecturally over a single Streamlit script

If all six answers come easily, the project has done its job — regardless of how well-known the underlying dataset is.

---

## Suggested Build Order

1. Finish Phase 0 (schema + data dictionary) — everything downstream depends on trusting this layer.
2. Phase 1, Q1–Q3 first (leakage, RFM, churn definition) — these feed the model and the dashboard's first two pages.
3. Phase 2 (model) — the highest-leverage phase for interview talking points; don't rush the BO write-up.
4. Phase 3 (API) before Phase 4 (dashboard) — the dashboard has nothing to call otherwise.
5. Phase 5 continuously, not at the end — write README sections as each phase finishes.