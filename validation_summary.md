# Validation Summary

Data validation is included to make the analytics trustworthy. Each check is written in SQL and can be run against PostgreSQL after loading the pipeline outputs.

| Validation Check | What It Does | Why It Matters | Clean Result |
|---|---|---|---|
| Duplicate readings for same meter and timestamp | Finds repeated records for one meter at the same timestamp. | Prevents double-counted consumption and duplicated alerts. | Zero duplicate meter/timestamp groups. |
| Negative consumption values | Finds readings below zero. | Utility consumption cannot be negative for normal daily reporting. | Zero negative values. |
| Missing values where not expected | Finds non-missing readings without consumption values. | Prevents hidden blanks from being treated as valid readings. | Zero failed rows. |
| Invalid meter IDs | Finds fact rows that do not match `dim_meter`. | Ensures drill-through and meter health reporting work. | Every reading maps to a known meter. |
| Invalid customer IDs | Finds meters that do not map to `dim_customer`. | Protects customer-type and regional reporting. | Every meter maps to a known customer. |
| Impossible future timestamps | Finds readings dated after the current timestamp. | Identifies clock or ingestion errors. | Zero future readings. |
| Date table coverage | Ensures every fact `date_key` exists in `dim_date`. | Required for time intelligence in Power BI. | Every fact date is covered. |
| Fact table row count | Confirms the reading fact table is populated. | Dashboards are not meaningful without fact rows. | Reading fact table has rows. |
| Active meters matching expected distinct counts | Finds active meters without readings. | Active assets should report data unless there is a service issue. | Zero active meters without readings. |
| Anomaly count consistency | Reconciles anomaly flags with data-quality events. | BI and operations should see the same anomaly count. | Counts match exactly. |
| Health score range | Finds health scores outside 0-100. | Keeps health status interpretation consistent. | All scores are between 0 and 100. |

A clean result means failed records are zero, or the check status is `PASS`. This supports trust in reporting because dashboard users can see that core business metrics are backed by explicit quality controls.

