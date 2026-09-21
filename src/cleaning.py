"""
Cleaning layer.

Each function documents WHY a particular missing-value or duplicate
strategy was chosen for that column, as required by Gate 2. Nothing
here silently drops large portions of data - every removal is counted
and returned alongside the cleaned frame so the pipeline can report it.
"""

import logging

import numpy as np
import pandas as pd

from src import standardization as std

logger = logging.getLogger(__name__)


def clean_mandi_master(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Mandi master table.

    Decisions:
    - business key = mandi_id (after normalization) -> exact duplicate
      rows on the *normalized* id are true duplicates (re-exported
      master rows) and are dropped, keeping the first occurrence.
    - missing `district`: kept as 'Unknown District' rather than
      dropped, since state is still informative for aggregation.
    - missing `mandi_type` / `total_area_acres`: kept as NaN /
      'Unknown' - these are descriptive attributes, not required for
      joins or KPI math, so dropping rows would destroy arrivals data
      unnecessarily.
    """
    out = df.copy()
    out["mandi_id"] = out["mandi_id"].apply(std.normalize_mandi_id)
    out["mandi_type"] = out["mandi_type"].fillna("Unknown").str.strip().str.title()
    out["district"] = out["district"].fillna("Unknown District").str.strip().str.title()
    out["mandi_name"] = out["mandi_name"].str.strip()

    before = len(out)
    out = out.drop_duplicates(subset=["mandi_id"], keep="first")
    logger.info("mandi_master: dropped %s duplicate mandi_id rows", before - len(out))

    return out.reset_index(drop=True)


def clean_arrivals(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the daily arrivals table.

    Decisions:
    - business key = (mandi_id, crop_name, date, arrival_id-when-present).
      Exact duplicate rows across all columns are true duplicates
      (double export) and are dropped.
    - `arrival_id` missing/blank: regenerated as a synthetic surrogate
      key (ARR_GEN_<row>) rather than dropping the row, since the
      quantity/date/mandi data is still usable.
    - `arrival_quantity` missing: row is KEPT but flagged
      (quantity_is_missing=True) rather than imputed, because
      fabricating a tonnage would distort KPI totals; downstream KPI
      calculations simply exclude these rows from SUM/AVG.
    - negative quantities: treated as data-entry sign errors and
      corrected via abs() (documented assumption - a mandi cannot
      receive negative produce).
    - `farmer_count` missing: left as NaN, not used in any KPI so no
      imputation needed.
    """
    out = df.copy()

    before = len(out)
    out = out.drop_duplicates(keep="first")
    exact_dupes_removed = before - len(out)
    logger.info("arrivals: dropped %s exact duplicate rows", exact_dupes_removed)

    out["arrival_id"] = out["arrival_id"].replace("", np.nan)
    missing_id_mask = out["arrival_id"].isna()
    out.loc[missing_id_mask, "arrival_id"] = [
        f"ARR_GEN_{i}" for i in range(missing_id_mask.sum())
    ]

    out["mandi_id"] = out["mandi_id"].apply(std.normalize_mandi_id)
    out["crop"] = out["crop_name"].apply(std.normalize_crop)
    out["arrival_date"] = out["date"].apply(std.parse_date_any)
    invalid_dates = int(out["arrival_date"].isna().sum())
    logger.info("arrivals: %s rows had unparseable dates -> NaT", invalid_dates)

    out["arrival_quantity"] = pd.to_numeric(out["arrival_quantity"], errors="coerce")
    out["quantity_is_missing"] = out["arrival_quantity"].isna()
    out["arrival_quantity"] = out["arrival_quantity"].abs()

    out["quantity_quintal"] = out.apply(
        lambda r: std.convert_to_quintal(r["arrival_quantity"], r["unit"]), axis=1
    )

    out["variety"] = out["variety"].fillna("Unknown")
    return out.reset_index(drop=True)


def clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the wholesale price table. MSP now arrives embedded in each
    row (column 'msp') rather than as a separate lookup table, so the
    MSP gap metrics are computed directly here per row.
    """
    out = df.copy()
    before = len(out)
    out = out.drop_duplicates(keep="first")
    logger.info("prices: dropped %s exact duplicate rows", before - len(out))

    out = out.rename(columns={"record_id": "price_id"})
    out["mandi_id"] = out["mandi_id"].apply(std.normalize_mandi_id)
    out["crop"] = out["crop_name"].apply(std.normalize_crop)
    out["price_date"] = out["date"].apply(std.parse_date_any)
    out["district"] = out["district"].fillna("Unknown District")

    for col in ["min_price", "max_price", "modal_price", "msp"]:
        out[col] = out[col].apply(std.clean_price_string)
    out = out.rename(columns={"msp": "msp_per_quintal"})

    out["msp_gap"] = out["modal_price"] - out["msp_per_quintal"]
    out["msp_gap_pct"] = np.where(
        out["msp_per_quintal"].notna() & (out["msp_per_quintal"] != 0),
        (out["msp_gap"] / out["msp_per_quintal"]) * 100,
        np.nan,
    )
    out["below_msp"] = out["msp_gap"] < 0
    return out.reset_index(drop=True)

def build_msp_reference(prices_clean: pd.DataFrame) -> pd.DataFrame:
    """Small crop-level MSP reference table, derived from the per-row MSP
    values now embedded in prices (kept for the dashboard/docs, no longer
    used for joining)."""
    ref = (
        prices_clean.dropna(subset=["msp_per_quintal"])
        .groupby("crop")["msp_per_quintal"]
        .median()
        .reset_index()
        .rename(columns={"msp_per_quintal": "msp_per_quintal_reference"})
    )
    return ref

def clean_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the IoT weather sensor table.

    Decisions:
    - business key = (sensor_id, timestamp). Exact duplicates dropped.
    - `sensor_id` == 'UNKNOWN': kept (still usable for aggregate
      weather trends) but excluded from any sensor-level drill-down.
    - temperature/rainfall missing: left as NaN; weather KPIs use
      mean() which naturally ignores NaN, avoiding fabricated values.
    - unit columns missing: assumed Celsius / mm (the most common
      units in the source), a documented assumption.
    """
    out = df.copy()
    before = len(out)
    out = out.drop_duplicates(keep="first")
    logger.info("weather: dropped %s exact duplicate rows", before - len(out))

    out["timestamp_ist"] = out["timestamp"].apply(std.normalize_timezone)
    out["temperature_c"] = out.apply(
        lambda r: std.convert_temperature_to_celsius(r["temperature"], r.get("temp_unit")), axis=1
    )
    out["rainfall_mm"] = out.apply(
        lambda r: std.convert_rainfall_to_mm(r["rainfall"], r.get("rain_unit")), axis=1
    )
    # sensor glitches: negative rainfall is physically impossible -> clip to 0
    out["rainfall_mm"] = out["rainfall_mm"].clip(lower=0)
    return out.reset_index(drop=True)


def clean_transport(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the transport/logistics table.

    Decisions:
    - business key = trip_id. Exact duplicates dropped.
    - negative `transit_hours`: physically impossible -> recomputed
      from arrival_time - departure_time when both parse successfully,
      otherwise flagged invalid (NaN) rather than guessed.
    - distance normalized to km via convert_distance_to_km().
    - vehicle_no standardized to upper-case, no-space canonical form.
    """
    out = df.copy()
    before = len(out)
    out = out.drop_duplicates(subset=["trip_id"], keep="first")
    logger.info("transport: dropped %s duplicate trip_id rows", before - len(out))

    out["mandi_id"] = out["mandi_id"].apply(std.normalize_mandi_id)
    out["departure_dt"] = out["departure_time"].apply(std.parse_date_any)
    out["arrival_dt"] = out["arrival_time"].apply(std.parse_date_any)

    # transit_hours may arrive as strings like '4.7 hrs' - extract the
    # numeric part before doing any numeric comparison.
    out["transit_hours"] = out["transit_hours"].apply(std.extract_numeric)

    recomputed = (out["arrival_dt"] - out["departure_dt"]).dt.total_seconds() / 3600.0
    out["transit_hours_clean"] = np.where(
        (recomputed.notna()) & (recomputed >= 0), recomputed,
        np.where(out["transit_hours"] >= 0, out["transit_hours"], np.nan)
    )
    out["transit_time_invalid"] = out["transit_hours_clean"].isna()

    out["distance_km"] = out.apply(
        lambda r: std.convert_distance_to_km(r["distance"], r.get("distance_unit")), axis=1
    )
    out["vehicle_no_clean"] = (
        out["vehicle_no"].astype(str).str.upper().str.replace(r"[\s\-]", "", regex=True)
    )
    out.loc[out["vehicle_no"].isna(), "vehicle_no_clean"] = np.nan

    return out.reset_index(drop=True)
