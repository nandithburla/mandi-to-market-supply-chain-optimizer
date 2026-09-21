"""
Unit tests for FastAPI endpoints.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"]["status"] == "healthy"
    assert data["database"]["counts"]["mandis"] == 57


def test_filters_endpoint():
    response = client.get("/api/filters")
    assert response.status_code == 200
    data = response.json()
    assert len(data["states"]) > 0
    assert len(data["crops"]) > 0
    assert len(data["mandis"]) > 0


def test_overview_endpoint():
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert data["kpis"]["active_mandis"] == 57
    assert data["kpis"]["total_arrivals_quintal"] > 0
    assert len(data["daily_arrivals_trend"]) > 0
    assert len(data["top_mandis"]) > 0


def test_arrivals_endpoint():
    response = client.get("/api/arrivals")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert len(data["mandi_table"]) > 0
    assert len(data["crop_breakdown"]) > 0


def test_prices_endpoint():
    response = client.get("/api/prices")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert len(data["msp_gap_by_crop"]) > 0


def test_weather_endpoint():
    response = client.get("/api/weather")
    assert response.status_code == 200
    data = response.json()
    assert "correlations" in data
    assert len(data["daily_trend"]) > 0


def test_risk_endpoint():
    response = client.get("/api/risk")
    assert response.status_code == 200
    data = response.json()
    assert len(data["risk_rankings"]) > 0
    assert "category_counts" in data


def test_transport_endpoint():
    response = client.get("/api/transport")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert len(data["warehouse_delays"]) > 0


def test_agent_query_endpoint():
    response = client.post("/api/agent/query", json={"query": "Which mandis have highest wheat arrivals?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["intent"] in ["arrivals", "prices", "weather", "transport"]
