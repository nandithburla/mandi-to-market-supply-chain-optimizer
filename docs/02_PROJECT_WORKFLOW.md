# Project Workflow

## End-to-End Flow

The Mandi-to-Market Supply Chain Optimizer follows this overall workflow:

```text
Raw Datasets
     ↓
Data Processing
     ↓
SQLite Database
     ↓
Analytics & KPIs
     ↓
FastAPI Backend
     ↓
React Frontend
     ↓
User Dashboard / AI Assistant

1. Data Processing
The project works with agricultural datasets containing information such as:


Mandi arrivals

Prices and MSP

Weather

Transportation

Mandi details
The data is cleaned and transformed before being stored in the SQLite database.

Raw Data
   ↓
Cleaning
   ↓
Transformation
   ↓
Processed Data
   ↓
SQLite

2. Database
The processed data is stored in:

data/processed/mandi_market.db


The database contains cleaned datasets, analytical features, and views used by the application.

3. Analytics
The system calculates useful agricultural and supply-chain insights, including:


Arrival trends

Price vs MSP

Weather relationships

Transport performance

Forecasting

Anomaly detection

Mandi clustering

Risk scores
These results are provided to the frontend through the backend APIs.

4. FastAPI Backend
FastAPI acts as the main connection between the frontend, database, analytics, and AI agent.

React
  ↓
FastAPI
  ↓
Services / Analytics / Agent
  ↓
SQLite

Important APIs include:

/api/health
/api/overview
/api/arrivals
/api/prices
/api/agent/query

5. AI Agricultural Assistant
The AI assistant allows users to ask questions using normal language.
Example:

"Which mandis have the highest wheat arrivals?"


The flow is:

User Question
      ↓
AI Agent
      ↓
Understand Intent
      ↓
Select Database Tool
      ↓
Run SQL Query
      ↓
Retrieve Data
      ↓
Generate Answer
      ↓
Display in React

The agent uses database results to ground its responses.

6. React Frontend
The React application displays:


Overview KPIs

Arrival information

Price analysis

Weather information

Transport information

Risk analysis

AI Assistant
Users interact with the application through the browser.

7. Deployment Flow
The application is packaged as a Docker image.

Code
 ↓
Docker Build
 ↓
Amazon ECR
 ↓
Amazon EKS
 ↓
Kubernetes Pods
 ↓
NodePort
 ↓
EC2 + Nginx
 ↓
Public Application

8. CI/CD Flow
When changes are pushed to the main branch:

git push
   ↓
GitHub Actions
   ↓
AWS OIDC
   ↓
Build Docker Image
   ↓
Push to ECR
   ↓
Update EKS Deployment
   ↓
Kubernetes Rollout

This makes the deployment process automatic.

Complete System
                 USER
                  ↓
            React Frontend
                  ↓
             FastAPI API
             ↙         ↘
       AI Agent       Analytics
          ↓              ↓
       DB Tools       SQLite DB
          ↘              ↙
             Data Results
                  ↓
             User Response

The system therefore connects data processing, analytics, AI-based querying, web visualization, and cloud deployment into one end-to-end platform.