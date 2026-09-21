"""
FastAPI Backend for Mandi-to-Market Supply Chain Optimizer.
Exposes clean RESTful endpoints for the React frontend, integrating
directly with the SQLite database, analytics layer, and custom AI agent.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(
    title="Mandi-to-Market Supply Chain Optimizer API",
    description="AgriTech Intelligence & Supply Chain Optimization Platform API",
    version="2.0.0",
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
