"""
End-to-end reproducible ETL pipeline.

    RAW -> INGESTION -> PROFILING -> CLEANING -> STANDARDIZATION
        -> VALIDATION -> FEATURE ENGINEERING -> SQLite DB -> Dashboard

Run with:
    python -m src.pipeline
"""

import json
import logging
import sqlite3
from pathlib import Path

import pandas as pd

from src import config, ingestion, profiling, cleaning, validation, feature_engineering as fe

logging.basicConfig(level=config.LOG_LEVEL, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def run_pipeline() -> dict:
    """Run the full pipeline and return the data-quality report dict."""
    config.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------- 1. INGESTION ----------------------------------
    logger.info("STAGE 1/6: Ingestion")
    raw = ingestion.load_all_raw()

    # ---------------- 2. PROFILING (on RAW data) ---------------------
    logger.info("STAGE 2/6: Profiling raw data")
    raw_profiles = {
        name: profiling.profile_dataset(name, df)
        for name, df in raw.items()
    }
    raw_row_counts = {name: len(df) for name, df in raw.items()}

    # ---------------- 3. CLEANING ------------------------------------
    logger.info("STAGE 3/6: Cleaning")
    cleaned = {
        "mandi_master": cleaning.clean_mandi_master(raw["mandi_master"]),
        "arrivals": cleaning.clean_arrivals(raw["arrivals"]),
        "prices": cleaning.clean_prices(raw["prices"]),
        "weather": cleaning.clean_weather(raw["weather"]),
        "transport": cleaning.clean_transport(raw["transport"]),
    }
    cleaned["msp_reference"] = cleaning.build_msp_reference(cleaned["prices"])
    cleaned_row_counts = {name: len(df) for name, df in cleaned.items()}

    # ---------------- 4. VALIDATION -----------------------------------
    logger.info("STAGE 4/6: Validation")
    validation_results = validation.run_all_validations(cleaned)

    # ---------------- 5. FEATURE ENGINEERING --------------------------
    logger.info("STAGE 5/6: Feature engineering")
    arrivals_feat = fe.build_arrivals_features(cleaned["arrivals"], cleaned["mandi_master"])
    price_feat = fe.build_price_features(cleaned["prices"])
    weather_daily = fe.build_weather_daily(cleaned["weather"])
    market_value = fe.build_market_value(arrivals_feat, price_feat)

    # ---------------- 6. LOAD (SQLite + processed files) --------------
    logger.info("STAGE 6/6: Loading into SQLite + processed files")
    _write_processed_csvs(cleaned, arrivals_feat, price_feat, weather_daily, market_value)
    _load_sqlite(cleaned, arrivals_feat, price_feat, weather_daily, market_value)

    # ---------------- DATA QUALITY REPORT ------------------------------
    report = _build_quality_report(raw, cleaned, raw_row_counts, cleaned_row_counts,
                                    raw_profiles, validation_results)
    with open(config.DATA_QUALITY_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info("Pipeline complete. Quality report -> %s", config.DATA_QUALITY_REPORT_PATH)
    _print_row_count_summary(report)
    return report


def _write_processed_csvs(cleaned, arrivals_feat, price_feat, weather_daily, market_value):
    for name, df in cleaned.items():
        df.to_csv(config.DATA_PROCESSED_DIR / f"clean_{name}.csv", index=False)
    arrivals_feat.to_csv(config.DATA_PROCESSED_DIR / "features_arrivals.csv", index=False)
    price_feat.to_csv(config.DATA_PROCESSED_DIR / "features_prices.csv", index=False)
    weather_daily.to_csv(config.DATA_PROCESSED_DIR / "features_weather_daily.csv", index=False)
    market_value.to_csv(config.DATA_PROCESSED_DIR / "features_market_value.csv", index=False)


def _load_sqlite(cleaned, arrivals_feat, price_feat, weather_daily, market_value):
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    try:
        cleaned["mandi_master"].to_sql("mandis", conn, if_exists="replace", index=False)
        cleaned["arrivals"].to_sql("arrivals_clean", conn, if_exists="replace", index=False)
        cleaned["prices"].to_sql("prices_clean", conn, if_exists="replace", index=False)
        cleaned["msp_reference"].to_sql("msp_reference", conn, if_exists="replace", index=False)
        cleaned["weather"].to_sql("weather_clean", conn, if_exists="replace", index=False)
        cleaned["transport"].to_sql("transport_clean", conn, if_exists="replace", index=False)

        arrivals_feat.to_sql("arrivals_features", conn, if_exists="replace", index=False)
        price_feat.to_sql("price_features", conn, if_exists="replace", index=False)
        weather_daily.to_sql("weather_daily", conn, if_exists="replace", index=False)
        market_value.to_sql("market_value", conn, if_exists="replace", index=False)

        # apply hand-written SQL views on top of the loaded tables
        sql_dir = config.ROOT_DIR / "sql"
        for sql_file in ["schema.sql", "views.sql"]:
            path = sql_dir / sql_file
            if path.exists():
                script = path.read_text(encoding="utf-8")
                try:
                    conn.executescript(script)
                except sqlite3.OperationalError as exc:
                    logger.warning("Skipping %s statement error: %s", sql_file, exc)
        conn.commit()
    finally:
        conn.close()


def _build_quality_report(raw, cleaned, raw_counts, cleaned_counts, raw_profiles, validation_results) -> dict:
    total_raw = sum(raw_counts.values())
    total_cleaned = sum(cleaned_counts.values())
    return {
        "_notice": "All figures below are computed live from the synthetic datasets - none are hard-coded.",
        "row_counts": {
            "per_dataset": {
                name: {
                    "raw": raw_counts[name],
                    "cleaned": cleaned_counts[name],
                    "rows_removed": raw_counts[name] - cleaned_counts[name],
                }
                for name in raw_counts
            },
            "total_raw_rows": total_raw,
            "total_cleaned_rows": total_cleaned,
            "total_rows_removed": total_raw - total_cleaned,
        },
        "raw_profiling": raw_profiles,
        "validation_results": validation_results,
        "crop_normalization": {
            "unique_raw_crop_values": int(raw["arrivals"]["crop_name"].nunique()),
            "unique_canonical_crops": int(cleaned["arrivals"]["crop"].nunique()),
        },
        "unit_conversion": {
            "distinct_raw_quantity_units": sorted(raw["arrivals"]["unit"].dropna().unique().tolist()),
            "canonical_unit": "Quintal",
        },
        "timezone_normalization": {
            "presentation_timezone": config.PRESENTATION_TZ,
            "weather_rows_localized": int(cleaned["weather"]["timestamp_ist"].notna().sum()),
            "weather_rows_total": len(cleaned["weather"]),
        },
    }


def _print_row_count_summary(report: dict):
    rc = report["row_counts"]
    print("\n" + "=" * 60)
    print("DATA QUALITY SUMMARY - RAW vs CLEANED ROW COUNTS")
    print("=" * 60)
    for name, counts in rc["per_dataset"].items():
        print(f"  {name:15s} raw={counts['raw']:>7,}  cleaned={counts['cleaned']:>7,}  removed={counts['rows_removed']:>6,}")
    print("-" * 60)
    print(f"  {'TOTAL':15s} raw={rc['total_raw_rows']:>7,}  cleaned={rc['total_cleaned_rows']:>7,}  removed={rc['total_rows_removed']:>6,}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_pipeline()
