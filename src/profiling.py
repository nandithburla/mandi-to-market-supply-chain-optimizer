"""
Data profiling utilities.

Used BEFORE cleaning to understand missingness, duplicates and raw row
counts so that every cleaning decision documented in
docs/methodology.md is backed by an actual measurement rather than a
guess.
"""

import logging
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def profile_missingness(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-column missing-value count + percentage table."""
    total = len(df)
    missing = df.isna().sum()
    # also treat common "soft nulls" as missing for profiling purposes
    soft_null_tokens = {"NA", "N/A", "null", "NULL", "", "UNKNOWN", "unknown"}
    soft_missing = df.apply(lambda col: col.astype(str).isin(soft_null_tokens).sum())
    combined = missing.add(soft_missing, fill_value=0)
    pct = (combined / total * 100).round(2) if total else combined
    return pd.DataFrame({
        "missing_count": combined.astype(int),
        "missing_pct": pct,
    }).sort_values("missing_pct", ascending=False)


def profile_duplicates(df: pd.DataFrame, subset=None) -> Dict[str, int]:
    """Return exact-duplicate and (optional) business-key duplicate counts."""
    exact_dupes = int(df.duplicated().sum())
    key_dupes = int(df.duplicated(subset=subset).sum()) if subset else None
    return {"exact_duplicates": exact_dupes, "business_key_duplicates": key_dupes}


def profile_dataset(name: str, df: pd.DataFrame, dedupe_subset=None) -> dict:
    """Build a single profiling summary block for one raw dataset."""
    summary = {
        "dataset": name,
        "raw_row_count": len(df),
        "columns": list(df.columns),
        "missingness": profile_missingness(df).to_dict(orient="index"),
        "duplicates": profile_duplicates(df, subset=dedupe_subset),
    }
    logger.info("Profiled %s: %s raw rows, %s exact duplicates",
                name, summary["raw_row_count"], summary["duplicates"]["exact_duplicates"])
    return summary
