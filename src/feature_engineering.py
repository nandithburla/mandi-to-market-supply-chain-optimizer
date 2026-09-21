"""
Feature engineering layer.

Builds the analytical (denormalized-for-analysis) feature tables that
sit on top of the cleaned relational tables: arrivals enriched with
Mandi geography, price enriched with MSP gap metrics, and a daily
weather aggregate usable for correlation analysis.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def build_arrivals_features(arrivals: pd.DataFrame, mandi_master: pd.DataFrame) -> pd.DataFrame:
    """Join arrivals to Mandi master data (district/state) and drop rows
    with unusable core fields (no mandi, no crop, no valid date, or
    negative/zero quantity) from the ANALYTICAL table only - the
    cleaned raw table on disk is left untouched for auditability.
    """
    merged = arrivals.merge(
        mandi_master[["mandi_id", "mandi_name", "district", "state"]],
        on="mandi_id", how="left",
    )
    usable = (
        merged["crop"].notna()
        & merged["arrival_date"].notna()
        & merged["quantity_quintal"].notna()
        & (merged["quantity_quintal"] > 0)
    )
    logger.info("arrivals_features: %s/%s rows usable for analytics", usable.sum(), len(merged))
    return merged.loc[usable].reset_index(drop=True)


def build_price_features(prices: pd.DataFrame) -> pd.DataFrame:
    """Filter to usable price rows. MSP gap metrics were already computed
    per-row in cleaning.clean_prices()."""
    usable = prices["modal_price"].notna() & prices["price_date"].notna()
    logger.info("price_features: %s/%s rows usable for analytics", usable.sum(), len(prices))
    return prices.loc[usable].reset_index(drop=True)


def build_weather_daily(weather: pd.DataFrame) -> pd.DataFrame:
    """Aggregate cleaned weather readings to one row per calendar date
    (Asia/Kolkata) for correlation with arrivals/prices.
    """
    out = weather.copy()
    out["date"] = out["timestamp_ist"].dt.date
    daily = (
        out.dropna(subset=["date"])
        .groupby("date")
        .agg(
            avg_temperature_c=("temperature_c", "mean"),
            total_rainfall_mm=("rainfall_mm", "sum"),
            avg_humidity_pct=("humidity_percent", "mean"),
            sensor_reading_count=("sensor_id", "count"),
        )
        .reset_index()
    )
    daily["date"] = pd.to_datetime(daily["date"])
    return daily


def build_market_value(arrivals_features: pd.DataFrame, price_features: pd.DataFrame) -> pd.DataFrame:
    """Estimate market value of arrivals by joining same-day, same-Mandi,
    same-crop modal price onto arrival volume.

    Estimated Market Value = Quantity (Quintal) x Modal Price (per Quintal)

    Where no matching price exists for that exact (mandi, crop, date)
    combination, the value is left as NaN rather than guessed - the
    dashboard reports the matched coverage % transparently.
    """
    price_key = price_features[["mandi_id", "crop", "price_date", "modal_price", "msp_per_quintal", "msp_gap", "msp_gap_pct", "below_msp"]].rename(
        columns={"price_date": "arrival_date"}
    )
    merged = arrivals_features.merge(price_key, on=["mandi_id", "crop", "arrival_date"], how="left")
    merged["estimated_market_value"] = merged["quantity_quintal"] * merged["modal_price"]
    match_rate = merged["modal_price"].notna().mean() * 100
    logger.info("market_value: price match rate = %.2f%%", match_rate)
    return merged
