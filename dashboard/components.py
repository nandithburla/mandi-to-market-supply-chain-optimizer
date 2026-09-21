"""
Reusable Streamlit UI components: cached data loaders, KPI cards and
the shared filter sidebar used across every dashboard page.
"""

import sqlite3

import pandas as pd
import streamlit as st

from src import config


@st.cache_data(show_spinner=False)
def load_table(table_name: str) -> pd.DataFrame:
    """Load a table/view from the SQLite analytical database, cached
    for the life of the Streamlit session."""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()
    for col in df.columns:
        if col.endswith("_date") or col == "date":
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_all_tables() -> dict:
    """Load every analytical table used by the dashboard in one call."""
    return {
        "mandis": load_table("mandis"),
        "arrivals_features": load_table("arrivals_features"),
        "price_features": load_table("price_features"),
        "weather_daily": load_table("weather_daily"),
        "market_value": load_table("market_value"),
        "transport_clean": load_table("transport_clean"),
    }


def kpi_card(label: str, value: str, help_text: str = "") -> None:
    """Render a single KPI metric using Streamlit's built-in metric widget."""
    st.metric(label=label, value=value, help=help_text or None)


def render_filter_sidebar(arrivals: pd.DataFrame, prices: pd.DataFrame, mandis: pd.DataFrame) -> dict:
    """Render the shared State / District / Mandi / Crop / Date-range
    filters and return the selected values as a dict."""
    st.sidebar.header("Filters")

    states = sorted(mandis["state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect("State", states, default=states)

    filtered_mandis = mandis[mandis["state"].isin(selected_states)] if selected_states else mandis
    districts = sorted(filtered_mandis["district"].dropna().unique().tolist())
    selected_districts = st.sidebar.multiselect("District", districts, default=districts)

    filtered_mandis = filtered_mandis[filtered_mandis["district"].isin(selected_districts)] if selected_districts else filtered_mandis
    mandi_options = sorted(filtered_mandis["mandi_id"].unique().tolist())
    selected_mandis = st.sidebar.multiselect("Mandi", mandi_options, default=mandi_options)

    crops = sorted(arrivals["crop"].dropna().unique().tolist())
    selected_crops = st.sidebar.multiselect("Crop", crops, default=crops)

    min_date = arrivals["arrival_date"].min()
    max_date = arrivals["arrival_date"].max()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date),
                                        min_value=min_date, max_value=max_date)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    return {
        "states": selected_states,
        "districts": selected_districts,
        "mandis": selected_mandis,
        "crops": selected_crops,
        "start_date": pd.Timestamp(start_date),
        "end_date": pd.Timestamp(end_date),
    }


def apply_filters(arrivals: pd.DataFrame, prices: pd.DataFrame, filters: dict):
    """Apply the shared sidebar filters to the arrivals and prices frames."""
    a = arrivals[
        arrivals["mandi_id"].isin(filters["mandis"])
        & arrivals["crop"].isin(filters["crops"])
        & (arrivals["arrival_date"] >= filters["start_date"])
        & (arrivals["arrival_date"] <= filters["end_date"])
    ]
    p = prices[
        prices["mandi_id"].isin(filters["mandis"])
        & prices["crop"].isin(filters["crops"])
        & (prices["price_date"] >= filters["start_date"])
        & (prices["price_date"] <= filters["end_date"])
    ]
    return a, p
