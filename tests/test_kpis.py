"""Tests for MSP/KPI/risk-score calculations."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dashboard import kpis


def _sample_prices():
    return pd.DataFrame({
        "mandi_id": ["MANDI001", "MANDI001", "MANDI002"],
        "crop": ["Wheat", "Wheat", "Rice"],
        "modal_price": [1800.0, 2200.0, 3000.0],
        "msp_per_quintal": [2000.0, 2000.0, 2500.0],
        "msp_gap": [-200.0, 200.0, 500.0],
        "msp_gap_pct": [-10.0, 10.0, 20.0],
        "below_msp": [True, False, False],
    })


def _sample_arrivals():
    return pd.DataFrame({
        "mandi_id": ["MANDI001", "MANDI002"],
        "crop": ["Wheat", "Rice"],
        "quantity_quintal": [100.0, 200.0],
        "arrival_date": [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")],
    })


def test_msp_gap_calculation():
    prices = _sample_prices()
    assert kpis.avg_msp_gap(prices) == prices["msp_gap"].mean()


def test_msp_gap_pct_calculation():
    prices = _sample_prices()
    assert round(kpis.avg_msp_gap_pct(prices), 2) == round(prices["msp_gap_pct"].mean(), 2)


def test_pct_below_msp():
    prices = _sample_prices()
    # 1 out of 3 rows is below MSP
    assert round(kpis.pct_below_msp(prices), 2) == round(1 / 3 * 100, 2)


def test_total_arrivals_quintal():
    arrivals = _sample_arrivals()
    assert kpis.total_arrivals_quintal(arrivals) == 300.0


def test_active_mandi_and_crop_counts():
    arrivals = _sample_arrivals()
    assert kpis.active_mandi_count(arrivals) == 2
    assert kpis.active_crop_count(arrivals) == 2


def test_classify_risk_bands():
    assert kpis.classify_risk(10) == "Low"
    assert kpis.classify_risk(45) == "Medium"
    assert kpis.classify_risk(70) == "High"
    assert kpis.classify_risk(95) == "Critical"


def test_risk_weights_sum_to_one():
    from src import config
    assert abs(sum(config.RISK_WEIGHTS.values()) - 1.0) < 1e-9
