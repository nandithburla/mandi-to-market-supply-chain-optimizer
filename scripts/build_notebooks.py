"""Builds notebooks/01_data_profiling.ipynb, 02_data_cleaning.ipynb and
03_analysis.ipynb as real, runnable notebooks (not screenshots)."""

import nbformat as nbf


def make_notebook(cells):
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    return nb


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


# ---------------------------------------------------------------------------
# 01_data_profiling.ipynb
# ---------------------------------------------------------------------------
profiling_cells = [
    md("# 01 - Data Profiling\n"
       "Profiles every RAW synthetic dataset before any cleaning happens, "
       "so every cleaning decision in `02_data_cleaning.ipynb` is backed by "
       "an actual measurement.\n\n"
       "**All data used here is synthetic** (see `data/raw/track3_dataset_notes.txt`)."),
    code("import sys, pathlib\n"
         "sys.path.insert(0, str(pathlib.Path('..').resolve()))\n"
         "import pandas as pd\n"
         "from src import ingestion, profiling\n"
         "pd.set_option('display.max_columns', 50)"),
    md("## Load raw datasets"),
    code("raw = ingestion.load_all_raw()\n"
         "{name: df.shape for name, df in raw.items()}"),
    md("## Raw row counts (for Gate 1 proof-of-cleaning comparison later)"),
    code("raw_counts = {name: len(df) for name, df in raw.items()}\n"
         "raw_counts"),
    md("## Missingness per dataset"),
    code("for name, df in raw.items():\n"
         "    print(f'--- {name} ---')\n"
         "    display(profiling.profile_missingness(df).head(10))"),
    md("## Duplicate counts per dataset"),
    code("for name, df in raw.items():\n"
         "    print(name, profiling.profile_duplicates(df))"),
    md("## Observed messiness (spot checks)\n"
       "A few manual spot-checks that motivate the standardization functions in `src/standardization.py`."),
    code("print('Distinct raw crop_name values (sample):')\n"
         "print(sorted(raw['arrivals']['crop_name'].dropna().unique())[:20])\n\n"
         "print('\\nDistinct raw quantity units:')\n"
         "print(raw['arrivals']['unit'].dropna().unique())\n\n"
         "print('\\nDistinct raw mandi_id formats (sample):')\n"
         "print(raw['arrivals']['mandi_id'].dropna().unique()[:15])"),
    md("These findings directly motivate: `normalize_crop()`, `normalize_mandi_id()`, "
       "`convert_to_quintal()`, `parse_date_any()` and `normalize_timezone()` in "
       "`src/standardization.py`, applied next in `02_data_cleaning.ipynb`."),
]

# ---------------------------------------------------------------------------
# 02_data_cleaning.ipynb
# ---------------------------------------------------------------------------
cleaning_cells = [
    md("# 02 - Data Cleaning & Standardization\n"
       "Runs the reusable cleaning/standardization functions from `src/` "
       "on each raw dataset and shows the raw-vs-cleaned row count proof "
       "required for Gate 1."),
    code("import sys, pathlib\n"
         "sys.path.insert(0, str(pathlib.Path('..').resolve()))\n"
         "import pandas as pd\n"
         "from src import ingestion, cleaning, validation, feature_engineering as fe"),
    md("## Load raw data"),
    code("raw = ingestion.load_all_raw()\n"
         "raw_counts = {name: len(df) for name, df in raw.items()}"),
    md("## Apply cleaning + standardization"),
    code("cleaned = {\n"
         "    'mandi_master': cleaning.clean_mandi_master(raw['mandi_master']),\n"
         "    'arrivals': cleaning.clean_arrivals(raw['arrivals']),\n"
         "    'prices': cleaning.clean_prices(raw['prices']),\n"
         "    'msp': cleaning.clean_msp(raw['msp']),\n"
         "    'weather': cleaning.clean_weather(raw['weather']),\n"
         "    'transport': cleaning.clean_transport(raw['transport']),\n"
         "}\n"
         "cleaned_counts = {name: len(df) for name, df in cleaned.items()}"),
    md("## RAW vs CLEANED row counts (Gate 1 requirement)"),
    code("summary = pd.DataFrame({'raw_rows': raw_counts, 'cleaned_rows': cleaned_counts})\n"
         "summary['rows_removed'] = summary['raw_rows'] - summary['cleaned_rows']\n"
         "summary.loc['TOTAL'] = summary.sum()\n"
         "summary"),
    md("## Spot-check: crop normalization worked"),
    code("cleaned['arrivals'][['crop_name', 'crop']].drop_duplicates().sample(10, random_state=1)"),
    md("## Spot-check: mandi_id normalization worked"),
    code("raw['arrivals']['mandi_id'].head(5).tolist(), cleaned['arrivals']['mandi_id'].head(5).tolist()"),
    md("## Spot-check: unit conversion to Quintal"),
    code("cleaned['arrivals'][['arrival_quantity', 'unit', 'quantity_quintal']].head(10)"),
    md("## Validation checks (referential integrity, dates, negative values)"),
    code("validation_results = validation.run_all_validations(cleaned)\n"
         "pd.DataFrame(validation_results)"),
    md("## Feature engineering (joins + derived KPIs feed columns)"),
    code("arrivals_feat = fe.build_arrivals_features(cleaned['arrivals'], cleaned['mandi_master'])\n"
         "price_feat = fe.build_price_features(cleaned['prices'], cleaned['msp'])\n"
         "weather_daily = fe.build_weather_daily(cleaned['weather'])\n"
         "market_value = fe.build_market_value(arrivals_feat, price_feat)\n"
         "arrivals_feat.shape, price_feat.shape, weather_daily.shape, market_value.shape"),
    md("This is the same logic executed end-to-end and reproducibly by `python -m src.pipeline`, "
       "which also writes the cleaned/feature tables to `data/processed/` and the SQLite database."),
]

# ---------------------------------------------------------------------------
# 03_analysis.ipynb
# ---------------------------------------------------------------------------
analysis_cells = [
    md("# 03 - Analysis\n"
       "Exploratory analysis on top of the cleaned analytical tables: core KPIs, "
       "MSP performance, weather correlation, forecasting, anomaly detection and clustering."),
    code("import sys, pathlib\n"
         "sys.path.insert(0, str(pathlib.Path('..').resolve()))\n"
         "import sqlite3, pandas as pd\n"
         "from src import config, analytics\n"
         "from dashboard import kpis\n\n"
         "conn = sqlite3.connect(config.SQLITE_DB_PATH)\n"
         "arrivals = pd.read_sql_query('SELECT * FROM arrivals_features', conn)\n"
         "prices = pd.read_sql_query('SELECT * FROM price_features', conn)\n"
         "weather_daily = pd.read_sql_query('SELECT * FROM weather_daily', conn)\n"
         "market_value = pd.read_sql_query('SELECT * FROM market_value', conn)\n"
         "arrivals['arrival_date'] = pd.to_datetime(arrivals['arrival_date'])\n"
         "prices['price_date'] = pd.to_datetime(prices['price_date'])\n"
         "weather_daily['date'] = pd.to_datetime(weather_daily['date'])\n"
         "market_value['arrival_date'] = pd.to_datetime(market_value['arrival_date'])"),
    md("## Core KPIs"),
    code("print('Total arrivals (Quintal):', round(kpis.total_arrivals_quintal(arrivals), 2))\n"
         "print('Total estimated market value:', round(kpis.total_market_value(market_value), 2))\n"
         "print('Avg modal price:', round(kpis.avg_modal_price(prices), 2))\n"
         "print('Avg MSP:', round(kpis.avg_msp(prices), 2))\n"
         "print('Avg MSP gap %:', round(kpis.avg_msp_gap_pct(prices), 2))\n"
         "print('% observations below MSP:', round(kpis.pct_below_msp(prices), 2))\n"
         "print('Active Mandis:', kpis.active_mandi_count(arrivals))\n"
         "print('Active crops:', kpis.active_crop_count(arrivals))\n"
         "print('Arrival growth rate %:', round(kpis.arrival_growth_rate(arrivals), 2))"),
    md("## Mandi Risk Score"),
    code("risk_df = kpis.compute_mandi_risk_scores(prices, arrivals, weather_daily)\n"
         "risk_df.sort_values('risk_score', ascending=False).head(10)"),
    md("## Weather vs Arrivals correlation"),
    code("daily_arr = arrivals.groupby('arrival_date')['quantity_quintal'].sum().reset_index()\n"
         "daily_arr = daily_arr.rename(columns={'quantity_quintal':'total_quantity_quintal','arrival_date':'date'})\n"
         "merged = daily_arr.merge(weather_daily, on='date', how='inner')\n"
         "merged[['total_rainfall_mm','avg_temperature_c','avg_humidity_pct','total_quantity_quintal']].corr()"),
    md("## Forecasting (Exponential Smoothing)"),
    code("crop_example = arrivals['crop'].value_counts().idxmax()\n"
         "forecast_df = analytics.forecast_arrivals(arrivals, crop=crop_example, periods=14)\n"
         "forecast_df.tail(14)"),
    md("## Anomaly Detection (IQR + rolling z-score)"),
    code("arrival_anomalies = analytics.detect_arrival_anomalies(arrivals)\n"
         "arrival_anomalies[arrival_anomalies['iqr_anomaly']].head(10)"),
    md("## Mandi Clustering (K-Means)"),
    code("cluster_df = analytics.cluster_mandis(arrivals, prices, n_clusters=4)\n"
         "cluster_df.groupby('cluster').agg(mandis=('mandi_id','count'), avg_arrivals=('total_arrivals','mean'), avg_price=('avg_modal_price','mean'))"),
    md("These same functions power the interactive Streamlit dashboard (`dashboard/app.py`), "
       "so every number a Board member sees on screen can be reproduced here."),
]

nbf.write(make_notebook(profiling_cells), "notebooks/01_data_profiling.ipynb")
nbf.write(make_notebook(cleaning_cells), "notebooks/02_data_cleaning.ipynb")
nbf.write(make_notebook(analysis_cells), "notebooks/03_analysis.ipynb")
print("Notebooks written.")
