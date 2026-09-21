"""Tests for the post-cleaning validation layer."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import validation


def test_referential_integrity_full_match():
    child = pd.DataFrame({"mandi_id": ["MANDI001", "MANDI002"]})
    parent = pd.DataFrame({"mandi_id": ["MANDI001", "MANDI002", "MANDI003"]})
    result = validation.validate_referential_integrity(child, "mandi_id", parent, "mandi_id")
    assert result["match_rate_pct"] == 100.0
    assert result["unmatched_rows"] == 0


def test_referential_integrity_partial_match():
    child = pd.DataFrame({"mandi_id": ["MANDI001", "MANDI999"]})
    parent = pd.DataFrame({"mandi_id": ["MANDI001"]})
    result = validation.validate_referential_integrity(child, "mandi_id", parent, "mandi_id")
    assert result["match_rate_pct"] == 50.0
    assert result["unmatched_rows"] == 1


def test_validate_date_column_counts_invalid():
    df = pd.DataFrame({"d": [pd.Timestamp("2026-01-01"), pd.NaT, pd.NaT]})
    result = validation.validate_date_column(df, "d")
    assert result["invalid_dates_remaining"] == 2
    assert result["total_rows"] == 3


def test_validate_no_negative_detects_negatives():
    df = pd.DataFrame({"qty": [10, -5, 3]})
    result = validation.validate_no_negative(df, "qty")
    assert result["remaining_negative_count"] == 1


def test_validate_value_ranges_flags_out_of_range():
    df = pd.DataFrame({"temp": [10, 60, -20, 25]})
    result = validation.validate_value_ranges(df, "temp", min_val=-10, max_val=55)
    assert result["out_of_range_count"] == 2
