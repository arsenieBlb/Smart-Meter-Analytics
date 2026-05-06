SET search_path TO utility;

-- Executive KPI row for the dashboard landing page.
SELECT *
FROM vw_executive_kpis;

-- Monthly trend by region and meter type.
SELECT year, month, region_name, meter_type, total_consumption, avg_daily_consumption
FROM vw_monthly_consumption
ORDER BY year, month, region_name, meter_type;

-- Critical meters that need operational follow-up.
SELECT *
FROM vw_meter_health
WHERE health_status = 'Critical'
ORDER BY health_score ASC, data_freshness_hours DESC;

-- Regional data-quality comparison.
SELECT *
FROM vw_region_data_quality
ORDER BY missing_reading_percentage DESC, anomaly_count DESC;

-- Latest anomalies.
SELECT *
FROM vw_anomaly_summary
ORDER BY reading_timestamp DESC
LIMIT 50;

