# Methodology

## 1. Missing Values
Missingness was profiled per-column (`src/profiling.py`) before any cleaning
decision was made (see `notebooks/01_data_profiling.ipynb`). Strategy varies
by column:

- **Descriptive/non-KPI fields** (district, mandi_type, variety): filled with
  an explicit `"Unknown"` label rather than dropped, preserving the row for
  arrival/price analysis.
- **KPI-critical numeric fields** (arrival_quantity, modal_price): left as
  `NaN` when unparseable, and excluded from `SUM`/`AVG` via pandas' native
  NaN-skipping rather than imputed with a guessed value - imputing tonnage or
  price would silently bias every downstream KPI.
- **Foreign keys** (mandi_id on prices): kept even when null; the row still
  carries a `district`, enabling district-level aggregation without forcing a
  fabricated Mandi.

## 2. Duplicates
The business key for each dataset was chosen deliberately rather than using
"all columns":

| Dataset | Business key | Reasoning |
|---|---|---|
| mandi_master | `mandi_id` (normalized) | Same Mandi re-exported under a differently-formatted id is still one Mandi |
| arrivals | exact row match | Two exports of the same arrival are indistinguishable; a full-row duplicate is safest |
| prices | exact row match | Same reasoning as arrivals |
| msp | (`crop`, `year`, `season`) | MSP is set once per crop/season/year |
| weather | exact row match | Duplicate sensor pings |
| transport | `trip_id` | Trip id is the natural primary key |

## 3. Multilingual / Crop Normalization
`normalize_crop()` lower-cases and strips the raw value, then looks it up in
`config.CROP_CANONICAL_MAP`, which maps English spelling variants (Wheat /
wheat / WHEAT), transliterations (Gehun), and Hindi script (गेहूँ, गेहूं) to a
single canonical English name. Unrecognized values fall back to Title Case
rather than being dropped, so new/unexpected crop names remain visible for
review instead of disappearing silently.

## 4. Unit Conversion
Canonical quantity unit = **Quintal** (1 Quintal = 100 KG = 0.1 Tonne).
`convert_to_quintal()` applies a lookup-table factor (`config.UNIT_TO_QUINTAL_FACTOR`).
When the unit itself is missing, the value is assumed to already be in
Quintal (the most frequent unit observed during profiling) - a documented
assumption, not a silent guess. Distance is canonicalized to **km**
(`convert_distance_to_km()`, miles x 1.60934).

## 5. Date Normalization
`parse_date_any()` tries a fixed, documented list of expected formats (ISO,
`DD-MM-YYYY`, `MM/DD/YYYY`, dotted, `DD-Mon-YYYY`, ISO-datetime, 12-hour
clock, etc.) before falling back to pandas' flexible parser, and finally to
`NaT` if truly unparseable. Every stage returns real `datetime64`/`Timestamp`
objects, never strings, and every `NaT` produced is counted in the
data-quality report rather than being hidden.

## 6. Timezone Handling
Internal convention: raw weather timestamps may be suffixed `UTC` or `IST`,
or carry no timezone marker at all. `normalize_timezone()`:
1. Detects and strips a trailing `UTC`/`IST` tag.
2. Parses the remaining timestamp with `parse_date_any()`.
3. If tagged `UTC`, localizes to UTC then converts to `Asia/Kolkata`.
4. If tagged `IST` or **untagged**, assumes the timestamp is already
   `Asia/Kolkata` (sensors are physically located in India) - this
   assumption is explicit and documented here rather than buried in code.

All presentation and dashboard analysis uses `Asia/Kolkata` as required.

## 7. Relationships Between Datasets
- `arrivals.mandi_id` -> `mandis.mandi_id` (left join to attach district/state)
- `transport.mandi_id` -> `mandis.mandi_id`
- `prices.crop` + `year(price_date)` -> `msp.crop` + `msp.year` (MSP gap calc)
- `arrivals` + `prices` joined on (`mandi_id`, `crop`, `date`) to estimate
  market value; unmatched combinations are reported transparently (match-rate
  %) rather than forced.
- `weather` is aggregated to one row per calendar date and joined to daily
  arrival/price totals by date (sensor-to-Mandi mapping is out of scope for
  this synthetic dataset - documented simplification).

## 8. KPI Formulas
See `dashboard/kpis.py` docstrings for the authoritative, executable
definitions. Summary:

- **Total Arrivals (Quintal)** = SUM(quantity_quintal)
- **Total Market Value** = SUM(quantity_quintal x modal_price) where matched
- **MSP Gap** = Modal Price - MSP
- **MSP Gap %** = (MSP Gap / MSP) x 100
- **% Below MSP** = share of price rows where MSP Gap < 0
- **Price Volatility** = std. dev. of modal price
- **Arrival Growth Rate %** = (2nd-half total - 1st-half total) / 1st-half total x 100

## 9. Mandi Risk Score Methodology
`Risk Score = 0.35 x MSP_pressure + 0.25 x price_volatility + 0.20 x arrival_anomaly + 0.20 x weather_anomaly`
(weights configurable in `src/config.RISK_WEIGHTS`)

- **MSP pressure**: mean(max(0, -MSP Gap %)) per Mandi, min-max scaled 0-100.
- **Price volatility**: std. dev. of modal price per Mandi, min-max scaled.
- **Arrival anomaly**: coefficient of variation (std/mean) of daily arrivals
  per Mandi, min-max scaled - a stable Mandi has low CoV.
- **Weather anomaly**: national daily rainfall volatility (documented
  simplification - synthetic weather sensors are not Mandi-located).

Bands: **Low** 0-30, **Medium** 31-60, **High** 61-80, **Critical** 81-100.
