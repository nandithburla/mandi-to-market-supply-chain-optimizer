"""
Core KPI functions for the Mandi-to-Market dashboard.

Every KPI is computed live from whatever (already filtered) DataFrame
is passed in - nothing is hard-coded. Formulas are documented in each
docstring and mirrored in docs/methodology.md.
"""

from typing import Optional

import numpy as np
import pandas as pd

from src import config


def total_arrivals_quintal(arrivals: pd.DataFrame) -> float:
    """Total arrivals in Quintals = SUM(quantity_quintal)."""
    return float(arrivals["quantity_quintal"].sum())


def total_market_value(market_value: pd.DataFrame) -> float:
    """Total estimated market value = SUM(quantity_quintal * modal_price)
    over rows where a matching price record exists."""
    return float(market_value["estimated_market_value"].sum(skipna=True))


def avg_modal_price(prices: pd.DataFrame) -> float:
    """Average modal price across the filtered price records."""
    return float(prices["modal_price"].mean(skipna=True)) if len(prices) else float("nan")


def avg_msp(prices: pd.DataFrame) -> float:
    """Average MSP across the filtered (crop, year) matched price records."""
    return float(prices["msp_per_quintal"].mean(skipna=True)) if len(prices) else float("nan")


def avg_msp_gap(prices: pd.DataFrame) -> float:
    """MSP Gap = Modal Price - MSP (averaged)."""
    return float(prices["msp_gap"].mean(skipna=True)) if len(prices) else float("nan")


def avg_msp_gap_pct(prices: pd.DataFrame) -> float:
    """MSP Gap % = ((Modal Price - MSP) / MSP) x 100 (averaged)."""
    return float(prices["msp_gap_pct"].mean(skipna=True)) if len(prices) else float("nan")


def pct_below_msp(prices: pd.DataFrame) -> float:
    """Percentage of price observations where Modal Price < MSP."""
    valid = prices.dropna(subset=["msp_per_quintal"])
    if len(valid) == 0:
        return float("nan")
    return float(valid["below_msp"].mean() * 100)


def active_mandi_count(arrivals: pd.DataFrame) -> int:
    """Number of distinct Mandis with at least one arrival record."""
    return int(arrivals["mandi_id"].nunique())


def active_crop_count(arrivals: pd.DataFrame) -> int:
    """Number of distinct crops with at least one arrival record."""
    return int(arrivals["crop"].nunique())


def price_volatility(prices: pd.DataFrame, by: Optional[str] = None):
    """Price volatility = standard deviation of modal price.

    If `by` is given (e.g. 'crop' or 'mandi_id'), returns a per-group
    Series; otherwise returns a single float across the filtered data.
    """
    if by:
        return prices.groupby(by)["modal_price"].std()
    return float(prices["modal_price"].std(skipna=True)) if len(prices) else float("nan")


def arrival_growth_rate(arrivals: pd.DataFrame, date_col: str = "arrival_date") -> float:
    """Arrival growth rate = % change in total arrivals between the
    first half and second half of the selected date range.

    Growth Rate % = (Second-half total - First-half total) / First-half total x 100
    """
    if arrivals.empty:
        return float("nan")
    dates = arrivals[date_col]
    mid = dates.min() + (dates.max() - dates.min()) / 2
    first_half = arrivals.loc[dates <= mid, "quantity_quintal"].sum()
    second_half = arrivals.loc[dates > mid, "quantity_quintal"].sum()
    if first_half == 0:
        return float("nan")
    return float((second_half - first_half) / first_half * 100)


# ---------------------------------------------------------------------------
# Mandi Risk Score
# ---------------------------------------------------------------------------
def _minmax_scale(series: pd.Series) -> pd.Series:
    """Scale a series to 0-100. Constant/empty series scale to 0."""
    if series.empty or series.max() == series.min() or series.isna().all():
        return pd.Series(0.0, index=series.index)
    return ((series - series.min()) / (series.max() - series.min()) * 100).fillna(0.0)


def compute_mandi_risk_scores(
    price_features: pd.DataFrame,
    arrivals_features: pd.DataFrame,
    weather_daily: pd.DataFrame,
    weights: Optional[dict] = None,
) -> pd.DataFrame:
    """Compute a transparent 0-100 Mandi Risk Score per Mandi.

    Risk Score = w1*MSP_pressure + w2*price_volatility + w3*arrival_anomaly + w4*weather_anomaly

    - MSP pressure: how often/severely a Mandi's prices fall below MSP
      (mean of max(0, -msp_gap_pct)), min-max scaled to 0-100.
    - Price volatility: std dev of modal price per Mandi, scaled 0-100.
    - Arrival anomaly: coefficient of variation of daily arrivals per
      Mandi (std/mean), scaled 0-100 - a proxy for supply instability.
    - Weather anomaly: national daily rainfall volatility (std of
      total_rainfall_mm) applied uniformly, since sensors are not
      Mandi-specific in this dataset - documented simplification.

    Weights default to config.RISK_WEIGHTS but are fully configurable.
    """
    weights = weights or config.RISK_WEIGHTS

    msp_pressure = (
        price_features.assign(pressure=lambda d: d["msp_gap_pct"].apply(lambda x: max(0, -x) if pd.notna(x) else np.nan))
        .groupby("mandi_id")["pressure"].mean()
    )
    volatility = price_features.groupby("mandi_id")["modal_price"].std()

    arr_stats = arrivals_features.groupby("mandi_id")["quantity_quintal"].agg(["mean", "std"])
    arrival_anomaly = (arr_stats["std"] / arr_stats["mean"]).replace([np.inf, -np.inf], np.nan)

    weather_anomaly_value = 0.0
    if not weather_daily.empty and weather_daily["total_rainfall_mm"].std() is not None:
        weather_anomaly_value = weather_daily["total_rainfall_mm"].std(skipna=True) or 0.0

    mandi_ids = sorted(set(msp_pressure.index) | set(volatility.index) | set(arrival_anomaly.index))
    df = pd.DataFrame(index=mandi_ids)
    df["msp_pressure_raw"] = msp_pressure
    df["price_volatility_raw"] = volatility
    df["arrival_anomaly_raw"] = arrival_anomaly
    df["weather_anomaly_raw"] = weather_anomaly_value

    df["msp_pressure_score"] = _minmax_scale(df["msp_pressure_raw"])
    df["price_volatility_score"] = _minmax_scale(df["price_volatility_raw"])
    df["arrival_anomaly_score"] = _minmax_scale(df["arrival_anomaly_raw"])
    df["weather_anomaly_score"] = _minmax_scale(df["weather_anomaly_raw"])

    df["risk_score"] = (
        weights["msp_pressure"] * df["msp_pressure_score"]
        + weights["price_volatility"] * df["price_volatility_score"]
        + weights["arrival_anomaly"] * df["arrival_anomaly_score"]
        + weights["weather_anomaly"] * df["weather_anomaly_score"]
    ).round(2)

    df["risk_category"] = df["risk_score"].apply(classify_risk)
    df = df.reset_index().rename(columns={"index": "mandi_id"})
    return df


def classify_risk(score: float) -> str:
    """Classify a 0-100 risk score into Low/Medium/High/Critical bands."""
    for category, (low, high) in config.RISK_BANDS.items():
        if low <= score <= high:
            return category
    return "Unknown"
