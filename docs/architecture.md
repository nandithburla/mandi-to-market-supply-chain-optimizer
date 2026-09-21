# Architecture

## Pipeline Flow

```
data/raw/*.csv,.json,.xlsx (synthetic, messy)
        |
        v
  [ src/ingestion.py ]        -> read raw files into DataFrames
        |
        v
  [ src/profiling.py ]        -> missingness / duplicate profiling (pre-clean)
        |
        v
  [ src/cleaning.py ]         -> per-dataset missing-value + duplicate strategy
        |
        v
  [ src/standardization.py ]  -> normalize_crop, normalize_mandi_id,
        |                         convert_to_quintal, parse_date_any,
        |                         normalize_timezone, clean_price_string
        v
  [ src/validation.py ]       -> referential integrity, date validity,
        |                         negative-value checks
        v
  [ src/feature_engineering.py] -> joins (arrivals+mandi, prices+MSP,
        |                           weather daily agg, market value)
        v
  [ src/pipeline.py ]         -> orchestrates all of the above, writes:
        |                         - data/processed/*.csv
        |                         - data/processed/mandi_market.db (SQLite)
        |                         - data/processed/data_quality_report.json
        v
  +-----------------------------+-----------------------------+
  |                                                            |
  v                                                            v
[ sql/schema.sql, views.sql ]                    [ src/analytics.py ]
  applied on top of SQLite tables                 forecasting, anomaly
  (indexes + 5 analytical views)                  detection, clustering
  |                                                            |
  +-----------------------------+-----------------------------+
                                |
                                v
                [ dashboard/app.py (Streamlit) ]
                  components.py  -> cached data loaders, filters
                  kpis.py        -> core KPI + risk-score formulas
                  charts.py      -> Plotly chart builders
                  5 pages: Executive Overview, Mandi Intelligence,
                           MSP Monitor, Weather Impact, Supply Chain Risk
```

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `src/config.py` | Every path, unit-conversion factor, crop-name map, risk weight - single source of truth, nothing hard-coded elsewhere |
| `src/ingestion.py` | Pure file I/O, no transformation |
| `src/profiling.py` | Pre-cleaning missingness/duplicate measurement |
| `src/cleaning.py` | Documented missing-value + duplicate decisions per dataset |
| `src/standardization.py` | Reusable, unit-tested normalize/convert functions |
| `src/validation.py` | Post-cleaning sanity + referential-integrity checks |
| `src/feature_engineering.py` | Cross-dataset joins and derived analytical columns |
| `src/analytics.py` | Forecasting (Exponential Smoothing), anomaly detection (IQR / rolling z-score), K-Means clustering |
| `src/pipeline.py` | Orchestrates every stage end-to-end, reproducibly |
| `sql/*.sql` | Indexes, 5 analytical views, reference KPI queries |
| `dashboard/*.py` | Streamlit UI, KPI formulas, Plotly charts |
| `tests/*.py` | Unit tests for cleaning, validation and KPI logic |

## Data Store
**SQLite** (`data/processed/mandi_market.db`) was chosen over PostgreSQL for
zero-setup reproducibility - a grader can clone the repo and run the pipeline
without installing or configuring a database server.

## Why no denormalization beyond what's needed
Base tables (`mandis`, `arrivals_clean`, `prices_clean`, `msp`,
`weather_clean`, `transport_clean`) stay normalized. Only the SQL **views**
and the `*_features` / `market_value` analytical tables are denormalized,
and only because the dashboard and forecasting/anomaly/clustering functions
need flat, joined data to run efficiently.
