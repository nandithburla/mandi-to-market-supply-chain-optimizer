-- views.sql
-- ----------------------------------------------------------------------
-- Analytical views consumed by the dashboard (dashboard/kpis.py) and
-- by ad-hoc analysis in sql/analytics.sql. Kept intentionally simple
-- and readable rather than over-denormalized.
-- ----------------------------------------------------------------------

DROP VIEW IF EXISTS vw_daily_arrivals;
CREATE VIEW vw_daily_arrivals AS
SELECT
    arrival_date,
    mandi_id,
    mandi_name,
    district,
    state,
    crop,
    SUM(quantity_quintal)      AS total_quantity_quintal,
    COUNT(*)                   AS arrival_records,
    SUM(COALESCE(farmer_count, 0)) AS total_farmers
FROM arrivals_features
GROUP BY arrival_date, mandi_id, mandi_name, district, state, crop;


DROP VIEW IF EXISTS vw_daily_prices;
CREATE VIEW vw_daily_prices AS
SELECT
    price_date,
    mandi_id,
    crop,
    AVG(min_price)    AS avg_min_price,
    AVG(max_price)    AS avg_max_price,
    AVG(modal_price)  AS avg_modal_price,
    COUNT(*)          AS price_records
FROM price_features
GROUP BY price_date, mandi_id, crop;


DROP VIEW IF EXISTS vw_msp_comparison;
CREATE VIEW vw_msp_comparison AS
SELECT
    price_date,
    mandi_id,
    crop,
    modal_price,
    msp_per_quintal,
    msp_gap,
    msp_gap_pct,
    below_msp
FROM price_features
WHERE msp_per_quintal IS NOT NULL;


DROP VIEW IF EXISTS vw_mandi_performance;
CREATE VIEW vw_mandi_performance AS
SELECT
    a.mandi_id,
    a.mandi_name,
    a.district,
    a.state,
    SUM(a.quantity_quintal)              AS total_arrivals_quintal,
    COUNT(DISTINCT a.crop)               AS distinct_crops,
    COUNT(DISTINCT a.arrival_date)       AS active_days,
    AVG(mv.estimated_market_value)       AS avg_market_value_per_record
FROM arrivals_features a
LEFT JOIN market_value mv
    ON a.mandi_id = mv.mandi_id AND a.arrival_date = mv.arrival_date AND a.crop = mv.crop
GROUP BY a.mandi_id, a.mandi_name, a.district, a.state;


DROP VIEW IF EXISTS vw_weather_arrival_relationship;
CREATE VIEW vw_weather_arrival_relationship AS
SELECT
    d.arrival_date,
    SUM(d.total_quantity_quintal) AS total_quantity_quintal,
    w.avg_temperature_c,
    w.total_rainfall_mm,
    w.avg_humidity_pct
FROM vw_daily_arrivals d
LEFT JOIN weather_daily w
    ON d.arrival_date = w.date
GROUP BY d.arrival_date, w.avg_temperature_c, w.total_rainfall_mm, w.avg_humidity_pct;
