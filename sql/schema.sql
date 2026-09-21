-- schema.sql
-- ----------------------------------------------------------------------
-- The base tables themselves are created/loaded by src/pipeline.py via
-- pandas.DataFrame.to_sql() (mandis, arrivals_clean, prices_clean, msp,
-- weather_clean, transport_clean, arrivals_features, price_features,
-- weather_daily, market_value). This script only adds indexes on top
-- of those tables to keep the analytical views fast, and documents the
-- intended primary/foreign keys since SQLite + to_sql does not enforce
-- them automatically.
--
-- Logical relationships:
--   mandis.mandi_id            (PK)
--   arrivals_clean.mandi_id    (FK -> mandis.mandi_id)
--   transport_clean.mandi_id   (FK -> mandis.mandi_id)
--   prices_clean.mandi_id      (FK -> mandis.mandi_id, nullable)
--   price_features.crop, .year (FK -> msp.crop, msp.year)
-- ----------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_mandis_mandi_id ON mandis(mandi_id);

CREATE INDEX IF NOT EXISTS idx_arrivals_mandi_id ON arrivals_clean(mandi_id);
CREATE INDEX IF NOT EXISTS idx_arrivals_crop ON arrivals_clean(crop);
CREATE INDEX IF NOT EXISTS idx_arrivals_date ON arrivals_clean(arrival_date);

CREATE INDEX IF NOT EXISTS idx_prices_mandi_id ON prices_clean(mandi_id);
CREATE INDEX IF NOT EXISTS idx_prices_crop ON prices_clean(crop);
CREATE INDEX IF NOT EXISTS idx_prices_date ON prices_clean(price_date);

CREATE INDEX IF NOT EXISTS idx_transport_mandi_id ON transport_clean(mandi_id);


CREATE INDEX IF NOT EXISTS idx_arrfeat_mandi_date ON arrivals_features(mandi_id, arrival_date);
CREATE INDEX IF NOT EXISTS idx_pricefeat_mandi_date ON price_features(mandi_id, price_date);
CREATE INDEX IF NOT EXISTS idx_marketvalue_mandi_date ON market_value(mandi_id, arrival_date);
