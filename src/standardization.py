"""
Standardization utilities.

Contains the reusable, unit-tested functions that turn messy raw
values into canonical values: normalize_crop(), convert_to_quintal(),
normalize_mandi_id(), parse_date_any(), convert_distance_to_km(),
convert_temperature_to_celsius(), convert_rainfall_to_mm() and
normalize_timezone().
"""

import logging
import re
from typing import Optional, Union

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def extract_numeric(value) -> Optional[float]:
    """Pull a numeric value out of a string that may have a unit glued on
    (e.g. '4.7 hrs', '316.5 KM', '39.8°C'). Returns None if nothing
    numeric can be found. Already-numeric input passes through unchanged.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.upper() in {"NA", "N/A", "NULL", "NONE"}:
        return None
    numeric_str = re.sub(r"[^0-9\.\-]", "", s)
    if numeric_str in ("", "-", "."):
        return None
    try:
        return float(numeric_str)
    except ValueError:
        return None
    

def normalize_crop(raw_value: Optional[str]) -> Optional[str]:
    """Map an English/Hindi/mixed-case crop name to its canonical form.

    Example
    -------
    >>> normalize_crop("गेहूँ")
    'Wheat'
    >>> normalize_crop("CORN")
    'Maize'
    """
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    key = str(raw_value).strip().lower()
    if key == "":
        return None
    return config.CROP_CANONICAL_MAP.get(key, str(raw_value).strip().title())


def normalize_mandi_id(raw_value: Optional[Union[str, int]]) -> Optional[str]:
    """Normalize any Mandi-id spelling variant to the canonical MANDI### form.

    Handles: 'MANDI001', 'MANDI-001', 'mandi_001', 'mandi001', 'M001',
    and bare numeric strings like '056'.
    """
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    s = str(raw_value).strip()
    digits = re.sub(r"[^0-9]", "", s)
    if digits == "":
        return None
    number = int(digits)
    return f"MANDI{number:0{config.MANDI_ID_CANONICAL_WIDTH}d}"


def convert_to_quintal(quantity: Optional[float], unit: Optional[str]) -> Optional[float]:
    """Convert a quantity in an arbitrary unit into Quintals (canonical unit).

    1 Quintal = 100 KG, 1 Tonne = 10 Quintal.
    Unknown/missing units are assumed to already be Quintal (the most
    common unit in the source data) and this assumption is logged.
    """
    if quantity is None or (isinstance(quantity, float) and pd.isna(quantity)):
        return None
    if unit is None or (isinstance(unit, float) and pd.isna(unit)) or str(unit).strip() == "":
        factor = 1.0  # documented assumption: default to Quintal
    else:
        key = str(unit).strip().lower()
        factor = config.UNIT_TO_QUINTAL_FACTOR.get(key, 1.0)
    return round(quantity * factor, 4)


def convert_distance_to_km(distance, unit: Optional[str] = None) -> Optional[float]:
    """Convert a distance value to kilometres (canonical unit). Handles
    distance values with the unit embedded in the string (e.g. '316.5 KM')."""
    numeric_value = extract_numeric(distance)
    if numeric_value is None:
        return None
    unit_key = "" if unit is None or (isinstance(unit, float) and pd.isna(unit)) else str(unit).strip().lower()
    if isinstance(distance, str) and unit_key == "" and "mile" in distance.lower():
        unit_key = "miles"
    if unit_key == "miles":
        return round(numeric_value * config.MILES_TO_KM, 3)
    return round(numeric_value, 3)


def convert_temperature_to_celsius(value, unit: Optional[str] = None) -> Optional[float]:
    """Convert a temperature reading to Celsius (canonical unit).

    Handles two source formats seen in the raw data:
      1. A clean numeric value with the unit in a separate `unit` column
         (e.g. 39.8, 'F').
      2. The unit embedded directly in the value as a string
         (e.g. '39.8°C', '68F').
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    unit_key = "" if unit is None or (isinstance(unit, float) and pd.isna(unit)) else str(unit).strip().lower()

    if isinstance(value, str):
        s = value.strip()
        # detect an embedded unit marker before stripping it out
        s_lower = s.lower()
        if "f" in s_lower and unit_key == "":
            unit_key = "f"
        elif "c" in s_lower and unit_key == "":
            unit_key = "c"
        # keep only digits, sign and decimal point
        numeric_str = re.sub(r"[^0-9\.\-]", "", s)
        if numeric_str in ("", "-", "."):
            return None
        try:
            numeric_value = float(numeric_str)
        except ValueError:
            return None
    else:
        numeric_value = float(value)

    if unit_key.startswith("f"):
        return round((numeric_value - 32) * 5 / 9, 2)
    return round(numeric_value, 2)


def convert_rainfall_to_mm(value, unit: Optional[str] = None) -> Optional[float]:
    """Convert a rainfall reading to millimetres (canonical unit).
    Handles both a clean numeric value + separate unit column, and a
    unit embedded directly in the value string (e.g. '0.91in')."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    unit_key = "" if unit is None or (isinstance(unit, float) and pd.isna(unit)) else str(unit).strip().lower()

    if isinstance(value, str):
        s_lower = value.lower()
        if unit_key == "":
            if "in" in s_lower:
                unit_key = "in"
            elif "mm" in s_lower:
                unit_key = "mm"
        numeric_str = re.sub(r"[^0-9\.\-]", "", value)
        if numeric_str in ("", "-", "."):
            return None
        try:
            numeric_value = float(numeric_str)
        except ValueError:
            return None
    else:
        numeric_value = float(value)

    if unit_key in {"in", "inch", "inches"}:
        return round(numeric_value * 25.4, 2)
    return round(numeric_value, 2)


# A deliberately small, explicit list of formats we expect to see, tried
# in order. Falls back to pandas' flexible parser (dayfirst=False) if
# none match, and finally to NaT if the value is genuinely unparseable.
_KNOWN_DATE_FORMATS = [
    "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%d.%m.%Y",
    "%d-%b-%Y", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%m-%d-%Y %H:%M",
    "%d/%m/%Y %I:%M %p", "%m/%d/%Y", "%d-%b-%Y %I:%M %p", "%Y-%m-%d %H:%M:%S",
]


def parse_date_any(raw_value) -> Optional[pd.Timestamp]:
    """Parse a date/datetime string that may be in one of several formats.

    Returns a proper pandas.Timestamp (never a raw string). Returns
    pandas.NaT if the value cannot be parsed at all - callers should
    count these and report them in the data-quality report rather than
    silently dropping the row.
    """
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return pd.NaT
    s = str(raw_value).strip()
    if s == "":
        return pd.NaT
    for fmt in _KNOWN_DATE_FORMATS:
        try:
            return pd.to_datetime(s, format=fmt)
        except (ValueError, TypeError):
            continue
    # last resort: pandas' own inference
    try:
        return pd.to_datetime(s, errors="raise", dayfirst=True)
    except (ValueError, TypeError):
        logger.debug("Unparseable date value: %r", raw_value)
        return pd.NaT


def normalize_timezone(timestamp_raw: str) -> Optional[pd.Timestamp]:
    """Parse a weather timestamp (possibly tagged UTC/IST/untagged) and
    return a tz-aware pandas Timestamp converted to the presentation
    timezone (Asia/Kolkata).

    Internal convention: naive/untagged timestamps are ASSUMED to
    already be in the presentation timezone (Asia/Kolkata) since the
    sensors are physically located in India; this assumption is
    documented in docs/methodology.md.
    """
    if timestamp_raw is None or (isinstance(timestamp_raw, float) and pd.isna(timestamp_raw)):
        return pd.NaT
    s = str(timestamp_raw).strip()
    if s == "":
        return pd.NaT

    tz_tag = None
    if s.upper().endswith("IST"):
        tz_tag = "IST"
        s = s[:-3].strip()
    elif s.upper().endswith("UTC"):
        tz_tag = "UTC"
        s = s[:-3].strip()

    parsed = parse_date_any(s)
    if pd.isna(parsed):
        return pd.NaT

    if tz_tag == "UTC":
        localized = parsed.tz_localize("UTC")
    else:
        # IST-tagged or untagged -> assume Asia/Kolkata already
        localized = parsed.tz_localize(config.PRESENTATION_TZ)

    return localized.tz_convert(config.PRESENTATION_TZ)


def clean_price_string(raw_value) -> Optional[float]:
    """Strip currency symbols/commas from a price string and cast to float."""
    if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
        return None
    s = str(raw_value)
    s = re.sub(r"[₹,]", "", s)
    s = re.sub(r"(?i)\brs\.?|\binr\b", "", s).strip()
    try:
        return float(s)
    except ValueError:
        return None
