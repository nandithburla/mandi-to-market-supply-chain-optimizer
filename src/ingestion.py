"""
Ingestion layer.

Responsible ONLY for reading raw files (CSV / JSON / XLSX) into pandas
DataFrames. No cleaning or transformation happens here - that keeps the
pipeline stages testable in isolation.
"""

import json
import logging
from typing import Dict

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def load_mandi_master() -> pd.DataFrame:
    """Load the raw Mandi master data (Mandi id/name/district/state)."""
    df = pd.read_csv(config.RAW_MANDI_MASTER_FILE)
    logger.info("Loaded mandi_master: %s rows", len(df))
    return df


def load_arrivals() -> pd.DataFrame:
    """Load the raw daily Mandi arrivals data."""
    df = pd.read_csv(config.RAW_ARRIVALS_FILE)
    logger.info("Loaded arrivals: %s rows", len(df))
    return df


def load_price_and_msp() -> pd.DataFrame:
    """Load the raw wholesale price + embedded MSP data from JSON.
    """
    with open(config.RAW_PRICE_MSP_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)
    df = pd.DataFrame(payload)
    logger.info("Loaded price_and_msp: %s rows", len(df))
    return df



def load_weather() -> pd.DataFrame:
    """Load the raw IoT weather sensor data (Excel)."""
    df = pd.read_excel(config.RAW_WEATHER_FILE)
    logger.info("Loaded weather: %s rows", len(df))
    return df


def load_transport() -> pd.DataFrame:
    """Load the raw transport/logistics trip data."""
    df = pd.read_csv(config.RAW_TRANSPORT_FILE)
    logger.info("Loaded transport: %s rows", len(df))
    return df


def load_all_raw() -> Dict[str, pd.DataFrame]:
    """Convenience loader that returns every raw dataset in one dict."""
    return {
        "mandi_master": load_mandi_master(),
        "arrivals": load_arrivals(),
        "prices": load_price_and_msp(),
        "weather": load_weather(),
        "transport": load_transport(),
    }

