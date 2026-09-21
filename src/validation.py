"""
Validation layer.

Runs AFTER cleaning/standardization to confirm the cleaned data is
internally consistent (foreign keys resolve, values in expected
ranges, no leftover unparseable dates) before it is loaded into the
analytical database.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def validate_referential_integrity(child: pd.DataFrame, child_key: str,
                                    parent: pd.DataFrame, parent_key: str,
                                    child_name: str = "child", parent_name: str = "parent") -> dict:
    """Check what fraction of child_key values exist in parent_key."""
    parent_keys = set(parent[parent_key].dropna())
    child_keys = child[child_key]
    matched = child_keys.isin(parent_keys)
    result = {
        "child_dataset": child_name,
        "parent_dataset": parent_name,
        "total_child_rows": len(child),
        "matched_rows": int(matched.sum()),
        "unmatched_rows": int((~matched).sum()),
        "match_rate_pct": round(matched.mean() * 100, 2) if len(child) else 0.0,
    }
    logger.info("Referential check %s.%s -> %s.%s: %.2f%% matched",
                child_name, child_key, parent_name, parent_key, result["match_rate_pct"])
    return result


def validate_date_column(df: pd.DataFrame, date_col: str, name: str = "dataset") -> dict:
    """Report how many dates remain invalid (NaT) after cleaning."""
    invalid = int(df[date_col].isna().sum())
    result = {"dataset": name, "column": date_col, "invalid_dates_remaining": invalid, "total_rows": len(df)}
    logger.info("%s.%s: %s invalid dates remaining out of %s", name, date_col, invalid, len(df))
    return result


def validate_value_ranges(df: pd.DataFrame, col: str, min_val=None, max_val=None, name: str = "dataset") -> dict:
    """Report rows that fall outside an expected numeric range (not dropped, just flagged)."""
    series = pd.to_numeric(df[col], errors="coerce")
    out_of_range = pd.Series(False, index=df.index)
    if min_val is not None:
        out_of_range |= series < min_val
    if max_val is not None:
        out_of_range |= series > max_val
    result = {
        "dataset": name,
        "column": col,
        "out_of_range_count": int(out_of_range.sum()),
        "total_rows": len(df),
    }
    return result


def validate_no_negative(df: pd.DataFrame, col: str, name: str = "dataset") -> dict:
    """Confirm a quantity column has no remaining negative values post-cleaning."""
    series = pd.to_numeric(df[col], errors="coerce")
    negatives = int((series < 0).sum())
    result = {"dataset": name, "column": col, "remaining_negative_count": negatives}
    if negatives:
        logger.warning("%s.%s still has %s negative values after cleaning", name, col, negatives)
    return result


def run_all_validations(cleaned: dict) -> list:
    """Run the standard validation suite across the cleaned dataset dict.

    `cleaned` is expected to have keys: mandi_master, arrivals, prices,
    msp, weather, transport (all already-cleaned DataFrames).
    """
    checks = []

    checks.append(validate_referential_integrity(
        cleaned["arrivals"], "mandi_id", cleaned["mandi_master"], "mandi_id",
        "arrivals", "mandi_master"))
    checks.append(validate_referential_integrity(
        cleaned["transport"], "mandi_id", cleaned["mandi_master"], "mandi_id",
        "transport", "mandi_master"))

    checks.append(validate_date_column(cleaned["arrivals"], "arrival_date", "arrivals"))
    checks.append(validate_date_column(cleaned["prices"], "price_date", "prices"))

    checks.append(validate_no_negative(cleaned["arrivals"], "arrival_quantity", "arrivals"))
    checks.append(validate_no_negative(cleaned["weather"], "rainfall_mm", "weather"))
    checks.append(validate_no_negative(cleaned["transport"], "transit_hours_clean", "transport"))

    checks.append(validate_value_ranges(cleaned["weather"], "temperature_c", -10, 55, "weather"))
    checks.append(validate_value_ranges(cleaned["weather"], "humidity_percent", 0, 100, "weather"))

    return checks
