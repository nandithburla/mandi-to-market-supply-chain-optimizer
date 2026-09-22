# 🌾 Mandi-to-Market Supply Chain Optimizer
> **An Intelligent AgriTech Analytics Engine & AI-Driven Decision Support System**

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ LIVE PLATFORM   : http://51.20.97.243                                            │
│ INFRASTRUCTURE  : AWS (eu-north-1) • Amazon EKS • EC2 Nginx Gateway              │
│ CORE STACK      : FastAPI • React 18 • SQLite • Holt-Winters • K-Means • LLM     │
│ REPOSITORY      : github.com/nandithburla/mandi-to-market-supply-chain-optimizer │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 Platform Architecture & Core Workflow

The **Mandi-to-Market Supply Chain Optimizer** is a production-grade analytics platform that unifies agricultural market inflows, statutory MSP compliance, weather shocks, and transit logistics into a single actionable command center.

It couples statistical ML algorithms with a **database-grounded AI Agricultural Assistant** capable of querying live database records to deliver verifiable insights and dynamic charts.

```text
                      ┌──────────────────────────────────────────┐
                      │          Raw Multi-Source Data           │
                      │ Mandi Influx • Prices • Weather • Freight│
                      └────────────────────┬─────────────────────┘
                                           │
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │        Analytical Database & ETL         │
                      │ Cleaned Schema • Moving Averages • SQLite│
                      └────────────────────┬─────────────────────┘
                                           │
                ┌─────────────────┬────────┴────────┬─────────────────┐
                │                 │                 │                 │
                ▼                 ▼                 ▼                 ▼
     ┌─────────────────────┐ ┌──────────┐     ┌──────────┐ ┌────────────────────┐
     │   Trend Forecast    │ │ Anomaly  │     │  Mandi   │ │ 0-100 Risk Index   │
     │  (Holt Smoothing)   │ │ (Z-Score)│     │ Clusters │ │       Engine       │
     └──────────┬──────────┘ └────┬─────┘     └────┬─────┘ └──────────┬─────────┘
                │                 │                │                  │
                └─────────────────┼────────┬───────┴──────────────────┘
                                           │
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │           FastAPI REST Backend           │
                      │   Dashboard APIs  •  Grounded AI Agent   │
                      └────────────────────┬─────────────────────┘
                                           │
                                           ▼
                      ┌──────────────────────────────────────────┐
                      │       React 18 + Plotly Dashboard        │
                      │  Live Visual Analytics & Natural QA Chat │
                      └──────────────────────────────────────────┘
```

---

## 📑 Documentation Index

The complete project technical manual is structured across 10 specialized documents:

| #      | Document                                                                                                                                          | Scope & Purpose                                                             |
| :------:| :--------------------------------------------------------------------------------------------------------------------------------------------------| :----------------------------------------------------------------------------|
| **01** | [**`01 — Project Overview`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/01_PROJECT_OVERVIEW.md)       | Vision, problem space, business value, and solution overview                |
| **02** | [**`02 — Project Workflow`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/02_PROJECT_WORKFLOW.md)       | Complete end-to-end data, ML, AI, and deployment lifecycle                  |
| **03** | [**`03 — Project Structure`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/03_PROJECT_STRUCTURE.md)     | Comprehensive directory map, component breakdown, and file guide            |
| **04** | [**`04 — Setup & Local Run`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/04_SETUP_AND_LOCAL_RUN.md)   | Step-by-step local environment setup, virtual environments, and testing     |
| **05** | [**`05 — Architecture`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/05_ARCHITECTURE.md)               | In-depth technical architecture, EC2 gateway, and EKS pod routing           |
| **06** | [**`06 — Methodology`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/06_METHODOLOGY.md)                 | Mathematical formulation of Holt Forecasting, IQR, Z-Score, and Risk Index  |
| **07** | [**`07 — Data Dictionary`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/07_DATA_DICTIONARY.md)         | Complete schema definitions for all database tables, columns, and SQL views |
| **08** | [**`08 — AWS Deployment`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/08_AWS_DEPLOYMENT.md)           | Complete AWS infrastructure guide: EKS, ECR, NodePort, and EC2 Gateway      |
| **09** | [**`09 — GitHub Actions`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/09_GITHUB_ACTIONS.md)           | CI/CD automation pipeline with passwordless AWS IAM OIDC security           |
| **10** | [**`10 — Errors & Solutions`**](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer/blob/main/docs/10_ERRORS_AND_SOLUTIONS.md) | Troubleshooting handbook for deployment, Kubernetes, CORS, and Docker       |

---

## ◈ Core Capabilities Matrix

| Domain | What the Platform Delivers | Real-World Impact |
| :--- | :--- | :--- |
| **🌾 Mandi Inflow** | Real-time tracking of daily crop arrivals, state-level distribution, and volume spikes. | Preempts market saturation and manages physical yard capacity. |
| **💰 Price & MSP** | Modal price tracking against statutory Minimum Support Price (MSP) benchmarks. | Immediately flags distressed sales and price-manipulation patterns. |
| **🌦️ Climate Shock** | Precipitation and temperature overlay against arrival and supply disruptions. | Correlates heavy rainfall with transit delays and arrival drops. |
| **🚚 Transit & Freight** | Origin-to-mandi travel times, transit bottlenecks, and warehouse holding delays. | Reduces post-harvest spoilage and transit turnaround times. |
| **🛡️ Risk Index** | Composite **0–100 Mandi Risk Score** combining volatility, MSP deficit, and weather. | Prioritizes operational interventions across high-risk corridors. |
| **🤖 Grounded AI** | Natural language Q&A engine with deterministic SQL tool execution. | Gives non-technical traders and officers instant access to SQL insights. |

---

## 🤖 The AI Agricultural Assistant: Zero-Hallucination Architecture

Unlike traditional conversational LLMs that fabricate numbers, this assistant uses **deterministic database tool-calling**. The language model only formulates the query logic, while all answers are computed directly from the verified database.

> [!NOTE]  
> **How It Works Under the Hood**  
> When a user asks *"Which mandis have wheat prices 10% below MSP?"*, the agent selects the specialized `prices_tool`, generates a parameterized SQL query, evaluates the dataset, and returns both an English summary and a structured JSON payload for instant Plotly chart rendering.

```text
 User Question ───► [ Intent & Entity Parser ]
                           │
                           ▼
                [ Tool Routing Engine ]
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   arrivals_tool      prices_tool       weather_tool
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
             [ SQLite (mandi_market.db) ]
                           │
                           ▼
             [ Grounded Synthesis Engine ]
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ▼                                   ▼
  Natural Text Response              Interactive Chart Payload
```

### Specialized Query Tools:
* `arrivals_tool` ◈ Analyzes commodity volume surges and historical arrival trends.
* `prices_tool` ◈ Evaluates modal price spreads and calculates statutory MSP deltas.
* `weather_tool` ◈ Queries precipitation, heat indices, and storm impact metrics.
* `transport_tool` ◈ Computes route travel variances and warehouse holding delays.
* `db_tool` ◈ Read-only SQL executor for complex multi-table analytical joins.

### ⚡ Sample API Request & Grounded Response

```bash
# Query the live AI Agent endpoint
curl -X POST "http://localhost:8000/api/agent/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "Which top 3 mandis have the highest wheat arrivals?"}'
```

```json
{
  "question": "Which top 3 mandis have the highest wheat arrivals?",
  "tool_used": "arrivals_tool",
  "response": "The top 3 mandis by wheat arrivals are Khanna (42,500 MT), Rajpura (36,200 MT), and Sirsa (29,800 MT).",
  "chart_type": "bar",
  "data": [
    {"mandi": "Khanna", "arrivals_mt": 42500},
    {"mandi": "Rajpura", "arrivals_mt": 36200},
    {"mandi": "Sirsa", "arrivals_mt": 29800}
  ]
}
```

---

## 📈 Analytics & Mathematical Formulations

### 1. Short-Term Forecasting (Holt's Linear Exponential Smoothing)
$$
\begin{aligned}
\text{Level Equation:} \quad & \ell_t = \alpha y_t + (1 - \alpha)(\ell_{t-1} + b_{t-1}) \\
\text{Trend Equation:} \quad & b_t = \beta(\ell_t - \ell_{t-1}) + (1 - \beta)b_{t-1} \\
\text{Forecast Equation:} \quad & \hat{y}_{t+h\mid t} = \ell_t + h b_t
\end{aligned}
$$

### 2. Statistical Anomaly Detection
- **Interquartile Range (IQR)**: Outliers flagged when exceeding $[Q_1 - 1.5 \times IQR, \; Q_3 + 1.5 \times IQR]$
- **Rolling Z-Score (7-Day Window)**:
  $$Z_t = \frac{x_t - \mu_{7d}}{\sigma_{7d}} \qquad \text{Flagged if } |Z_t| > 2.5$$

### 3. Composite Mandi Risk Score (0 to 100 Index)
$$\text{Risk Score} = 0.35 \times \text{Volatility} + 0.25 \times (1 - \text{MSP Compliance}) + 0.20 \times \text{Rain Severity} + 0.20 \times \text{Transit Delay}$$

| Risk Tier | Score Range | Operational Meaning | Action Required |
| :--- | :---: | :--- | :--- |
| 🟢 **Stable** | `0 – 35` | Optimal arrivals, prices compliant with MSP, minimal transit delay | Normal operations |
| 🟡 **Monitor** | `36 – 70` | Moderate price deviations or transit delays detected | Watchlist & early alerts |
| 🔴 **Critical** | `71 – 100` | Severe MSP deficit, flash weather shock, or logistics bottleneck | Immediate procurement intervention |

---

## 🏗️ Production Cloud Blueprint (AWS Stockholm `eu-north-1`)

The production deployment addresses cloud VPC constraints through an **EC2 Gateway + Nginx Reverse Proxy** routing directly into **Amazon EKS**:

```text
                        PUBLIC INTERNET
                               │
                               ▼
                   Elastic IP: 51.20.97.243
                               │
                ┌──────────────┴──────────────┐
                │    Amazon EC2 (t3.micro)    │
                │  Nginx Reverse Proxy (:80)  │
                └──────────────┬──────────────┘
                               │
                               │ Forwarding to NodePort :31324
                               ▼
                ┌─────────────────────────────┐
                │  Amazon EKS Managed Nodes   │
                │                             │
                │   ┌─────────────────────┐   │
                │   │ Pod 1 (FastAPI+SPA) │   │
                │   └─────────────────────┘   │
                │   ┌─────────────────────┐   │
                │   │ Pod 2 (FastAPI+SPA) │   │
                │   └─────────────────────┘   │
                └──────────────┬──────────────┘
                               │
                               ▼
                   SQLite Analytical Database
```

### Infrastructure Specs:
- **EKS Cluster**: `mandi-agent-cluster` (Kubernetes 1.28+)
- **Container Registry**: Amazon ECR (`mandi-to-market-optimizer`)
- **Service Type**: Kubernetes `NodePort` on Port `31324`
- **Gateway**: Ubuntu 22.04 on `t3.micro` with permanent Elastic IP `51.20.97.243`
- **CI/CD Security**: GitHub Actions with **AWS IAM OpenID Connect (OIDC)** — zero static access keys stored in repository secrets.

---

## 📊 Dashboard Modules

The user interface is broken into 8 purpose-built modules:

```text
[01] Executive Overview       ───► Macro KPIs, high-risk flags, active market yards
[02] Arrivals & Mandis        ───► Inflow tonnage, spatial distribution, peak windows
[03] Price & MSP Monitor      ───► Modal price trends, statutory MSP breach radar
[04] Weather Dynamics         ───► Precipitation alerts, climate-inflow correlations
[05] Transport & Logistics    ───► Freight corridors, transit bottlenecks, warehouse turnaround
[06] Supply Chain Risk & ML   ───► 0-100 Risk heatmap, Holt forecasts, anomaly scatter plots
[07] AI Agricultural Assistant───► Natural language conversation, grounded queries & dynamic charts
[08] System & Pipeline Health ───► ETL status, DB query latency, pod runtime metrics
```

---

## 🗄️ Database Architecture (`mandi_market.db`)

```text
TABLES                                  ANALYTICAL VIEWS
├── msp (Statutory MSP rates)           ├── vw_daily_arrivals (Aggregated inflow)
├── mandis (Master yard directory)      ├── vw_daily_prices (Weighted modal rates)
├── arrivals_clean (Daily inflow logs)  ├── vw_msp_comparison (Real-time MSP delta)
├── prices_clean (Modal/Min/Max rates)  ├── vw_mandi_performance (Volume & risk rollup)
├── weather_clean (Precip/Temp logs)    └── vw_weather_arrival_relationship
├── transport_clean (Freight delays)
└── arrivals_features & price_features
```

---

## ⚡ Quickstart & Local Setup

### 1. Clone & Prepare
```bash
git clone https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer.git
cd mandi-to-market-supply-chain-optimizer
```

### 2. 🔑 Environment Configuration (`.env`)
Create a `.env` file in the root directory (or pass via environment variables):

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OPENROUTER_API_KEY` | *(Required for AI)* | API key for OpenRouter LLM query processing |
| `DATABASE_URL` | `sqlite:///data/processed/mandi_market.db` | Path to the SQLite analytical database |
| `PORT` | `8000` | Backend API server listening port |

### 3. Backend (FastAPI)
```bash
# Set up Python virtual environment
python -m venv .venv
# Activate: Windows -> .venv\Scripts\Activate.ps1 | Linux/macOS -> source .venv/bin/activate
pip install -r requirements.txt

# Start backend server (Runs on port 8000)
python run_server.py
```
> Swagger documentation available at `http://localhost:8000/docs`

### 4. Frontend (React 18 + Vite)
```bash
cd frontend
npm install
npm run dev
```
> UI accessible at `http://localhost:5173`

### 5. Running with Docker (Optional)
```bash
docker build -t mandi-optimizer:latest .
docker run -p 8000:8000 mandi-optimizer:latest
```

---

## 🌐 Public Deployment

The production platform is live and publicly accessible:
**[http://51.20.97.243](http://51.20.97.243)**

```text
Track      : AgriTech — Mandi-to-Market Supply Chain Optimization
Repository : https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer
Status     : Production Ready • AWS EKS Deployed
```
