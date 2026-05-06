# Metric Definitions

| Metric | Definition | Formula | Business Meaning | Data Source | Validation Note |
|---|---|---|---|---|---|
| Total Consumption | Sum of valid consumption values. | `SUM(consumption_value)` where `is_missing = false` | Shows total utility usage across selected filters. | `fact_meter_reading` | Excludes missing readings and depends on negative-value checks. |
| Active Meters | Count of meters with status `Active`. | `COUNTD(meter_id)` where `status = 'Active'` | Indicates operational meter base. | `dim_meter` | Reconciled against readings for active meters. |
| Total Meters | Count of all meters. | `COUNTD(meter_id)` | Shows total installed meter population. | `dim_meter` | Meter IDs must be unique. |
| Reading Success Rate | Share of readings successfully received. | `(non-missing readings / total reading rows) * 100` | Measures reliability of meter reporting. | `fact_meter_reading` | Missing flags must be populated consistently. |
| Missing Reading % | Share of reading rows marked missing. | `(missing readings / total reading rows) * 100` | Highlights data gaps that affect reporting trust. | `fact_meter_reading` | Checked through missing-value validation. |
| Anomaly Count | Number of readings flagged as abnormal. | `COUNT(reading_id)` where `is_anomaly = true` | Shows unusual consumption patterns requiring review. | `fact_meter_reading` | Reconciled with abnormal-spike quality events. |
| Critical Meter Count | Count of meters with critical health. | `COUNTD(meter_id)` where `health_status = 'Critical'` | Identifies meters needing operational follow-up. | `fact_meter_health` | Health score must be within 0-100. |
| Average Daily Consumption | Average consumption per calendar day. | `total consumption / distinct days` | Normalizes usage across date ranges. | `vw_monthly_consumption`, `fact_meter_reading` | Requires date table coverage. |
| Consumption Previous Month | Consumption shifted to previous month. | `CALCULATE([Total Consumption], PREVIOUSMONTH(dim_date[full_date]))` | Supports month-over-month analysis. | Power BI model | Requires dim_date marked as date table. |
| MoM Consumption Change % | Percentage change from previous month. | `([Total Consumption] - [Consumption Previous Month]) / [Consumption Previous Month]` | Shows whether consumption is increasing or decreasing. | Power BI model | Depends on consistent date relationships. |
| Average Health Score | Average meter health score. | `AVG(health_score)` | Summarizes operational meter reliability. | `fact_meter_health` | Scores must stay between 0 and 100. |
| Data Freshness Hours | Hours since latest meter reading. | `AVG(data_freshness_hours)` or meter-level value | Shows how current the reporting data is. | `fact_meter_health` | Future timestamp checks protect this metric. |
| Estimated Reading % | Share of readings marked estimated. | `(estimated readings / total readings) * 100` | Indicates how much reporting depends on estimates. | `fact_meter_reading` | Estimated flags must be boolean and complete. |

