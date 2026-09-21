-- analytics.sql
-- ----------------------------------------------------------------------
-- Reference analytical queries. These mirror the KPI formulas
-- implemented in Python (dashboard/kpis.py) so a reviewer can verify
-- the numbers independently in any SQLite client. Not auto-executed
-- by the pipeline; kept here for transparency/auditability.
-- ----------------------------------------------------------------------

-- 1. Total arrivals (Quintals)
SELECT SUM(total_quantity_quintal) AS total_arrivals_quintal FROM vw_daily_arrivals;

-- 2. Total estimated market value
SELECT SUM(estimated_market_value) AS total_market_value FROM market_value;

-- 3. Average modal price
SELECT AVG(modal_price) AS avg_modal_price FROM price_features;

-- 4. Average MSP
SELECT AVG(msp_per_quintal) AS avg_msp FROM msp;

-- 5. MSP gap (row level) and average MSP gap %
SELECT AVG(msp_gap) AS avg_msp_gap, AVG(msp_gap_pct) AS avg_msp_gap_pct
FROM price_features WHERE msp_per_quintal IS NOT NULL;

-- 6. Percentage of observations below MSP
SELECT
    100.0 * SUM(CASE WHEN below_msp THEN 1 ELSE 0 END) / COUNT(*) AS pct_below_msp
FROM price_features
WHERE msp_per_quintal IS NOT NULL;

-- 7. Number of active Mandis
SELECT COUNT(DISTINCT mandi_id) AS active_mandis FROM arrivals_features;

-- 8. Number of active crops
SELECT COUNT(DISTINCT crop) AS active_crops FROM arrivals_features;

-- 9. Price volatility (std dev of modal price) per crop
SELECT crop, AVG(modal_price) AS mean_price,
       (AVG(modal_price*modal_price) - AVG(modal_price)*AVG(modal_price)) AS variance_approx
FROM price_features
GROUP BY crop;

-- 10. Mandi-level total arrivals (used for growth-rate / ranking)
SELECT mandi_id, mandi_name, total_arrivals_quintal
FROM vw_mandi_performance
ORDER BY total_arrivals_quintal DESC;

-- 11. Weather-arrival correlation input (raw pairs, correlation computed in Python)
SELECT arrival_date, total_quantity_quintal, avg_temperature_c, total_rainfall_mm, avg_humidity_pct
FROM vw_weather_arrival_relationship
ORDER BY arrival_date;
