# Project Overview

## Mandi-to-Market Supply Chain Optimizer

The Mandi-to-Market Supply Chain Optimizer is an AgriTech platform designed to analyze mandi and supply-chain data and provide useful insights for agricultural decision-making.

## Problem

Mandi and supply-chain data can come from multiple sources and may contain inconsistent formats, missing values, different units, and information related to arrivals, prices, weather, and transportation.

The project processes this data into a structured database and provides analytics through a web application.

## Solution

The system combines:

- Data cleaning and processing
- SQLite database
- Analytical features and KPIs
- Price and MSP comparison
- Arrival analysis
- Weather analysis
- Transport analysis
- Mandi risk analysis
- AI Agricultural Assistant
- Interactive React dashboard

## Main Components

### 1. Data Layer

Raw agricultural datasets are processed and stored in:

```text
data/processed/mandi_market.db

The database contains cleaned data, analytical features, and database views.

2. Analytics Layer
The project performs analytical operations such as:


Arrival analysis

Price and MSP comparison

Weather analysis

Transport analysis

Forecasting

Anomaly detection

Mandi clustering

Risk scoring
3. AI Agent
The AI Agricultural Assistant allows users to ask questions in natural language.
Basic flow:

User Question
      ↓
AI Agent
      ↓
Intent Understanding
      ↓
Database Tool
      ↓
SQL Query
      ↓
Database Result
      ↓
AI Response

The agent uses the available database tools to retrieve relevant information before generating the response.

4. Backend
The backend is built with FastAPI.
It provides REST APIs for:

/api/health
/api/overview
/api/arrivals
/api/prices
/api/agent/query

5. Frontend
The frontend is built using:


React

Vite

Tailwind CSS
It provides pages for the main project analytics and the AI Agricultural Assistant.

6. Deployment
The application is containerized using Docker and deployed on AWS.
Production architecture:

React Frontend
      ↓
FastAPI Backend
      ↓
Docker Container
      ↓
Amazon ECR
      ↓
Amazon EKS
      ↓
EC2 + Nginx
      ↓
Public Application

Technology Stack
AreaTechnologyFrontendReact, Vite, Tailwind CSSBackendFastAPIProgrammingPythonDatabaseSQLiteAIOpenRouterContainerizationDockerCloudAWSKubernetesAmazon EKSRegistryAmazon ECRCI/CDGitHub ActionsReverse ProxyNginx
Project Goal
The main goal is to provide a single platform where mandi, price, weather, transport, and supply-chain information can be analyzed through dashboards and natural-language AI queries.