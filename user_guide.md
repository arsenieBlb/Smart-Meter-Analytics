# User Guide

This guide is written for business users viewing the Power BI dashboard.

## Filtering The Dashboard

Use slicers to filter by date, region, meter type, and customer type. Filters apply to KPI cards, trend charts, tables, and anomaly views unless a page states otherwise.

Common workflows:

- Select a region to compare local consumption and data quality.
- Select a meter type to focus on electricity, water, or heat.
- Select a customer type to compare residential, commercial, and industrial behavior.
- Narrow the date range to investigate a specific month or operational period.

## Interpreting KPIs

Total Consumption shows the sum of valid meter readings. Missing readings are excluded from this value.

Active Meters shows meters currently expected to report readings.

Reading Success Rate shows the percentage of reading records that were received successfully.

Missing Reading % shows the share of expected readings that were not received.

Anomaly Count shows readings flagged as abnormal consumption spikes.

Critical Meter Count shows meters with low health scores that may require operational follow-up.

## Finding Problematic Meters

Open the Meter Health & Data Quality page and sort the critical meters table by health score or data freshness. Meters with low health scores, high missing reading counts, high anomaly counts, or stale data should be investigated first.

## Interpreting Anomalies

Anomalies are unusually high consumption values compared with expected behavior for the meter type and customer segment. An anomaly is not automatically an error. It is a signal for review.

Examples:

- A heat meter spike during winter may be explainable.
- A water spike may indicate leakage or reporting error.
- A sudden industrial electricity spike may reflect a production event.

## Using The Metric Definitions Page

Use the Metric Definitions page when a KPI is unclear. It explains each metric, its formula, business meaning, data source, and validation note.

This page helps dashboard users understand whether a number is about consumption, data quality, meter operations, or reporting freshness.

