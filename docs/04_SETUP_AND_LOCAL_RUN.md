# Setup and Local Run

This document explains how to install and run the project locally.

## 1. Requirements

Install:

- Git
- Python 3.11+
- Node.js and npm
- Docker Desktop
- AWS CLI
- kubectl

## 2. Clone the Project

```powershell
git clone [https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer.git](https://github.com/nandithburla/mandi-to-market-supply-chain-optimizer.git)
cd mandi-to-market-supply-chain-optimizer

3. Backend Setup
Create and activate a Python virtual environment:


python -m venv .venv
.venv\Scripts\Activate.ps1

Install dependencies:


pip install -r requirements.txt


The processed database is located at:

data/processed/mandi_market.db


4. AI Configuration
The AI Assistant uses the OpenRouter API.
Set the API key as an environment variable:


$env:OPENROUTER_API_KEY="YOUR_API_KEY"


Never commit the API key to GitHub.

5. Frontend Setup
Open another terminal:


cd frontendnpm installnpm run dev

6. Start the Backend
From the project root:


python run_server.py


The FastAPI backend provides APIs such as:

/api/health
/api/overview
/api/arrivals
/api/prices
/api/agent/query

The React frontend communicates with these APIs.

7. Local Application Flow
Browser
   ↓
React Frontend
   ↓
FastAPI Backend
   ↓
SQLite Database

For AI queries:

User Question
   ↓
React
   ↓
FastAPI
   ↓
AI Agent
   ↓
Database
   ↓
AI Response

8. Docker
Build the application image:


docker build -t mandi-to-market-optimizer .


Run the container using the port configured by the Dockerfile:


docker run -p 8000:8000 mandi-to-market-optimizer


9. AWS / Kubernetes Verification
Configure AWS:


aws configure


Connect to the EKS cluster:


aws eks update-kubeconfig --region eu-north-1 --name mandi-agent-cluster


Check the cluster:


kubectl get nodes


Check application pods:


kubectl get pods


10. Development Flow
Clone
  ↓
Install Dependencies
  ↓
Run Backend
  ↓
Run Frontend
  ↓
Test
  ↓
Make Changes
  ↓
Git Commit
  ↓
Git Push

Production deployment is handled automatically through GitHub Actions.

