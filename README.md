# 🌾 Mandi-to-Market Supply Chain Optimizer

An enterprise-grade AgriTech supply chain intelligence and analytics platform designed for State Agriculture Boards to monitor daily crop arrivals across Mandis, track wholesale prices against the government Minimum Support Price (MSP), evaluate IoT weather dynamics, detect logistics bottlenecks, run predictive models, and query data using a natural-language AI Agricultural Assistant.

---

## 🚀 Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, Framer Motion, Lucide React, Recharts
- **Backend API**: FastAPI, Uvicorn, Pydantic, Python 3.11+
- **Data & Storage**: SQLite (`data/processed/mandi_market.db`), pandas, numpy
- **Analytics & ML**: statsmodels (Holt's Exponential Smoothing), scikit-learn (K-Means, StandardScaler)
- **AI Agent**: Custom Native Python AI Agent with OpenRouter LLM NLU and parametric SQLite query tools
- **Testing**: pytest (35 comprehensive unit & API test cases)
- **Deployment**: Multi-stage Docker, Kubernetes (AWS EKS & AWS LoadBalancer ready)

---

## 📁 Project Structure

```
├── agent/                  # Custom Native AI Agent (NLU, router, tools, final answer)
│   └── tools/              # Parametric SQLite query tools (arrivals, prices, weather, transport)
├── data/
│   ├── raw/                # 5 raw synthetic agricultural datasets
│   └── processed/          # SQLite analytical database (mandi_market.db) & cleaned CSVs
├── docs/                   # Data dictionary, methodology, architecture specifications
├── frontend/               # Modern React + Vite + Tailwind CSS dashboard application
│   ├── src/components/     # Sidebar, Header, Global FilterBar, KpiCard, LoadingSkeleton
│   └── src/pages/          # Overview, Arrivals, Prices, Weather, Transport, Risk, Assistant, Settings
├── k8s/                    # Kubernetes manifests (Deployment, Service, Secret, Ingress)
├── notebooks/              # Profiling, cleaning, and analysis Jupyter notebooks
├── sql/                    # Table indexes, analytical views, and reference queries
├── src/
│   ├── api/                # FastAPI application, REST endpoints, and service layer
│   ├── analytics.py        # Forecasting, IQR anomaly detection, Mandi clustering
│   ├── cleaning.py         # Missing-value & duplicate cleaning logic per dataset
│   ├── feature_engineering.py # Enriched features (arrivals_features, price_features, market_value)
│   └── pipeline.py         # End-to-end reproducible ETL pipeline
├── tests/                  # Unit tests (ETL, KPIs, validations, REST API endpoints)
├── Dockerfile              # Multi-stage production container build
├── requirements.txt        # Python dependencies
└── run_server.py           # Unified production server (FastAPI + React SPA)
```

---

## 🏃 Local Quickstart

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.11 & 3.14)
- Node.js 18+ and npm

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
npm run build
cd ..
```

### 3. Run the Application
```bash
# Start unified FastAPI backend + compiled React SPA
python run_server.py
```
Open **`http://localhost:8000`** in your browser.

### 4. Running in Frontend Development Mode (Optional)
If developing the React frontend with Vite Hot Module Reloading (HMR):
```bash
# Terminal 1: Start FastAPI backend
python run_server.py

# Terminal 2: Start Vite Dev Server (with API proxy to :8000)
cd frontend
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 🧪 Testing

Run the test suite across all ETL, KPI, validation, and REST API endpoints:
```bash
python -m pytest tests/
```
Run the automated end-to-end API verification script:
```bash
python scripts/verify_api.py
```

---

## 🐳 Docker Container Deployment

Build and run the production container:
```bash
# Build multi-stage Docker image
docker build -t mandi-to-market-optimizer:latest .

# Run container exposing port 8000
docker run -p 8000:8000 \
  -e OPENROUTER_API_KEY="your_key_here" \
  mandi-to-market-optimizer:latest
```

---

## ☁️ Kubernetes & AWS EKS Deployment

1. **Configure Secret**:
   Update `k8s/secret.yaml` with your `OPENROUTER_API_KEY`.
2. **Apply Manifests**:
   ```bash
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```
3. **Verify Deployment**:
   ```bash
   kubectl get pods -l app=mandi-to-market
   kubectl get svc mandi-to-market-service
   ```

---

## 🤖 AI Assistant Capabilities

The AI Agricultural Assistant communicates with the custom lightweight Python agent (`agent/agent.py`) to execute real parametric SQL queries against `mandi_market.db`.

Example queries supported:
- `"Which mandis have the highest wheat arrivals?"`
- `"Which mandis have wheat prices below MSP?"`
- `"What is the average rainfall and temperature?"`
- `"Show me the transport delays."`
