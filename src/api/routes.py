"""
FastAPI Routes for Mandi-to-Market Supply Chain Optimizer.
"""

from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from src.api.service import market_service
import sqlite3
from src import config

router = APIRouter()

class AgentQueryRequest(BaseModel):
    query: str

@router.get("/health")
def health_check():
    try:
        conn = sqlite3.connect(config.SQLITE_DB_PATH)
        mandi_count = conn.execute("SELECT COUNT(*) FROM mandis").fetchone()[0]
        arrivals_count = conn.execute("SELECT COUNT(*) FROM arrivals_clean").fetchone()[0]
        prices_count = conn.execute("SELECT COUNT(*) FROM prices_clean").fetchone()[0]
        weather_count = conn.execute("SELECT COUNT(*) FROM weather_clean").fetchone()[0]
        transport_count = conn.execute("SELECT COUNT(*) FROM transport_clean").fetchone()[0]
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
        mandi_count = arrivals_count = prices_count = weather_count = transport_count = 0

    return {
        "status": "online",
        "service": "Mandi-to-Market Supply Chain Optimizer API",
        "database": {
            "status": db_status,
            "path": str(config.SQLITE_DB_PATH),
            "counts": {
                "mandis": mandi_count,
                "arrivals": arrivals_count,
                "prices": prices_count,
                "weather_records": weather_count,
                "transport_trips": transport_count,
            }
        }
    }

@router.get("/filters")
def get_filters():
    try:
        return market_service.get_filter_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
def get_overview(
    states: Optional[List[str]] = Query(None),
    districts: Optional[List[str]] = Query(None),
    mandis: Optional[List[str]] = Query(None),
    crops: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    try:
        return market_service.get_overview(
            states=states,
            districts=districts,
            mandis=mandis,
            crops=crops,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/arrivals")
def get_arrivals(
    states: Optional[List[str]] = Query(None),
    districts: Optional[List[str]] = Query(None),
    mandis: Optional[List[str]] = Query(None),
    crops: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    try:
        return market_service.get_arrivals_data(
            states=states,
            districts=districts,
            mandis=mandis,
            crops=crops,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices")
def get_prices(
    states: Optional[List[str]] = Query(None),
    districts: Optional[List[str]] = Query(None),
    mandis: Optional[List[str]] = Query(None),
    crops: Optional[List[str]] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    try:
        return market_service.get_prices_data(
            states=states,
            districts=districts,
            mandis=mandis,
            crops=crops,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather")
def get_weather():
    try:
        return market_service.get_weather_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk")
def get_risk(crop: Optional[str] = Query(None)):
    try:
        return market_service.get_risk_analytics(crop=crop)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transport")
def get_transport():
    try:
        return market_service.get_transport_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/query")
def agent_query(req: AgentQueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        result = market_service.process_ai_query(req.query.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
