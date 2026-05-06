SET search_path TO utility;

CREATE OR REPLACE VIEW vw_executive_kpis AS
SELECT
    COALESCE(SUM(fr.consumption_value) FILTER (WHERE fr.is_missing = FALSE), 0)::NUMERIC(18, 3) AS total_consumption,
    COUNT(DISTINCT dm.meter_id) FILTER (WHERE dm.status = 'Active') AS active_meters,
    COUNT(DISTINCT dm.meter_id) AS total_meters,
    ROUND(
        100.0 * COUNT(fr.reading_id) FILTER (WHERE fr.is_missing = FALSE)
        / NULLIF(COUNT(fr.reading_id), 0),
        2
    ) AS reading_success_rate,
    ROUND(
        100.0 * COUNT(fr.reading_id) FILTER (WHERE fr.is_missing = TRUE)
        / NULLIF(COUNT(fr.reading_id), 0),
        2
    ) AS missing_reading_percentage,
    COUNT(fr.reading_id) FILTER (WHERE fr.is_anomaly = TRUE) AS anomaly_count,
    COUNT(DISTINCT fh.meter_id) FILTER (WHERE fh.health_status = 'Critical') AS critical_meter_count,
    MAX(fr.reading_timestamp) AS latest_reading_timestamp
FROM dim_meter dm
LEFT JOIN fact_meter_reading fr ON dm.meter_id = fr.meter_id
LEFT JOIN fact_meter_health fh ON dm.meter_id = fh.meter_id;

CREATE OR REPLACE VIEW vw_daily_consumption AS
SELECT
    dd.full_date AS date,
    dr.region_name,
    dc.customer_type,
    dm.meter_type,
    COALESCE(SUM(fr.consumption_value) FILTER (WHERE fr.is_missing = FALSE), 0)::NUMERIC(18, 3) AS total_consumption,
    COUNT(DISTINCT dm.meter_id) FILTER (WHERE dm.status = 'Active') AS active_meters,
    COUNT(fr.reading_id) FILTER (WHERE fr.is_anomaly = TRUE) AS anomaly_count,
    COUNT(fr.reading_id) FILTER (WHERE fr.is_missing = TRUE) AS missing_reading_count
FROM fact_meter_reading fr
JOIN dim_date dd ON fr.date_key = dd.date_key
JOIN dim_meter dm ON fr.meter_id = dm.meter_id
JOIN dim_customer dc ON dm.customer_id = dc.customer_id
JOIN dim_region dr ON dc.region_id = dr.region_id
GROUP BY dd.full_date, dr.region_name, dc.customer_type, dm.meter_type;

CREATE OR REPLACE VIEW vw_monthly_consumption AS
SELECT
    dd.year,
    dd.month,
    dr.region_name,
    dc.customer_type,
    dm.meter_type,
    COALESCE(SUM(fr.consumption_value) FILTER (WHERE fr.is_missing = FALSE), 0)::NUMERIC(18, 3) AS total_consumption,
    ROUND(
        COALESCE(SUM(fr.consumption_value) FILTER (WHERE fr.is_missing = FALSE), 0)
        / NULLIF(COUNT(DISTINCT dd.full_date), 0),
        3
    ) AS avg_daily_consumption,
    COUNT(DISTINCT dm.meter_id) FILTER (WHERE dm.status = 'Active') AS active_meters
FROM fact_meter_reading fr
JOIN dim_date dd ON fr.date_key = dd.date_key
JOIN dim_meter dm ON fr.meter_id = dm.meter_id
JOIN dim_customer dc ON dm.customer_id = dc.customer_id
JOIN dim_region dr ON dc.region_id = dr.region_id
GROUP BY dd.year, dd.month, dr.region_name, dc.customer_type, dm.meter_type;

CREATE OR REPLACE VIEW vw_meter_health AS
SELECT
    dm.meter_id,
    dc.customer_id,
    dr.region_name,
    dm.meter_type,
    dm.status,
    fh.health_status,
    fh.health_score,
    fh.missing_reading_count_30d,
    fh.anomaly_count_30d,
    fh.data_freshness_hours
FROM dim_meter dm
JOIN dim_customer dc ON dm.customer_id = dc.customer_id
JOIN dim_region dr ON dc.region_id = dr.region_id
LEFT JOIN fact_meter_health fh ON dm.meter_id = fh.meter_id;

CREATE OR REPLACE VIEW vw_region_data_quality AS
SELECT
    dr.region_name,
    COUNT(DISTINCT dm.meter_id) AS total_meters,
    COUNT(DISTINCT dm.meter_id) FILTER (WHERE dm.status = 'Active') AS active_meters,
    ROUND(
        100.0 * COUNT(fr.reading_id) FILTER (WHERE fr.is_missing = TRUE)
        / NULLIF(COUNT(fr.reading_id), 0),
        2
    ) AS missing_reading_percentage,
    COUNT(fr.reading_id) FILTER (WHERE fr.is_anomaly = TRUE) AS anomaly_count,
    ROUND(AVG(fh.health_score), 2) AS avg_health_score,
    COUNT(DISTINCT fh.meter_id) FILTER (WHERE fh.health_status = 'Critical') AS critical_meter_count
FROM dim_region dr
JOIN dim_customer dc ON dr.region_id = dc.region_id
JOIN dim_meter dm ON dc.customer_id = dm.customer_id
LEFT JOIN fact_meter_reading fr ON dm.meter_id = fr.meter_id
LEFT JOIN fact_meter_health fh ON dm.meter_id = fh.meter_id
GROUP BY dr.region_name;

CREATE OR REPLACE VIEW vw_anomaly_summary AS
SELECT
    fr.meter_id,
    dr.region_name,
    dm.meter_type,
    fr.reading_timestamp,
    fr.consumption_value,
    dc.customer_type,
    CASE
        WHEN fr.consumption_value IS NULL THEN 'Missing anomaly value'
        ELSE 'Consumption spike above expected range'
    END AS anomaly_reason
FROM fact_meter_reading fr
JOIN dim_meter dm ON fr.meter_id = dm.meter_id
JOIN dim_customer dc ON dm.customer_id = dc.customer_id
JOIN dim_region dr ON dc.region_id = dr.region_id
WHERE fr.is_anomaly = TRUE;

