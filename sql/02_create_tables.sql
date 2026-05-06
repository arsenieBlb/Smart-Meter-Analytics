SET search_path TO utility;

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    week INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_id INTEGER PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_type VARCHAR(30) NOT NULL CHECK (customer_type IN ('Residential', 'Commercial', 'Industrial')),
    region_id INTEGER NOT NULL REFERENCES dim_region(region_id),
    city VARCHAR(100) NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_meter (
    meter_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL REFERENCES dim_customer(customer_id),
    meter_type VARCHAR(30) NOT NULL CHECK (meter_type IN ('Electricity', 'Water', 'Heat')),
    installation_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Active', 'Inactive')),
    expected_readings_per_day INTEGER NOT NULL DEFAULT 1 CHECK (expected_readings_per_day > 0)
);

CREATE TABLE IF NOT EXISTS fact_meter_reading (
    reading_id VARCHAR(30) PRIMARY KEY,
    meter_id VARCHAR(20) NOT NULL REFERENCES dim_meter(meter_id),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    reading_timestamp TIMESTAMP NOT NULL,
    consumption_value NUMERIC(14, 3),
    is_missing BOOLEAN NOT NULL DEFAULT FALSE,
    is_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    is_anomaly BOOLEAN NOT NULL DEFAULT FALSE,
    ingestion_timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_meter_health (
    health_id VARCHAR(30) PRIMARY KEY,
    meter_id VARCHAR(20) NOT NULL REFERENCES dim_meter(meter_id),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    latest_reading_timestamp TIMESTAMP,
    missing_reading_count_30d INTEGER NOT NULL,
    anomaly_count_30d INTEGER NOT NULL,
    data_freshness_hours NUMERIC(12, 2) NOT NULL,
    health_status VARCHAR(20) NOT NULL CHECK (health_status IN ('Healthy', 'Watch', 'Critical', 'Inactive')),
    health_score NUMERIC(5, 2) NOT NULL CHECK (health_score BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS fact_data_quality_event (
    event_id VARCHAR(30) PRIMARY KEY,
    meter_id VARCHAR(20) REFERENCES dim_meter(meter_id),
    date_key INTEGER REFERENCES dim_date(date_key),
    event_type VARCHAR(60) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('Info', 'Low', 'Medium', 'High', 'Critical')),
    description TEXT NOT NULL,
    detected_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fact_meter_reading_meter_date ON fact_meter_reading(meter_id, date_key);
CREATE INDEX IF NOT EXISTS idx_fact_meter_reading_timestamp ON fact_meter_reading(reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_meter_reading_flags ON fact_meter_reading(is_missing, is_anomaly, is_estimated);
CREATE INDEX IF NOT EXISTS idx_fact_meter_health_meter ON fact_meter_health(meter_id);
CREATE INDEX IF NOT EXISTS idx_fact_quality_event_type ON fact_data_quality_event(event_type, severity);
CREATE INDEX IF NOT EXISTS idx_dim_customer_region ON dim_customer(region_id);
CREATE INDEX IF NOT EXISTS idx_dim_meter_customer ON dim_meter(customer_id);

