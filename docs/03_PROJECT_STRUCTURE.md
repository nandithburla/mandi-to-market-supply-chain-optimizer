# Project Structure

This document gives a quick overview of the main project folders and files.

```text
mandi-to-market-supply-chain-optimizer/
│
├── agent/
│   ├── agent.py
│   ├── ai_router.py
│   ├── charts.py
│   ├── final_answer.py
│   ├── llm.py
│   ├── prompts.py
│   ├── response.py
│   ├── router.py
│   ├── understanding.py
│   └── tools/
│       ├── arrivals.py
│       ├── db.py
│       ├── prices.py
│       ├── transport.py
│       └── weather.py
│
├── data/
│   └── processed/
│       └── mandi_market.db
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── api/
│       ├── App.jsx
│       └── index.css
│
├── src/
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── service.py
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── secret.yaml
│   └── ingress.yaml
│
├── scripts/
│   └── verify_api.py
│
├── tests/
│   └── test_api.py
│
├── docs/
│
├── Dockerfile
├── requirements.txt
├── run_server.py
├── .gitignore
└── README.md

Main Folders
FolderPurposeagent/AI Agricultural Assistant and database toolsdata/Processed agricultural databasefrontend/React user interfacesrc/api/FastAPI backend and API routesk8s/Kubernetes deployment configurationscripts/Utility and verification scriptstests/Automated testsdocs/Project documentation
AI Agent
The agent/ folder contains the AI assistant.
Important files:

agent.py — main agent flow
understanding.py — interprets user questions
router.py / ai_router.py — routes requests
llm.py — LLM communication
final_answer.py — prepares final responses
charts.py — chart generation
tools/ — database query tools
Backend
The FastAPI backend is mainly organized under:

src/api/


It connects the frontend with the database, analytics, and AI agent.
run_server.py starts the backend application.

Frontend
The React frontend is located in:

frontend/


The main pages include:


Overview

Arrivals

Prices

Weather

Transport

Risk

AI Assistant

Settings
Reusable UI components are stored inside:

frontend/src/components/


Kubernetes
The k8s/ directory contains deployment configuration for AWS EKS.
Important files:

deployment.yaml — application deployment
service.yaml — Kubernetes service
secret.yaml — application secrets
ingress.yaml — ingress configuration
Database
The processed SQLite database is:

data/processed/mandi_market.db


It stores the cleaned datasets and analytical data used by the application.

Documentation
Project documentation is available inside:

docs/


The documentation covers:


Project overview

Workflow

Structure

Local setup

AWS deployment

GitHub Actions

Errors and solutions
Additional technical documentation includes:

architecture.md
data_dictionary.md
methodology.md

Each document focuses on a specific aspect of the project rather than repeating the complete project explanation.