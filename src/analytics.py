"""
Advanced analytics layer (Gate 4).

Implements simple, explainable models first:
  - Arrival & price forecasting via Exponential Smoothing (falls back
    to a linear trend if there isn't enough history for the chosen
    seasonal period).
  - Arrival / price anomaly detection via IQR and rolling z-score.
  - Mandi clustering via K-Means on a small set of interpretable
    aggregate features.

Every function answers a specific business question rather than being
included for decoration (see docstrings).
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Forecasting - "What will arrivals/prices look like next week?"
# ---------------------------------------------------------------------------
def forecast_series(daily_series: pd.Series, periods: int = 14) -> pd.DataFrame:
    """Forecast the next `periods` values of a daily time series.

    Uses Holt's Exponential Smoothing (additive trend, no seasonality
    by default - agricultural arrival data over a few months rarely
    has enough cycles to fit a reliable seasonal component). Falls
    back to a naive linear-trend extrapolation if there are fewer than
    10 historical points.

    Returns a DataFrame with columns: date, forecast, is_forecast.
    """
    series = daily_series.dropna().sort_index()
    # Reindex to a continuous daily calendar (filling gaps with 0) so
    # statsmodels has a well-defined frequency to forecast from - agri
    # arrival/price data legitimately has "no activity" days that are
    # not missing data, just zero volume for that Mandi/crop.
    if len(series) > 1:
        full_index = pd.date_range(series.index.min(), series.index.max(), freq="D")
        series = series.reindex(full_index, fill_value=0)
        series.index.freq = "D"

    if len(series) < 10:
        logger.warning("Not enough history (%s points) for smoothing; using linear trend.", len(series))
        x = np.arange(len(series))
        if len(series) >= 2:
            slope, intercept = np.polyfit(x, series.values, 1)
        else:
            slope, intercept = 0.0, series.mean() if len(series) else 0.0
        future_x = np.arange(len(series), len(series) + periods)
        forecast_vals = slope * future_x + intercept
    else:
        model = ExponentialSmoothing(series, trend="add", seasonal=None, initialization_method="estimated")
        fit = model.fit(optimized=True)
        forecast_vals = fit.forecast(periods).values

    forecast_vals = np.clip(forecast_vals, a_min=0, a_max=None)  # arrivals/prices cannot be negative
    last_date = series.index.max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods, freq="D")
    forecast_df = pd.DataFrame({"date": future_dates, "forecast": forecast_vals, "is_forecast": True})
    history_df = pd.DataFrame({"date": series.index, "forecast": series.values, "is_forecast": False})
    return pd.concat([history_df, forecast_df], ignore_index=True)


def forecast_arrivals(arrivals_features: pd.DataFrame, crop: Optional[str] = None,
                       mandi_id: Optional[str] = None, periods: int = 14) -> pd.DataFrame:
    """Business question: 'How many Quintals of a crop are expected to
    arrive over the next N days at this Mandi?' Aggregates filtered
    arrivals to a daily total and forecasts forward."""
    df = arrivals_features.copy()
    if crop:
        df = df[df["crop"] == crop]
    if mandi_id:
        df = df[df["mandi_id"] == mandi_id]
    daily = df.groupby("arrival_date")["quantity_quintal"].sum().sort_index()
    return forecast_series(daily, periods=periods)


def forecast_price(price_features: pd.DataFrame, crop: Optional[str] = None,
                    mandi_id: Optional[str] = None, periods: int = 14) -> pd.DataFrame:
    """Business question: 'Where is the modal price for this crop headed?'"""
    df = price_features.copy()
    if crop:
        df = df[df["crop"] == crop]
    if mandi_id:
        df = df[df["mandi_id"] == mandi_id]
    daily = df.groupby("price_date")["modal_price"].mean().sort_index()
    return forecast_series(daily, periods=periods)


# ---------------------------------------------------------------------------
# Anomaly detection - "Which days/Mandis look unusual and need attention?"
# ---------------------------------------------------------------------------
def detect_anomalies_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    """Flag values outside [Q1 - k*IQR, Q3 + k*IQR]. Returns a boolean mask."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)


def detect_anomalies_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Flag values whose rolling z-score exceeds `threshold` (7-day window)."""
    rolling_mean = series.rolling(window=7, min_periods=3).mean()
    rolling_std = series.rolling(window=7, min_periods=3).std().replace(0, np.nan)
    z = (series - rolling_mean) / rolling_std
    return z.abs() > threshold


def detect_arrival_anomalies(arrivals_features: pd.DataFrame) -> pd.DataFrame:
    """Business question: 'Which arrival days spiked or crashed
    unexpectedly?' Returns the daily arrivals series with both IQR and
    rolling-z-score anomaly flags attached, per crop.
    """
    daily = (
        arrivals_features.groupby(["crop", "arrival_date"])["quantity_quintal"]
        .sum().reset_index().sort_values(["crop", "arrival_date"])
    )
    results = []
    for crop, grp in daily.groupby("crop"):
        grp = grp.set_index("arrival_date").sort_index()
        grp["iqr_anomaly"] = detect_anomalies_iqr(grp["quantity_quintal"])
        grp["zscore_anomaly"] = detect_anomalies_zscore(grp["quantity_quintal"])
        grp["crop"] = crop
        results.append(grp.reset_index())
    return pd.concat(results, ignore_index=True) if results else daily


def detect_price_anomalies(price_features: pd.DataFrame) -> pd.DataFrame:
    """Business question: 'Which price observations look like crashes or spikes?'"""
    daily = (
        price_features.groupby(["crop", "price_date"])["modal_price"]
        .mean().reset_index().sort_values(["crop", "price_date"])
    )
    results = []
    for crop, grp in daily.groupby("crop"):
        grp = grp.set_index("price_date").sort_index()
        grp["iqr_anomaly"] = detect_anomalies_iqr(grp["modal_price"])
        grp["zscore_anomaly"] = detect_anomalies_zscore(grp["modal_price"])
        grp["crop"] = crop
        results.append(grp.reset_index())
    return pd.concat(results, ignore_index=True) if results else daily


# ---------------------------------------------------------------------------
# Clustering - "Which Mandis behave similarly and could share a supply
# chain / risk-mitigation strategy?"
# ---------------------------------------------------------------------------
def cluster_mandis(arrivals_features: pd.DataFrame, price_features: pd.DataFrame,
                    n_clusters: int = 4) -> pd.DataFrame:
    """K-Means clustering of Mandis using interpretable aggregate
    features: total arrival volume, arrival volatility, average modal
    price, and average MSP gap %.

    Returns one row per Mandi with its assigned cluster label.
    """
    arr_agg = arrivals_features.groupby("mandi_id")["quantity_quintal"].agg(["sum", "std"]).rename(
        columns={"sum": "total_arrivals", "std": "arrival_volatility"})
    price_agg = price_features.groupby("mandi_id").agg(
        avg_modal_price=("modal_price", "mean"),
        avg_msp_gap_pct=("msp_gap_pct", "mean"),
    )
    features = arr_agg.join(price_agg, how="inner").dropna()

    if len(features) < n_clusters:
        logger.warning("Not enough Mandis (%s) for %s clusters; skipping clustering.", len(features), n_clusters)
        features["cluster"] = 0
        return features.reset_index()

    scaled = StandardScaler().fit_transform(features)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    features["cluster"] = model.fit_predict(scaled)
    return features.reset_index()
