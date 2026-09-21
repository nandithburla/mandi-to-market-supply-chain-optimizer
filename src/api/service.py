"""
Data Service layer for FastAPI backend.
Queries data/processed/mandi_market.db and uses analytics / KPI modules
to compute real-time metrics with zero fabricated data.
"""

import sqlite3
import numpy as np
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path

from src import config, analytics
from dashboard import kpis
from agent.agent import ask_agent

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_table(table_name: str) -> pd.DataFrame:
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()
    for col in df.columns:
        if col.endswith("_date") or col == "date":
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

class MarketService:
    def __init__(self):
        self._cached_tables = {}

    def _get_tables(self) -> Dict[str, pd.DataFrame]:
        # Load tables on demand
        required = ["mandis", "arrivals_features", "price_features", "weather_daily", "market_value", "transport_clean"]
        for t in required:
            if t not in self._cached_tables:
                self._cached_tables[t] = load_table(t)
        return self._cached_tables

    def reload(self):
        self._cached_tables.clear()

    def get_filter_options(self) -> Dict[str, Any]:
        tables = self._get_tables()
        mandis_df = tables["mandis"]
        arrivals_df = tables["arrivals_features"]

        states = sorted(mandis_df["state"].dropna().unique().tolist())
        districts = sorted(mandis_df["district"].dropna().unique().tolist())
        
        mandi_list = (
            mandis_df[["mandi_id", "mandi_name", "state", "district"]]
            .dropna(subset=["mandi_id"])
            .fillna("")
            .sort_values("mandi_name")
            .to_dict(orient="records")
        )

        crops = sorted(arrivals_df["crop"].dropna().unique().tolist())
        min_date = arrivals_df["arrival_date"].min()
        max_date = arrivals_df["arrival_date"].max()

        return {
            "states": states,
            "districts": districts,
            "mandis": mandi_list,
            "crops": crops,
            "date_range": {
                "min": str(min_date.date()) if pd.notna(min_date) else "2026-01-01",
                "max": str(max_date.date()) if pd.notna(max_date) else "2026-12-31"
            }
        }

    def _filter_dfs(
        self,
        states: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        mandis: Optional[List[str]] = None,
        crops: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        tables = self._get_tables()
        mandis_df = tables["mandis"]
        arrivals_df = tables["arrivals_features"].copy()
        prices_df = tables["price_features"].copy()
        market_val_df = tables["market_value"].copy()
        weather_df = tables["weather_daily"].copy()

        # Resolve mandi list from states / districts / mandis
        valid_mandis = mandis_df.copy()
        if states:
            valid_mandis = valid_mandis[valid_mandis["state"].isin(states)]
        if districts:
            valid_mandis = valid_mandis[valid_mandis["district"].isin(districts)]
        if mandis:
            valid_mandis = valid_mandis[valid_mandis["mandi_id"].isin(mandis)]
        
        valid_mandi_ids = set(valid_mandis["mandi_id"].unique())

        if valid_mandi_ids:
            arrivals_df = arrivals_df[arrivals_df["mandi_id"].isin(valid_mandi_ids)]
            prices_df = prices_df[prices_df["mandi_id"].isin(valid_mandi_ids)]
            market_val_df = market_val_df[market_val_df["mandi_id"].isin(valid_mandi_ids)]

        if crops:
            arrivals_df = arrivals_df[arrivals_df["crop"].isin(crops)]
            prices_df = prices_df[prices_df["crop"].isin(crops)]
            market_val_df = market_val_df[market_val_df["crop"].isin(crops)]

        if start_date:
            s_dt = pd.to_datetime(start_date)
            arrivals_df = arrivals_df[arrivals_df["arrival_date"] >= s_dt]
            prices_df = prices_df[prices_df["price_date"] >= s_dt]
            market_val_df = market_val_df[market_val_df["arrival_date"] >= s_dt]

        if end_date:
            e_dt = pd.to_datetime(end_date)
            arrivals_df = arrivals_df[arrivals_df["arrival_date"] <= e_dt]
            prices_df = prices_df[prices_df["price_date"] <= e_dt]
            market_val_df = market_val_df[market_val_df["arrival_date"] <= e_dt]

        return arrivals_df, prices_df, market_val_df, weather_df, valid_mandis

    def get_overview(
        self,
        states: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        mandis: Optional[List[str]] = None,
        crops: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        arr_f, price_f, mv_f, weather_df, _ = self._filter_dfs(
            states, districts, mandis, crops, start_date, end_date
        )

        risk_df = kpis.compute_mandi_risk_scores(price_f, arr_f, weather_df)
        avg_risk = float(risk_df["risk_score"].mean()) if not risk_df.empty and pd.notna(risk_df["risk_score"].mean()) else None

        tot_arr = kpis.total_arrivals_quintal(arr_f)
        tot_mv = kpis.total_market_value(mv_f)
        avg_price = kpis.avg_modal_price(price_f)
        pct_below = kpis.pct_below_msp(price_f)

        # 1. Daily Arrivals Trend
        daily_arr = (
            arr_f.groupby("arrival_date")["quantity_quintal"]
            .sum()
            .reset_index()
            .sort_values("arrival_date")
        )
        daily_arrivals_trend = [
            {"date": str(row["arrival_date"].date()), "arrivals": round(float(row["quantity_quintal"]), 2)}
            for _, row in daily_arr.iterrows()
        ]

        # 2. Daily Price vs MSP Trend
        valid_prices = price_f.dropna(subset=["msp_per_quintal"])
        daily_prices = (
            valid_prices.groupby("price_date")
            .agg(modal_price=("modal_price", "mean"), msp=("msp_per_quintal", "mean"))
            .reset_index()
            .sort_values("price_date")
        )
        price_vs_msp_trend = [
            {
                "date": str(row["price_date"].date()),
                "modal_price": round(float(row["modal_price"]), 2),
                "msp": round(float(row["msp"]), 2),
            }
            for _, row in daily_prices.iterrows()
        ]

        # 3. Top Mandis by Arrivals
        top_mandis_agg = (
            arr_f.groupby("mandi_name")["quantity_quintal"]
            .sum()
            .reset_index()
            .sort_values("quantity_quintal", ascending=False)
            .head(10)
        )
        top_mandis = [
            {"mandi_name": str(row["mandi_name"]), "arrivals": round(float(row["quantity_quintal"]), 2)}
            for _, row in top_mandis_agg.iterrows()
        ]

        # 4. Crop Distribution
        crop_agg = (
            arr_f.groupby("crop")["quantity_quintal"]
            .sum()
            .reset_index()
            .sort_values("quantity_quintal", ascending=False)
        )
        total_vol = crop_agg["quantity_quintal"].sum() or 1.0
        crop_distribution = [
            {
                "crop": str(row["crop"]),
                "arrivals": round(float(row["quantity_quintal"]), 2),
                "percentage": round(float(row["quantity_quintal"]) / total_vol * 100, 1),
            }
            for _, row in crop_agg.iterrows()
        ]

        return {
            "kpis": {
                "total_arrivals_quintal": round(tot_arr, 2),
                "total_market_value": round(tot_mv, 2),
                "avg_modal_price": round(avg_price, 2) if pd.notna(avg_price) else None,
                "pct_below_msp": round(pct_below, 1) if pd.notna(pct_below) else None,
                "avg_risk_score": round(avg_risk, 1) if avg_risk is not None else None,
                "active_mandis": kpis.active_mandi_count(arr_f),
                "active_crops": kpis.active_crop_count(arr_f),
            },
            "daily_arrivals_trend": daily_arrivals_trend,
            "price_vs_msp_trend": price_vs_msp_trend,
            "top_mandis": top_mandis,
            "crop_distribution": crop_distribution,
        }

    def get_arrivals_data(
        self,
        states: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        mandis: Optional[List[str]] = None,
        crops: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        arr_f, price_f, mv_f, weather_df, _ = self._filter_dfs(
            states, districts, mandis, crops, start_date, end_date
        )

        tot_arr = kpis.total_arrivals_quintal(arr_f)
        growth_rate = kpis.arrival_growth_rate(arr_f)
        active_mandi_cnt = kpis.active_mandi_count(arr_f)
        active_crop_cnt = kpis.active_crop_count(arr_f)

        # Mandi Summary Table
        mandi_summary = (
            arr_f.groupby(["mandi_id", "mandi_name", "district", "state"])
            .agg(
                total_arrivals=("quantity_quintal", "sum"),
                active_days=("arrival_date", "nunique"),
                farmer_count=("farmer_count", "sum"),
            )
            .reset_index()
        )
        
        price_summary = (
            price_f.groupby("mandi_id")
            .agg(
                avg_modal_price=("modal_price", "mean"),
                avg_msp_gap_pct=("msp_gap_pct", "mean"),
                price_volatility=("modal_price", "std"),
            )
            .reset_index()
        )

        risk_df = kpis.compute_mandi_risk_scores(price_f, arr_f, weather_df)
        
        merged_table = mandi_summary.merge(price_summary, on="mandi_id", how="left")
        if not risk_df.empty:
            merged_table = merged_table.merge(
                risk_df[["mandi_id", "risk_score", "risk_category"]],
                on="mandi_id",
                how="left"
            )
        else:
            merged_table["risk_score"] = None
            merged_table["risk_category"] = "Unknown"

        mandi_table = []
        for _, r in merged_table.sort_values("total_arrivals", ascending=False).iterrows():
            mandi_table.append({
                "mandi_id": str(r["mandi_id"]),
                "mandi_name": str(r["mandi_name"]),
                "district": str(r["district"]),
                "state": str(r["state"]),
                "total_arrivals": round(float(r["total_arrivals"]), 2),
                "active_days": int(r["active_days"]),
                "avg_daily_arrivals": round(float(r["total_arrivals"]) / max(1, int(r["active_days"])), 2),
                "farmer_count": int(r["farmer_count"]) if pd.notna(r["farmer_count"]) else 0,
                "avg_modal_price": round(float(r["avg_modal_price"]), 2) if pd.notna(r["avg_modal_price"]) else None,
                "avg_msp_gap_pct": round(float(r["avg_msp_gap_pct"]), 1) if pd.notna(r["avg_msp_gap_pct"]) else None,
                "price_volatility": round(float(r["price_volatility"]), 2) if pd.notna(r["price_volatility"]) else None,
                "risk_score": round(float(r["risk_score"]), 1) if pd.notna(r["risk_score"]) else None,
                "risk_category": str(r["risk_category"]) if pd.notna(r["risk_category"]) else "Unknown",
            })

        # Crop-wise arrival breakdown
        crop_agg = (
            arr_f.groupby("crop")
            .agg(
                total_arrivals=("quantity_quintal", "sum"),
                mandi_count=("mandi_id", "nunique"),
                records=("quantity_quintal", "count"),
            )
            .reset_index()
            .sort_values("total_arrivals", ascending=False)
        )
        total_qtl = crop_agg["total_arrivals"].sum() or 1.0
        crop_breakdown = [
            {
                "crop": str(r["crop"]),
                "total_arrivals": round(float(r["total_arrivals"]), 2),
                "mandi_count": int(r["mandi_count"]),
                "percentage": round(float(r["total_arrivals"]) / total_qtl * 100, 1),
            }
            for _, r in crop_agg.iterrows()
        ]

        # Top 15 Mandis
        top_15_mandis = mandi_table[:15]

        # Pivot daily arrivals by crop for stacked charts
        daily_crop = (
            arr_f.groupby(["arrival_date", "crop"])["quantity_quintal"]
            .sum()
            .unstack(fill_value=0)
            .reset_index()
            .sort_values("arrival_date")
        )
        daily_crop_timeline = []
        for _, r in daily_crop.iterrows():
            item = {"date": str(r["arrival_date"].date())}
            for c in daily_crop.columns:
                if c != "arrival_date":
                    item[str(c)] = round(float(r[c]), 2)
            daily_crop_timeline.append(item)

        return {
            "kpis": {
                "total_arrivals_quintal": round(tot_arr, 2),
                "growth_rate_pct": round(growth_rate, 1) if pd.notna(growth_rate) else None,
                "active_mandis": active_mandi_cnt,
                "active_crops": active_crop_cnt,
            },
            "top_mandis": top_15_mandis,
            "crop_breakdown": crop_breakdown,
            "daily_crop_timeline": daily_crop_timeline,
            "mandi_table": mandi_table,
        }

    def get_prices_data(
        self,
        states: Optional[List[str]] = None,
        districts: Optional[List[str]] = None,
        mandis: Optional[List[str]] = None,
        crops: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        arr_f, price_f, mv_f, _, _ = self._filter_dfs(
            states, districts, mandis, crops, start_date, end_date
        )

        avg_price = kpis.avg_modal_price(price_f)
        avg_msp = kpis.avg_msp(price_f)
        avg_gap = kpis.avg_msp_gap(price_f)
        avg_gap_pct = kpis.avg_msp_gap_pct(price_f)
        pct_below = kpis.pct_below_msp(price_f)

        # 1. Price vs MSP timeline
        valid_prices = price_f.dropna(subset=["msp_per_quintal"])
        daily_prices = (
            valid_prices.groupby("price_date")
            .agg(
                modal_price=("modal_price", "mean"),
                msp=("msp_per_quintal", "mean"),
                min_price=("min_price", "mean"),
                max_price=("max_price", "mean"),
            )
            .reset_index()
            .sort_values("price_date")
        )
        timeline = [
            {
                "date": str(r["price_date"].date()),
                "modal_price": round(float(r["modal_price"]), 2),
                "msp": round(float(r["msp"]), 2),
                "min_price": round(float(r["min_price"]), 2) if pd.notna(r["min_price"]) else None,
                "max_price": round(float(r["max_price"]), 2) if pd.notna(r["max_price"]) else None,
            }
            for _, r in daily_prices.iterrows()
        ]

        # 2. MSP Gap by Crop
        crop_gap = (
            valid_prices.groupby("crop")
            .agg(
                avg_modal_price=("modal_price", "mean"),
                avg_msp=("msp_per_quintal", "mean"),
                avg_gap=("msp_gap", "mean"),
                avg_gap_pct=("msp_gap_pct", "mean"),
                below_msp_pct=("below_msp", lambda x: float(x.mean() * 100)),
                sample_count=("modal_price", "count"),
            )
            .reset_index()
            .sort_values("avg_gap_pct")
        )
        msp_gap_by_crop = [
            {
                "crop": str(r["crop"]),
                "avg_modal_price": round(float(r["avg_modal_price"]), 2),
                "avg_msp": round(float(r["avg_msp"]), 2),
                "avg_gap": round(float(r["avg_gap"]), 2),
                "avg_gap_pct": round(float(r["avg_gap_pct"]), 1),
                "below_msp_pct": round(float(r["below_msp_pct"]), 1),
                "sample_count": int(r["sample_count"]),
            }
            for _, r in crop_gap.iterrows()
        ]

        # 3. Top Mandis Below MSP
        mandi_below = (
            valid_prices.groupby("mandi_id")
            .agg(
                below_msp_pct=("below_msp", lambda x: float(x.mean() * 100)),
                avg_modal_price=("modal_price", "mean"),
                avg_msp=("msp_per_quintal", "mean"),
                avg_gap=("msp_gap", "mean"),
                sample_count=("modal_price", "count"),
            )
            .reset_index()
            .sort_values("below_msp_pct", ascending=False)
            .head(15)
        )
        
        # Attach mandi names
        mandis_master = self._get_tables()["mandis"]
        mandi_below = mandi_below.merge(mandis_master[["mandi_id", "mandi_name", "state"]], on="mandi_id", how="left")
        mandis_below_msp = [
            {
                "mandi_id": str(r["mandi_id"]),
                "mandi_name": str(r.get("mandi_name") or r["mandi_id"]),
                "state": str(r.get("state") or "Unknown"),
                "below_msp_pct": round(float(r["below_msp_pct"]), 1),
                "avg_modal_price": round(float(r["avg_modal_price"]), 2),
                "avg_msp": round(float(r["avg_msp"]), 2),
                "avg_gap": round(float(r["avg_gap"]), 2),
                "sample_count": int(r["sample_count"]),
            }
            for _, r in mandi_below.iterrows()
        ]

        return {
            "kpis": {
                "avg_modal_price": round(avg_price, 2) if pd.notna(avg_price) else None,
                "avg_msp": round(avg_msp, 2) if pd.notna(avg_msp) else None,
                "avg_msp_gap": round(avg_gap, 2) if pd.notna(avg_gap) else None,
                "avg_msp_gap_pct": round(avg_gap_pct, 1) if pd.notna(avg_gap_pct) else None,
                "pct_below_msp": round(pct_below, 1) if pd.notna(pct_below) else None,
            },
            "timeline": timeline,
            "msp_gap_by_crop": msp_gap_by_crop,
            "mandis_below_msp": mandis_below_msp,
        }

    def get_weather_data(self) -> Dict[str, Any]:
        tables = self._get_tables()
        weather_daily = tables["weather_daily"]
        arrivals_f = tables["arrivals_features"]
        price_f = tables["price_features"]

        # KPIs
        avg_temp = float(weather_daily["avg_temperature_c"].mean()) if not weather_daily.empty else None
        tot_rain = float(weather_daily["total_rainfall_mm"].sum()) if not weather_daily.empty else None
        avg_humidity = float(weather_daily["avg_humidity_pct"].mean()) if not weather_daily.empty else None
        total_readings = int(weather_daily["sensor_reading_count"].sum()) if not weather_daily.empty else 0

        # Daily arrivals for merging
        daily_arr = (
            arrivals_f.groupby("arrival_date")["quantity_quintal"]
            .sum()
            .reset_index()
            .rename(columns={"arrival_date": "date", "quantity_quintal": "total_quantity_quintal"})
        )
        daily_price = (
            price_f.groupby("price_date")["modal_price"]
            .mean()
            .reset_index()
            .rename(columns={"price_date": "date", "modal_price": "avg_modal_price"})
        )

        merged = weather_daily.merge(daily_arr, on="date", how="inner").merge(daily_price, on="date", how="left")

        # Correlations
        corr_rain = float(merged["total_rainfall_mm"].corr(merged["total_quantity_quintal"])) if not merged.empty else None
        corr_temp = float(merged["avg_temperature_c"].corr(merged["total_quantity_quintal"])) if not merged.empty else None
        corr_hum = float(merged["avg_humidity_pct"].corr(merged["total_quantity_quintal"])) if not merged.empty else None

        daily_weather_trend = [
            {
                "date": str(r["date"].date()),
                "avg_temperature_c": round(float(r["avg_temperature_c"]), 1) if pd.notna(r["avg_temperature_c"]) else None,
                "total_rainfall_mm": round(float(r["total_rainfall_mm"]), 1) if pd.notna(r["total_rainfall_mm"]) else None,
                "avg_humidity_pct": round(float(r["avg_humidity_pct"]), 1) if pd.notna(r["avg_humidity_pct"]) else None,
                "arrivals": round(float(r["total_quantity_quintal"]), 2) if pd.notna(r.get("total_quantity_quintal")) else None,
                "modal_price": round(float(r["avg_modal_price"]), 2) if pd.notna(r.get("avg_modal_price")) else None,
            }
            for _, r in merged.sort_values("date").iterrows()
        ]

        return {
            "kpis": {
                "avg_temperature_c": round(avg_temp, 1) if avg_temp is not None else None,
                "total_rainfall_mm": round(tot_rain, 1) if tot_rain is not None else None,
                "avg_humidity_pct": round(avg_humidity, 1) if avg_humidity is not None else None,
                "sensor_reading_count": total_readings,
            },
            "correlations": {
                "rainfall_vs_arrivals": round(corr_rain, 2) if pd.notna(corr_rain) else None,
                "temperature_vs_arrivals": round(corr_temp, 2) if pd.notna(corr_temp) else None,
                "humidity_vs_arrivals": round(corr_hum, 2) if pd.notna(corr_hum) else None,
            },
            "daily_trend": daily_weather_trend,
        }

    def get_risk_analytics(self, crop: Optional[str] = None) -> Dict[str, Any]:
        tables = self._get_tables()
        arrivals_f = tables["arrivals_features"]
        price_f = tables["price_features"]
        weather_daily = tables["weather_daily"]
        mandis_master = tables["mandis"]

        # 1. Mandi Risk Scores
        risk_df = kpis.compute_mandi_risk_scores(price_f, arrivals_f, weather_daily)
        risk_df = risk_df.merge(mandis_master[["mandi_id", "mandi_name", "state", "district"]], on="mandi_id", how="left")

        risk_rankings = [
            {
                "mandi_id": str(r["mandi_id"]),
                "mandi_name": str(r.get("mandi_name") or r["mandi_id"]),
                "district": str(r.get("district") or ""),
                "state": str(r.get("state") or ""),
                "risk_score": round(float(r["risk_score"]), 1),
                "risk_category": str(r["risk_category"]),
                "msp_pressure_score": round(float(r["msp_pressure_score"]), 1),
                "price_volatility_score": round(float(r["price_volatility_score"]), 1),
                "arrival_anomaly_score": round(float(r["arrival_anomaly_score"]), 1),
                "weather_anomaly_score": round(float(r["weather_anomaly_score"]), 1),
            }
            for _, r in risk_df.sort_values("risk_score", ascending=False).iterrows()
        ]

        # Category Counts
        category_counts = {
            "Low": int((risk_df["risk_category"] == "Low").sum()),
            "Medium": int((risk_df["risk_category"] == "Medium").sum()),
            "High": int((risk_df["risk_category"] == "High").sum()),
            "Critical": int((risk_df["risk_category"] == "Critical").sum()),
        }

        # 2. Anomalies
        available_crops = sorted(arrivals_f["crop"].dropna().unique().tolist())
        selected_crop = crop if crop in available_crops else (available_crops[0] if available_crops else None)

        arrival_anom_df = analytics.detect_arrival_anomalies(arrivals_f)
        price_anom_df = analytics.detect_price_anomalies(price_f)

        arrival_anomalies = []
        if selected_crop and not arrival_anom_df.empty:
            sub = arrival_anom_df[arrival_anom_df["crop"] == selected_crop].sort_values("arrival_date")
            arrival_anomalies = [
                {
                    "date": str(r["arrival_date"].date()),
                    "quantity": round(float(r["quantity_quintal"]), 2),
                    "is_anomaly": bool(r["iqr_anomaly"]),
                    "zscore_anomaly": bool(r["zscore_anomaly"]),
                    "crop": selected_crop,
                }
                for _, r in sub.iterrows()
            ]

        price_anomalies = []
        if selected_crop and not price_anom_df.empty:
            sub2 = price_anom_df[price_anom_df["crop"] == selected_crop].sort_values("price_date")
            price_anomalies = [
                {
                    "date": str(r["price_date"].date()),
                    "modal_price": round(float(r["modal_price"]), 2),
                    "is_anomaly": bool(r["iqr_anomaly"]),
                    "zscore_anomaly": bool(r["zscore_anomaly"]),
                    "crop": selected_crop,
                }
                for _, r in sub2.iterrows()
            ]

        # 3. 14-Day Forecasting
        arrival_forecast = []
        price_forecast = []
        if selected_crop:
            fc_arr = analytics.forecast_arrivals(arrivals_f, crop=selected_crop, periods=14)
            arrival_forecast = [
                {
                    "date": str(r["date"].date()),
                    "value": round(float(r["forecast"]), 2),
                    "is_forecast": bool(r["is_forecast"]),
                }
                for _, r in fc_arr.iterrows()
            ]

            fc_price = analytics.forecast_price(price_f, crop=selected_crop, periods=14)
            price_forecast = [
                {
                    "date": str(r["date"].date()),
                    "value": round(float(r["forecast"]), 2),
                    "is_forecast": bool(r["is_forecast"]),
                }
                for _, r in fc_price.iterrows()
            ]

        # 4. K-Means Mandi Clustering
        cluster_df = analytics.cluster_mandis(arrivals_f, price_f, n_clusters=4)
        cluster_df = cluster_df.merge(mandis_master[["mandi_id", "mandi_name", "state"]], on="mandi_id", how="left")
        clusters = [
            {
                "mandi_id": str(r["mandi_id"]),
                "mandi_name": str(r.get("mandi_name") or r["mandi_id"]),
                "state": str(r.get("state") or ""),
                "total_arrivals": round(float(r["total_arrivals"]), 2),
                "avg_modal_price": round(float(r["avg_modal_price"]), 2),
                "cluster": int(r["cluster"]),
            }
            for _, r in cluster_df.iterrows()
        ]

        return {
            "risk_weights": config.RISK_WEIGHTS,
            "risk_rankings": risk_rankings,
            "category_counts": category_counts,
            "selected_crop": selected_crop,
            "available_crops": available_crops,
            "arrival_anomalies": arrival_anomalies,
            "price_anomalies": price_anomalies,
            "arrival_forecast": arrival_forecast,
            "price_forecast": price_forecast,
            "clusters": clusters,
        }

    def get_transport_data(self) -> Dict[str, Any]:
        tables = self._get_tables()
        transport_df = tables["transport_clean"]

        valid_trips = transport_df[transport_df["transit_time_invalid"] == 0]

        total_trips = len(valid_trips)
        avg_transit = float(valid_trips["transit_hours_clean"].mean()) if not valid_trips.empty else None
        tot_distance = float(valid_trips["distance_km"].sum()) if not valid_trips.empty else None
        active_warehouses = int(valid_trips["destination_warehouse"].nunique()) if not valid_trips.empty else 0

        # Warehouse Delays Aggregation
        wh_agg = (
            valid_trips.groupby("destination_warehouse")
            .agg(
                avg_transit_hours=("transit_hours_clean", "mean"),
                total_trips=("trip_id", "count"),
                avg_distance_km=("distance_km", "mean"),
            )
            .reset_index()
            .sort_values("avg_transit_hours", ascending=False)
        )
        warehouse_delays = [
            {
                "warehouse": str(r["destination_warehouse"]),
                "avg_transit_hours": round(float(r["avg_transit_hours"]), 2),
                "total_trips": int(r["total_trips"]),
                "avg_distance_km": round(float(r["avg_distance_km"]), 1) if pd.notna(r["avg_distance_km"]) else None,
            }
            for _, r in wh_agg.iterrows()
        ]

        # Top Mandi -> Warehouse logistics routes
        route_agg = (
            valid_trips.groupby(["mandi_id", "destination_warehouse"])
            .agg(
                avg_transit_hours=("transit_hours_clean", "mean"),
                total_trips=("trip_id", "count"),
                avg_distance_km=("distance_km", "mean"),
            )
            .reset_index()
            .sort_values("avg_transit_hours", ascending=False)
            .head(15)
        )
        mandis_master = tables["mandis"]
        route_agg = route_agg.merge(mandis_master[["mandi_id", "mandi_name"]], on="mandi_id", how="left")
        routes = [
            {
                "mandi_id": str(r["mandi_id"]),
                "mandi_name": str(r.get("mandi_name") or r["mandi_id"]),
                "warehouse": str(r["destination_warehouse"]),
                "avg_transit_hours": round(float(r["avg_transit_hours"]), 2),
                "total_trips": int(r["total_trips"]),
                "avg_distance_km": round(float(r["avg_distance_km"]), 1) if pd.notna(r["avg_distance_km"]) else None,
            }
            for _, r in route_agg.iterrows()
        ]

        return {
            "kpis": {
                "total_trips": total_trips,
                "avg_transit_hours": round(avg_transit, 2) if avg_transit is not None else None,
                "total_distance_km": round(tot_distance, 1) if tot_distance is not None else None,
                "active_warehouses": active_warehouses,
            },
            "warehouse_delays": warehouse_delays,
            "routes": routes,
        }

    def process_ai_query(self, query: str) -> Dict[str, Any]:
        """Directly delegates to the existing custom Python agent."""
        return ask_agent(query)

market_service = MarketService()
