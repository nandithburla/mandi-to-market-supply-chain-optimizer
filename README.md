# 🌾 Mandi-to-Market Supply Chain Optimizer

An end-to-end AgriTech platform that helps analyze mandi arrivals, crop prices, MSP, weather, transportation and supply-chain risks.

The platform combines data analytics with a custom AI Agricultural Assistant so users can ask questions about the mandi and supply-chain data using normal language.

---

## 🚀 Key Features

- Mandi arrivals analysis
- Crop price and MSP comparison
- Weather and supply analysis
- Transportation and warehouse delay analysis
- Supply-chain risk analysis
- Short-term forecasting
- Anomaly detection
- Mandi clustering
- AI Agricultural Assistant
- Interactive charts and dashboards
- React frontend
- FastAPI backend
- SQLite analytical database
- Docker containerization
- Amazon ECR and Amazon EKS deployment
- EC2 + Nginx public gateway
- GitHub Actions CI/CD

---

## 🏗️ Technology Stack

### Frontend
- React
- Vite
- Tailwind CSS
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn

### Data & Analytics
- Pandas
- NumPy
- Scikit-learn
- SQLite
- Holt Exponential Smoothing
- IQR / Rolling Z-score anomaly detection
- K-Means clustering
- Plotly

### AI
- Custom Python AI Agent
- OpenRouter API
- Natural-language query understanding
- Database tools
- Grounded responses
- Dynamic chart generation

### Deployment & DevOps
- Docker
- Amazon ECR
- Amazon EKS
- Kubernetes
- Amazon EC2
- Nginx
- GitHub Actions
- GitHub OIDC

---

## 🧠 System Architecture

```text
                         INTERNET
                            │
                            ▼
                  Elastic IP: 51.20.97.243
                            │
                            ▼
                    EC2 Gateway Server
                       Nginx :80
                            │
                            ▼
                    EKS NodePort :31324
                            │
                            ▼
                 Kubernetes Deployment
                       ┌────┴────┐
                       ▼         ▼
                     Pod 1     Pod 2
                       │         │
                       └────┬────┘
                            ▼
                     FastAPI + React
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Analytics      AI Agent       SQLite

🔄 Complete Project Flow
Raw Datasets
     ↓
Data Cleaning & Transformation
     ↓
SQLite Database
     ↓
Feature Engineering & Analytical Views
     ↓
Analytics
 ┌───┼────────────┬────────────┐
 ▼   ▼            ▼            ▼
Forecasting   Anomaly      Clustering   Risk Score
              Detection
     ↓
FastAPI Backend
 ┌───────────────┬────────────────┐
 ▼               ▼
Dashboard APIs   AI Agent API
     ↓               ↓
     └───────┬───────┘
             ▼
       React Frontend
             ↓
       User Dashboard

🤖 AI Agricultural Assistant
The AI Assistant allows users to ask questions in normal language.
Example:

Which mandis have the highest wheat arrivals?


The flow is:

User Question
      ↓
React Assistant
      ↓
FastAPI /api/agent/query
      ↓
AI Agent
      ↓
Question Understanding
      ↓
Tool Selection
      ↓
SQLite Query
      ↓
Database Result
      ↓
AI Final Answer
      ↓
Text + Chart Data
      ↓
React Dashboard

The agent contains tools for:


Arrivals

Prices

Weather

Transport

Database access
📊 Dashboard Modules
The application contains:


Executive Overview & Mandi Intelligence

Price & MSP Monitor

Weather Dynamics & Supply Dynamics

Logistics Corridors & Warehouse Transit Delays

Supply Chain Risk

AI Agricultural Assistant

Settings
🗄️ Database
The main database is:

data/processed/mandi_market.db


Important tables include:

msp
mandis
arrivals_clean
prices_clean
msp_reference
weather_clean
transport_clean
arrivals_features
price_features
weather_daily
market_value

Important analytical views include:

vw_daily_arrivals
vw_daily_prices
vw_msp_comparison
vw_mandi_performance
vw_weather_arrival_relationship

📈 Analytics
The project includes:

Forecasting
Holt Exponential Smoothing is used for short-term forecasting.

Anomaly Detection
IQR and rolling Z-score methods are used to detect unusual values.

Clustering
K-Means is used to group mandis based on their characteristics.

Risk Scoring
Supply-chain indicators are combined into a 0–100 mandi risk score.
📁 Project Documentation
Detailed documentation is separated into different files:

Project Overview
Project Workflow
Project Structure
Local Setup & Run
AWS Deployment
GitHub Actions CI/CD
Errors & Solutions
☁️ Deployment Architecture
The final deployment uses:

GitHub Repository
       ↓
GitHub Actions
       ↓
GitHub OIDC
       ↓
AWS IAM Role
       ↓
Amazon ECR
       ↓
Amazon EKS
       ↓
Kubernetes Pods
       ↓
NodePort 31324
       ↓
EC2 Gateway
       ↓
Nginx
       ↓
Elastic IP
       ↓
Public Application

AWS Resources
Region

eu-north-1


ECR Repository

mandi-to-market-optimizer


EKS Cluster

mandi-agent-cluster


Kubernetes Deployment

mandi-to-market-optimizer


Kubernetes Container

mandi-to-market-app


NodePort

31324


Public IP

51.20.97.243


🔁 GitHub Actions CI/CD
Every push to the main branch triggers the deployment workflow.

git push
   ↓
GitHub Actions
   ↓
AWS OIDC Authentication
   ↓
Amazon ECR Login
   ↓
Docker Build
   ↓
Docker Push
   ↓
Update EKS kubeconfig
   ↓
Update Kubernetes Image
   ↓
Kubernetes Rollout

The Docker image is tagged using the GitHub commit SHA.
GitHub repository secrets used:

AWS_GITHUB_ACTIONS_ROLE_ARN
ECR_REGISTRY

No long-lived AWS access keys are used by GitHub Actions.
🌐 Public Application
The deployed application is available at:
[http://51.20.97.243](http://51.20.97.243)
📚 Documentation
For complete information about how the project was built and deployed, see:


Project workflow

Project structure

Local setup

AWS deployment

GitHub Actions

Errors and solutions
The detailed documentation is available inside the docs/ folder.....