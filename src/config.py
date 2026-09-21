"""
Configuration constants for the Mandi-to-Market Supply Chain Optimizer.

Centralising paths, canonical vocab and tunable weights here means no
other module should ever hard-code a path, unit factor or KPI weight.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATA_EXTERNAL_DIR = ROOT_DIR / "data" / "external"

RAW_ARRIVALS_FILE = DATA_RAW_DIR / "track3_mandi_arrivals.csv"
RAW_PRICE_MSP_FILE = DATA_RAW_DIR / "track3_price_and_msp.json"
RAW_WEATHER_FILE = DATA_RAW_DIR / "track3_weather_sensors.xlsx"
RAW_TRANSPORT_FILE = DATA_RAW_DIR / "track3_transport_logistics.csv"
RAW_MANDI_MASTER_FILE = DATA_RAW_DIR / "track3_mandi_master.csv"

SQLITE_DB_PATH = DATA_PROCESSED_DIR / "mandi_market.db"
DATA_QUALITY_REPORT_PATH = DATA_PROCESSED_DIR / "data_quality_report.json"

# ---------------------------------------------------------------------------
# Unit conversion (canonical quantity unit = Quintal)
# ---------------------------------------------------------------------------
KG_PER_QUINTAL = 100.0
QUINTAL_PER_TONNE = 10.0

UNIT_TO_QUINTAL_FACTOR = {
    "qtl": 1.0, "quintal": 1.0, "quintals": 1.0, "q": 1.0,
    "kg": 1 / KG_PER_QUINTAL, "kgs": 1 / KG_PER_QUINTAL, "kilo": 1 / KG_PER_QUINTAL,
    "tonnes": QUINTAL_PER_TONNE, "tonne": QUINTAL_PER_TONNE, "mt": QUINTAL_PER_TONNE, "t": QUINTAL_PER_TONNE,
}

# distance: canonical unit = km
MILES_TO_KM = 1.60934

# ---------------------------------------------------------------------------
# Crop name normalization (English / Hindi / spelling variants -> canonical)
# ---------------------------------------------------------------------------
CROP_CANONICAL_MAP = {
    # Wheat
    "wheat": "Wheat", "gehun": "Wheat", "ganne": "Wheat",  # 'ganne' typo seen in source -> mapped w/ care
    "गेहूँ": "Wheat", "गेहूं": "Wheat",
    # Rice
    "rice": "Rice", "paddy": "Rice", "chawal": "Rice", "धान": "Rice",
    # Maize
    "maize": "Maize", "corn": "Maize", "makka": "Maize", "मक्का": "Maize",
    # Mustard
    "mustard": "Mustard", "sarson": "Mustard", "sarso": "Mustard", "सरसों": "Mustard",
    # Cotton
    "cotton": "Cotton", "kapas": "Cotton",
    # Sugarcane
    "sugarcane": "Sugarcane", "ganna": "Sugarcane",
    # Basmati
    "basmati": "Basmati",
    
    "कपास": "Cotton",

    "गन्ना": "Sugarcane",

    "बासमती": "Basmati",
}

# ---------------------------------------------------------------------------
# Mandi ID normalization
# ---------------------------------------------------------------------------
MANDI_ID_CANONICAL_WIDTH = 3  # MANDI001 style, zero-padded to 3 digits

# ---------------------------------------------------------------------------
# Timezone handling
# ---------------------------------------------------------------------------
INTERNAL_TZ = "UTC"          # internal storage convention
PRESENTATION_TZ = "Asia/Kolkata"  # display/analysis convention

# ---------------------------------------------------------------------------
# Risk score weights (must sum to 1.0) - configurable
# ---------------------------------------------------------------------------
RISK_WEIGHTS = {
    "msp_pressure": 0.35,
    "price_volatility": 0.25,
    "arrival_anomaly": 0.20,
    "weather_anomaly": 0.20,
}

RISK_BANDS = {
    "Low": (0, 30),
    "Medium": (31, 60),
    "High": (61, 80),
    "Critical": (81, 100),
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_LEVEL = "INFO"
