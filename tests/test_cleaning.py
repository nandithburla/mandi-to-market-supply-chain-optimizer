"""Tests for crop normalization, unit conversion, date parsing, and
duplicate/missing-value handling."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import standardization as std
from src import cleaning


def test_normalize_crop_english_variants():
    assert std.normalize_crop("wheat") == "Wheat"
    assert std.normalize_crop("WHEAT") == "Wheat"
    assert std.normalize_crop("Gehun") == "Wheat"


def test_normalize_crop_hindi_variants():
    assert std.normalize_crop("गेहूँ") == "Wheat"
    assert std.normalize_crop("गेहूं") == "Wheat"
    assert std.normalize_crop("धान") == "Rice"
    assert std.normalize_crop("मक्का") == "Maize"


def test_normalize_crop_handles_missing():
    assert std.normalize_crop(None) is None
    assert std.normalize_crop(float("nan")) is None


def test_normalize_mandi_id_variants():
    assert std.normalize_mandi_id("MANDI001") == "MANDI001"
    assert std.normalize_mandi_id("MANDI-001") == "MANDI001"
    assert std.normalize_mandi_id("mandi_001") == "MANDI001"
    assert std.normalize_mandi_id("M001") == "MANDI001"
    assert std.normalize_mandi_id("056") == "MANDI056"


def test_convert_to_quintal():
    assert std.convert_to_quintal(100, "KG") == 1.0
    assert std.convert_to_quintal(1, "Tonnes") == 10.0
    assert std.convert_to_quintal(5, "Qtl") == 5.0
    assert std.convert_to_quintal(5, None) == 5.0  # default assumption: already Quintal


def test_convert_distance_to_km():
    assert std.convert_distance_to_km(10, "miles") == round(10 * 1.60934, 3)
    assert std.convert_distance_to_km(10, "km") == 10.0


def test_convert_temperature_to_celsius():
    assert std.convert_temperature_to_celsius(32, "F") == 0.0
    assert std.convert_temperature_to_celsius(100, "C") == 100.0


def test_convert_rainfall_to_mm():
    assert std.convert_rainfall_to_mm(1, "in") == 25.4
    assert std.convert_rainfall_to_mm(10, "mm") == 10.0


def test_parse_date_any_multiple_formats():
    assert pd.Timestamp(std.parse_date_any("2026-01-15")) == pd.Timestamp("2026-01-15")
    assert pd.Timestamp(std.parse_date_any("15-01-2026")) == pd.Timestamp("2026-01-15")
    assert pd.Timestamp(std.parse_date_any("01/15/2026")) == pd.Timestamp("2026-01-15")


def test_parse_date_any_unparseable_returns_nat():
    assert pd.isna(std.parse_date_any("not-a-date"))
    assert pd.isna(std.parse_date_any(None))


def test_clean_price_string():
    assert std.clean_price_string("₹1,500.00") == 1500.0
    assert std.clean_price_string("Rs. 2,000") == 2000.0
    assert std.clean_price_string("INR 999.5") == 999.5


def test_clean_arrivals_removes_exact_duplicates():
    df = pd.DataFrame({
        "arrival_id": ["A1", "A1"],
        "date": ["2026-01-01", "2026-01-01"],
        "mandi_id": ["MANDI001", "MANDI001"],
        "crop_name": ["Wheat", "Wheat"],
        "variety": ["Local", "Local"],
        "arrival_quantity": [10.0, 10.0],
        "unit": ["Qtl", "Qtl"],
        "farmer_count": [5, 5],
    })
    cleaned = cleaning.clean_arrivals(df)
    assert len(cleaned) == 1


def test_clean_arrivals_fixes_negative_quantity():
    df = pd.DataFrame({
        "arrival_id": ["A1"], "date": ["2026-01-01"], "mandi_id": ["MANDI001"],
        "crop_name": ["Wheat"], "variety": ["Local"], "arrival_quantity": [-50.0],
        "unit": ["Qtl"], "farmer_count": [5],
    })
    cleaned = cleaning.clean_arrivals(df)
    assert cleaned.loc[0, "arrival_quantity"] == 50.0


def test_clean_mandi_master_dedupes_on_normalized_id():
    df = pd.DataFrame({
        "mandi_id": ["MANDI001", "mandi_001"],
        "mandi_name": ["A", "A"], "district": ["D", "D"], "state": ["S", "S"],
        "mandi_type": ["Private", "private"], "total_area_acres": [10, 10],
    })
    cleaned = cleaning.clean_mandi_master(df)
    assert len(cleaned) == 1
