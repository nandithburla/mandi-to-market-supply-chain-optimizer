"""
Plotly chart-builder functions. Kept separate from app.py so pages stay
thin and every chart is independently testable / reusable.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def daily_arrivals_trend(arrivals: pd.DataFrame) -> go.Figure:
    """Line chart: total daily arrivals (Quintals) over time."""
    daily = arrivals.groupby("arrival_date")["quantity_quintal"].sum().reset_index()
    fig = px.line(daily, x="arrival_date", y="quantity_quintal",
                  title="Daily Arrivals Trend (Quintals)",
                  labels={"arrival_date": "Date", "quantity_quintal": "Arrivals (Quintal)"})
    fig.update_traces(line_color="#2E7D32")
    return fig


def price_vs_msp(prices: pd.DataFrame) -> go.Figure:
    """Line chart: average modal price vs average MSP over time."""
    daily = prices.dropna(subset=["msp_per_quintal"]).groupby("price_date").agg(
        modal_price=("modal_price", "mean"), msp=("msp_per_quintal", "mean")
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["price_date"], y=daily["modal_price"], name="Modal Price", line=dict(color="#1565C0")))
    fig.add_trace(go.Scatter(x=daily["price_date"], y=daily["msp"], name="MSP", line=dict(color="#C62828", dash="dash")))
    fig.update_layout(title="Modal Price vs MSP", xaxis_title="Date", yaxis_title="Price (INR / Quintal)")
    return fig


def top_mandis_by_arrivals(arrivals: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart: top Mandis by total arrival volume."""
    agg = arrivals.groupby("mandi_name")["quantity_quintal"].sum().sort_values(ascending=False).head(top_n)
    fig = px.bar(agg.reset_index(), x="quantity_quintal", y="mandi_name", orientation="h",
                 title=f"Top {top_n} Mandis by Arrival Volume",
                 labels={"quantity_quintal": "Arrivals (Quintal)", "mandi_name": "Mandi"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def crop_distribution(arrivals: pd.DataFrame) -> go.Figure:
    """Bar chart: arrival volume share by crop (a bar, not a pie, per
    the no-unnecessary-pie-charts guideline)."""
    agg = arrivals.groupby("crop")["quantity_quintal"].sum().sort_values(ascending=False)
    fig = px.bar(agg.reset_index(), x="crop", y="quantity_quintal",
                 title="Arrival Volume by Crop", labels={"quantity_quintal": "Arrivals (Quintal)", "crop": "Crop"})
    return fig


def msp_gap_by_crop(prices: pd.DataFrame) -> go.Figure:
    """Bar chart: average MSP gap % per crop."""
    agg = prices.dropna(subset=["msp_gap_pct"]).groupby("crop")["msp_gap_pct"].mean().sort_values()
    fig = px.bar(agg.reset_index(), x="crop", y="msp_gap_pct", title="Average MSP Gap % by Crop",
                 labels={"msp_gap_pct": "MSP Gap %", "crop": "Crop"},
                 color="msp_gap_pct", color_continuous_scale=["#C62828", "#2E7D32"])
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    return fig


def below_msp_by_mandi(prices: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar: Mandis with the highest share of below-MSP observations."""
    valid = prices.dropna(subset=["msp_per_quintal"])
    agg = valid.groupby("mandi_id")["below_msp"].mean().mul(100).sort_values(ascending=False).head(top_n)
    fig = px.bar(agg.reset_index(), x="below_msp", y="mandi_id", orientation="h",
                 title=f"Top {top_n} Mandis by % Observations Below MSP",
                 labels={"below_msp": "% Below MSP", "mandi_id": "Mandi"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def weather_scatter(merged: pd.DataFrame, weather_col: str, weather_label: str) -> go.Figure:
    """Scatter plot: a weather variable vs total daily arrivals, with
    a linear trendline to visualize correlation direction/strength."""
    fig = px.scatter(merged, x=weather_col, y="total_quantity_quintal", trendline="ols",
                      title=f"{weather_label} vs Daily Arrivals",
                      labels={weather_col: weather_label, "total_quantity_quintal": "Arrivals (Quintal)"})
    return fig


def weather_price_scatter(merged: pd.DataFrame, weather_col: str, weather_label: str) -> go.Figure:
    """Scatter plot: a weather variable vs average daily modal price."""
    fig = px.scatter(merged, x=weather_col, y="avg_modal_price", trendline="ols",
                      title=f"{weather_label} vs Average Modal Price",
                      labels={weather_col: weather_label, "avg_modal_price": "Avg Modal Price"})
    return fig


def risk_ranking_bar(risk_df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar: Mandi risk ranking, colored by risk category."""
    top = risk_df.sort_values("risk_score", ascending=False).head(top_n)
    fig = px.bar(top, x="risk_score", y="mandi_id", orientation="h", color="risk_category",
                 title=f"Top {top_n} Mandis by Risk Score",
                 color_discrete_map={"Low": "#2E7D32", "Medium": "#F9A825", "High": "#EF6C00", "Critical": "#C62828"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def risk_category_counts(risk_df: pd.DataFrame) -> go.Figure:
    """Bar chart: number of Mandis per risk category."""
    counts = (
        risk_df["risk_category"]
        .value_counts()
        .reindex(["Low", "Medium", "High", "Critical"])
        .fillna(0)
        .rename_axis("risk_category")
        .reset_index(name="count")
    )
    fig = px.bar(counts, x="risk_category", y="count",
                 title="Mandi Count by Risk Category",
                 labels={"risk_category": "Risk Category", "count": "Number of Mandis"},
                 color="risk_category",
                 color_discrete_map={"Low": "#2E7D32", "Medium": "#F9A825", "High": "#EF6C00", "Critical": "#C62828"})
    return fig


def anomaly_timeseries(df: pd.DataFrame, date_col: str, value_col: str, anomaly_col: str, title: str) -> go.Figure:
    """Line chart with anomalous points highlighted as red markers."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[date_col], y=df[value_col], mode="lines", name=value_col, line=dict(color="#1565C0")))
    anomalies = df[df[anomaly_col]]
    fig.add_trace(go.Scatter(x=anomalies[date_col], y=anomalies[value_col], mode="markers",
                              name="Anomaly", marker=dict(color="#C62828", size=9, symbol="x")))
    fig.update_layout(title=title)
    return fig


def forecast_chart(forecast_df: pd.DataFrame, title: str, y_label: str) -> go.Figure:
    """Line chart distinguishing historical values from the forecast horizon."""
    hist = forecast_df[~forecast_df["is_forecast"]]
    future = forecast_df[forecast_df["is_forecast"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["date"], y=hist["forecast"], name="Historical", line=dict(color="#1565C0")))
    fig.add_trace(go.Scatter(x=future["date"], y=future["forecast"], name="Forecast", line=dict(color="#EF6C00", dash="dash")))
    fig.update_layout(title=title, xaxis_title="Date", yaxis_title=y_label)
    return fig


def cluster_scatter(cluster_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of Mandi clusters on total arrivals vs avg modal price."""
    fig = px.scatter(cluster_df, x="total_arrivals", y="avg_modal_price", color=cluster_df["cluster"].astype(str),
                      hover_data=["mandi_id"], title="Mandi Clusters (Arrivals vs Avg Modal Price)",
                      labels={"total_arrivals": "Total Arrivals (Quintal)", "avg_modal_price": "Avg Modal Price", "color": "Cluster"})
    return fig
