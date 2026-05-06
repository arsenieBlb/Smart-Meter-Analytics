# Power BI Build Guide

## 1. Prepare Data

Run the pipeline:

```powershell
python -m python.run_pipeline
```

For PostgreSQL:

```powershell
docker compose up -d postgres
python -m python.run_pipeline --load-postgres
```

## 2. Connect Power BI

PostgreSQL:

- `Get data > PostgreSQL database`
- Server: `localhost:5432`
- Database: `smart_utility`
- Select schema `utility`

CSV:

- `Get data > Text/CSV`
- Import files from `data/processed/`

## 3. Build The Model

Follow `semantic_model_guide.md`:

- Create relationships.
- Mark `dim_date` as the Date table.
- Hide technical keys.
- Add a Measures table.
- Paste measures from `dax_measures.dax`.

## 4. Build Pages

Follow `report_pages_layout.md` to create:

- Executive Overview
- Consumption Analysis
- Meter Health & Data Quality
- Anomaly Detection
- Metric Definitions

## 5. Validate And Capture Screenshots

Before publishing screenshots:

- Run SQL validation checks.
- Confirm slicers affect KPIs.
- Confirm totals match `vw_executive_kpis`.
- Capture screenshots listed in `screenshot_checklist.md`.

