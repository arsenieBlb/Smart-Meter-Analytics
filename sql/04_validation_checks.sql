SET search_path TO utility;

SELECT 'duplicate_readings_same_meter_timestamp' AS check_name,
       COUNT(*) AS failed_records,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       'Duplicate readings can double-count consumption and distort operational alerts.' AS business_reason
FROM (
    SELECT meter_id, reading_timestamp
    FROM fact_meter_reading
    GROUP BY meter_id, reading_timestamp
    HAVING COUNT(*) > 1
) duplicates

UNION ALL
SELECT 'negative_consumption_values',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Negative consumption is not physically valid and must not feed billing or KPI reporting.'
FROM fact_meter_reading
WHERE consumption_value < 0

UNION ALL
SELECT 'missing_values_where_not_expected',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Non-missing readings require a usable consumption value.'
FROM fact_meter_reading
WHERE is_missing = FALSE AND consumption_value IS NULL

UNION ALL
SELECT 'invalid_meter_ids',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Every fact row must connect to a known meter for trustworthy drill-through analysis.'
FROM fact_meter_reading fr
LEFT JOIN dim_meter dm ON fr.meter_id = dm.meter_id
WHERE dm.meter_id IS NULL

UNION ALL
SELECT 'invalid_customer_ids',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Every meter must belong to a known customer so segment and regional reporting remain correct.'
FROM dim_meter dm
LEFT JOIN dim_customer dc ON dm.customer_id = dc.customer_id
WHERE dc.customer_id IS NULL

UNION ALL
SELECT 'impossible_future_timestamps',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Future timestamps indicate clock, ingestion, or synthetic-data generation errors.'
FROM fact_meter_reading
WHERE reading_timestamp > CURRENT_TIMESTAMP

UNION ALL
SELECT 'date_table_coverage',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'All fact dates must be represented in dim_date for time intelligence in Power BI.'
FROM fact_meter_reading fr
LEFT JOIN dim_date dd ON fr.date_key = dd.date_key
WHERE dd.date_key IS NULL

UNION ALL
SELECT 'fact_table_row_count',
       CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END,
       CASE WHEN COUNT(*) = 0 THEN 'FAIL' ELSE 'PASS' END,
       'The reading fact table must contain records before dashboards can be trusted.'
FROM fact_meter_reading

UNION ALL
SELECT 'active_meters_have_readings',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Active meters without readings reduce service visibility and understate operational risk.'
FROM (
    SELECT dm.meter_id
    FROM dim_meter dm
    LEFT JOIN fact_meter_reading fr ON dm.meter_id = fr.meter_id
    WHERE dm.status = 'Active'
    GROUP BY dm.meter_id
    HAVING COUNT(fr.reading_id) = 0
) active_meters_without_readings

UNION ALL
SELECT 'anomaly_count_consistency',
       ABS(
           (SELECT COUNT(*) FROM fact_meter_reading WHERE is_anomaly = TRUE)
           - (SELECT COUNT(*) FROM fact_data_quality_event WHERE event_type = 'Abnormal Spike')
       ),
       CASE
           WHEN (
               SELECT COUNT(*) FROM fact_meter_reading WHERE is_anomaly = TRUE
           ) = (
               SELECT COUNT(*) FROM fact_data_quality_event WHERE event_type = 'Abnormal Spike'
           ) THEN 'PASS'
           ELSE 'FAIL'
       END,
       'Anomaly flags and quality events must reconcile so operations and BI users see the same issue count.'

UNION ALL
SELECT 'health_score_range_0_to_100',
       COUNT(*),
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
       'Health scores outside 0-100 cannot be interpreted consistently by business users.'
FROM fact_meter_health
WHERE health_score < 0 OR health_score > 100;
