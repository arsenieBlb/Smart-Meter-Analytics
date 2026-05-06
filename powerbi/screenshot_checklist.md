# Screenshot Checklist

Add screenshots after manually building the Power BI dashboard.

## Required Screenshots

- Executive Overview page with KPI cards and trend visuals
- Consumption Analysis page
- Meter Health & Data Quality page
- Anomaly Detection page
- Metric Definitions page
- Power BI model relationship view
- FastAPI Swagger/OpenAPI docs at `/docs`
- Pipeline terminal summary after running `python -m python.run_pipeline`
- PostgreSQL tables or views visible in pgAdmin

## Quality Checklist

- KPI cards are readable.
- Slicers are visible.
- Report pages use business-friendly names.
- Critical meters table shows health score and freshness.
- Model view shows a clean star schema.
- Screenshots do not expose secrets or local credentials.

