"""
Mandi-to-Market Supply Chain Optimizer - Streamlit Dashboard.

Run with:
    streamlit run dashboard/app.py

Requires the pipeline to have been run first:
    python -m src.pipeline
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, analytics
from dashboard import kpis, charts, components
from agent.agent import ask_agent


st.set_page_config(
    page_title="Mandi-to-Market Supply Chain Optimizer",
    layout="wide",
    page_icon="🌾",
)


CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 1.6rem;
    }

    div[data-testid="stMetric"] {
        background-color: #F4F8F4;
        border: 1px solid #DCE8DC;
        border-radius: 10px;
        padding: 12px 16px;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricLabel"] {
        color: #000000 !important;
    }

    h1, h2, h3 {
        color: #1B4332;
    }

    .synthetic-badge {
        display: inline-block;
        background: #FFF3CD;
        color: #7A5B00;
        border: 1px solid #F0D98C;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.8rem;
        margin-bottom: 8px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _load_data():
    if not config.SQLITE_DB_PATH.exists():
        return None

    return components.load_all_tables()


def _missing_db_message():
    st.error(
        "No analytical database found. Please run the pipeline first:\n\n"
        "```\npython -m src.pipeline\n```"
    )


def render_executive_overview(data, arrivals_f, prices_f, market_value_f):
    st.header("📊 Executive Overview")
    st.caption(
        "A single-glance view of arrivals, prices and risk across every selected Mandi."
    )

    risk_df = kpis.compute_mandi_risk_scores(
        prices_f,
        arrivals_f,
        data["weather_daily"],
    )

    avg_risk = (
        risk_df["risk_score"].mean()
        if not risk_df.empty
        else float("nan")
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        components.kpi_card(
            "Total Arrivals (Qtl)",
            f"{kpis.total_arrivals_quintal(arrivals_f):,.0f}",
            "Sum of quantity_quintal across selected filters.",
        )

    with c2:
        components.kpi_card(
            "Est. Market Value",
            f"₹{kpis.total_market_value(market_value_f):,.0f}",
            "Quantity x Modal Price, only where a matching price record exists.",
        )

    with c3:
        components.kpi_card(
            "Avg Modal Price",
            f"₹{kpis.avg_modal_price(prices_f):,.0f}",
        )

    with c4:
        components.kpi_card(
            "% Below MSP",
            f"{kpis.pct_below_msp(prices_f):.1f}%",
            "Share of price observations where Modal Price < MSP.",
        )

    with c5:
        components.kpi_card(
            "Avg Risk Score",
            f"{avg_risk:.1f}" if pd.notna(avg_risk) else "N/A",
            "0-100 transparent Mandi Risk Score (see Supply Chain Risk page).",
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            charts.daily_arrivals_trend(arrivals_f),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            charts.price_vs_msp(prices_f),
            use_container_width=True,
        )

    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(
            charts.top_mandis_by_arrivals(arrivals_f),
            use_container_width=True,
        )

    with col4:
        st.plotly_chart(
            charts.crop_distribution(arrivals_f),
            use_container_width=True,
        )

    st.markdown(
        "**Story:** Arrivals and prices are tracked side-by-side so the Board can immediately see "
        "whether periods of high supply coincide with prices sliding toward (or below) MSP - "
        "the earliest signal of farmer distress."
    )


def render_mandi_intelligence(
    arrivals_f,
    prices_f,
    market_value_f,
    weather_daily,
):
    st.header("🏪 Mandi Intelligence")
    st.caption(
        "Drill into any Mandi's arrival volume, pricing and risk profile."
    )

    if arrivals_f.empty:
        st.info("No arrivals match the current filters.")
        return

    mandi_summary = arrivals_f.groupby(
        ["mandi_id", "mandi_name"]
    ).agg(
        total_arrivals_quintal=("quantity_quintal", "sum"),
        active_days=("arrival_date", "nunique"),
    ).reset_index()

    price_summary = prices_f.groupby("mandi_id").agg(
        avg_modal_price=("modal_price", "mean"),
        avg_msp_gap_pct=("msp_gap_pct", "mean"),
        volatility=("modal_price", "std"),
    ).reset_index()

    merged = mandi_summary.merge(
        price_summary,
        on="mandi_id",
        how="left",
    )

    risk_df = kpis.compute_mandi_risk_scores(
        prices_f,
        arrivals_f,
        weather_daily,
    )

    merged = merged.merge(
        risk_df[
            ["mandi_id", "risk_score", "risk_category"]
        ],
        on="mandi_id",
        how="left",
    )

    st.dataframe(
        merged.sort_values(
            "total_arrivals_quintal",
            ascending=False,
        ).style.format(
            {
                "total_arrivals_quintal": "{:,.0f}",
                "avg_modal_price": "₹{:,.0f}",
                "avg_msp_gap_pct": "{:.1f}%",
                "volatility": "{:,.0f}",
                "risk_score": "{:.1f}",
            }
        ),
        use_container_width=True,
        height=420,
    )

    st.plotly_chart(
        charts.top_mandis_by_arrivals(
            arrivals_f,
            top_n=15,
        ),
        use_container_width=True,
    )


def render_msp_monitor(prices_f):
    st.header("💰 MSP Monitor")
    st.caption(
        "Where is the market paying below the Minimum Support Price?"
    )

    if prices_f.dropna(
        subset=["msp_per_quintal"]
    ).empty:
        st.info(
            "No price records with a matching MSP in the current filters."
        )
        return

    c1, c2, c3 = st.columns(3)

    with c1:
        components.kpi_card(
            "Avg MSP Gap",
            f"₹{kpis.avg_msp_gap(prices_f):,.0f}",
        )

    with c2:
        components.kpi_card(
            "Avg MSP Gap %",
            f"{kpis.avg_msp_gap_pct(prices_f):.1f}%",
        )

    with c3:
        components.kpi_card(
            "% Observations Below MSP",
            f"{kpis.pct_below_msp(prices_f):.1f}%",
        )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            charts.price_vs_msp(prices_f),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            charts.msp_gap_by_crop(prices_f),
            use_container_width=True,
        )

    st.plotly_chart(
        charts.below_msp_by_mandi(prices_f),
        use_container_width=True,
    )

    st.markdown(
        "**Story:** Crops with a persistently negative MSP Gap % indicate the Board's price-support "
        "mechanism is not reaching farmers in that Mandi/crop combination and may need intervention."
    )


def render_weather_impact(arrivals_f, weather_daily):
    st.header("🌦️ Weather Impact")
    st.caption(
        "How do rainfall, temperature and humidity relate to crop arrivals?"
    )

    daily_arrivals = (
        arrivals_f.groupby("arrival_date")["quantity_quintal"]
        .sum()
        .reset_index()
    )

    daily_arrivals = daily_arrivals.rename(
        columns={
            "quantity_quintal": "total_quantity_quintal",
            "arrival_date": "date",
        }
    )

    merged = daily_arrivals.merge(
        weather_daily,
        on="date",
        how="inner",
    )

    if merged.empty:
        st.info(
            "No overlapping weather and arrival dates in the current filters."
        )
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        corr_rain = merged[
            "total_rainfall_mm"
        ].corr(
            merged["total_quantity_quintal"]
        )

        components.kpi_card(
            "Rainfall <> Arrivals corr.",
            f"{corr_rain:.2f}"
            if pd.notna(corr_rain)
            else "N/A",
        )

    with col2:
        corr_temp = merged[
            "avg_temperature_c"
        ].corr(
            merged["total_quantity_quintal"]
        )

        components.kpi_card(
            "Temperature <> Arrivals corr.",
            f"{corr_temp:.2f}"
            if pd.notna(corr_temp)
            else "N/A",
        )

    with col3:
        corr_hum = merged[
            "avg_humidity_pct"
        ].corr(
            merged["total_quantity_quintal"]
        )

        components.kpi_card(
            "Humidity <> Arrivals corr.",
            f"{corr_hum:.2f}"
            if pd.notna(corr_hum)
            else "N/A",
        )

    col4, col5 = st.columns(2)

    with col4:
        st.plotly_chart(
            charts.weather_scatter(
                merged,
                "total_rainfall_mm",
                "Rainfall (mm)",
            ),
            use_container_width=True,
        )

    with col5:
        st.plotly_chart(
            charts.weather_scatter(
                merged,
                "avg_temperature_c",
                "Temperature (°C)",
            ),
            use_container_width=True,
        )

    st.plotly_chart(
        charts.weather_scatter(
            merged,
            "avg_humidity_pct",
            "Humidity (%)",
        ),
        use_container_width=True,
    )


def render_supply_chain_risk(
    arrivals_f,
    prices_f,
    weather_daily,
):
    st.header("⚠️ Supply Chain Risk")
    st.caption(
        "A transparent, configurable Mandi Risk Score combining MSP pressure, "
        "price volatility, arrival anomalies and weather anomalies."
    )

    risk_df = kpis.compute_mandi_risk_scores(
        prices_f,
        arrivals_f,
        weather_daily,
    )

    if risk_df.empty:
        st.info(
            "Not enough data to compute risk scores for the current filters."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            charts.risk_ranking_bar(risk_df),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            charts.risk_category_counts(risk_df),
            use_container_width=True,
        )

    with st.expander(
        "Risk score weights (configurable in src/config.py)"
    ):
        st.json(config.RISK_WEIGHTS)

    st.divider()

    st.subheader("Arrival Anomalies")

    arrival_anomalies = analytics.detect_arrival_anomalies(
        arrivals_f
    )

    crop_choice = st.selectbox(
        "Crop for anomaly view",
        (
            sorted(arrival_anomalies["crop"].unique())
            if not arrival_anomalies.empty
            else []
        ),
    )

    if crop_choice:
        sub = arrival_anomalies[
            arrival_anomalies["crop"] == crop_choice
        ]

        st.plotly_chart(
            charts.anomaly_timeseries(
                sub,
                "arrival_date",
                "quantity_quintal",
                "iqr_anomaly",
                f"Arrival Anomalies (IQR method) - {crop_choice}",
            ),
            use_container_width=True,
        )

    st.subheader("Price Anomalies")

    price_anomalies = analytics.detect_price_anomalies(
        prices_f
    )

    crop_choice2 = st.selectbox(
        "Crop for price-anomaly view",
        (
            sorted(price_anomalies["crop"].unique())
            if not price_anomalies.empty
            else []
        ),
        key="price_anom_crop",
    )

    if crop_choice2:
        sub2 = price_anomalies[
            price_anomalies["crop"] == crop_choice2
        ]

        st.plotly_chart(
            charts.anomaly_timeseries(
                sub2,
                "price_date",
                "modal_price",
                "iqr_anomaly",
                f"Price Anomalies (IQR method) - {crop_choice2}",
            ),
            use_container_width=True,
        )

    st.divider()

    st.subheader("Forecasting")

    fc1, fc2 = st.columns(2)

    crops_available = (
        sorted(arrivals_f["crop"].unique())
        if not arrivals_f.empty
        else []
    )

    with fc1:
        fc_crop = (
            st.selectbox(
                "Crop to forecast",
                crops_available,
                key="fc_crop",
            )
            if crops_available
            else None
        )

        if fc_crop:
            fc_df = analytics.forecast_arrivals(
                arrivals_f,
                crop=fc_crop,
                periods=14,
            )

            st.plotly_chart(
                charts.forecast_chart(
                    fc_df,
                    f"14-Day Arrival Forecast - {fc_crop}",
                    "Arrivals (Quintal)",
                ),
                use_container_width=True,
            )

    with fc2:
        if fc_crop:
            fc_price_df = analytics.forecast_price(
                prices_f,
                crop=fc_crop,
                periods=14,
            )

            st.plotly_chart(
                charts.forecast_chart(
                    fc_price_df,
                    f"14-Day Price Forecast - {fc_crop}",
                    "Modal Price",
                ),
                use_container_width=True,
            )

    st.divider()

    st.subheader("Mandi Clustering (K-Means)")

    cluster_df = analytics.cluster_mandis(
        arrivals_f,
        prices_f,
        n_clusters=min(
            4,
            max(
                2,
                arrivals_f["mandi_id"].nunique() // 3 or 2,
            ),
        ),
    )

    if not cluster_df.empty and "cluster" in cluster_df.columns:
        st.plotly_chart(
            charts.cluster_scatter(cluster_df),
            use_container_width=True,
        )

        st.caption(
            "Mandis in the same cluster show similar arrival-volume and pricing "
            "behaviour and may benefit from shared logistics or price-support strategies."
        )


def render_ai_assistant():
    st.header("🤖 AI Agricultural Assistant")

    st.caption(
        "Ask questions about mandi arrivals, crop prices, MSP, "
        "transport, warehouses and weather using the agricultural dataset."
    )

    question = st.text_input(
        "Ask a question",
        placeholder="Example: Which wheat mandis are selling below MSP?",
    )

    if not question:
        st.info(
            "Ask a question to get an AI-powered answer from the agricultural dataset."
        )
        return

    with st.spinner("AI is analyzing your question..."):
        try:
            result = ask_agent(question)

            st.markdown(result["answer"])

            if result["chart"] is not None:
                st.plotly_chart(
                    result["chart"],
                    use_container_width=True,
                )

        except Exception as exc:
            st.error(
                "The AI assistant could not process this question right now."
            )

            st.caption(
                f"Error: {exc}"
            )


def main():
    st.title("🌾 Mandi-to-Market Supply Chain Optimizer")

    data = _load_data()

    if data is None:
        _missing_db_message()
        return

    filters = components.render_filter_sidebar(
        data["arrivals_features"],
        data["price_features"],
        data["mandis"],
    )

    arrivals_f, prices_f = components.apply_filters(
        data["arrivals_features"],
        data["price_features"],
        filters,
    )

    market_value_f = data["market_value"][
        data["market_value"]["mandi_id"].isin(filters["mandis"])
        & data["market_value"]["crop"].isin(filters["crops"])
        & (
            data["market_value"]["arrival_date"]
            >= filters["start_date"]
        )
        & (
            data["market_value"]["arrival_date"]
            <= filters["end_date"]
        )
    ]

    page = st.sidebar.radio(
        "Page",
        [
            "1. Executive Overview",
            "2. Mandi Intelligence",
            "3. MSP Monitor",
            "4. Weather Impact",
            "5. Supply Chain Risk",
            "6. AI Agricultural Assistant",
        ],
    )

    if page.startswith("1"):
        render_executive_overview(
            data,
            arrivals_f,
            prices_f,
            market_value_f,
        )

    elif page.startswith("2"):
        render_mandi_intelligence(
            arrivals_f,
            prices_f,
            market_value_f,
            data["weather_daily"],
        )

    elif page.startswith("3"):
        render_msp_monitor(prices_f)

    elif page.startswith("4"):
        render_weather_impact(
            arrivals_f,
            data["weather_daily"],
        )

    elif page.startswith("5"):
        render_supply_chain_risk(
            arrivals_f,
            prices_f,
            data["weather_daily"],
        )

    elif page.startswith("6"):
        render_ai_assistant()


if __name__ == "__main__":
    main()