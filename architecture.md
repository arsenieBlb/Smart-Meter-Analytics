# Architecture

## Flow

```text
Synthetic Data / Optional Open Data
-> Python Pipeline
-> PostgreSQL Star Schema
-> SQL Views
-> Validation Checks
-> FastAPI
-> Power BI
-> Documentation
```

## Components

The Python pipeline generates realistic smart-meter data, standardizes it, derives meter health and data-quality events, and exports clean CSV files. The same pipeline can optionally load PostgreSQL.

PostgreSQL stores data in a star schema with dimensions for date, region, customer, and meter. Fact tables hold meter readings, meter health snapshots, and data-quality events.

SQL views expose business-friendly datasets for Power BI and API consumers. They keep report logic consistent and reduce repeated calculations across tools.

Validation checks create a transparent trust layer. They test for duplicate readings, invalid relationships, missing values, future timestamps, anomaly consistency, and health score range.

FastAPI exposes operational endpoints for KPIs, meters, regional quality, anomalies, and data-quality events. This demonstrates how analytics outputs can also support applications and operational workflows.

Power BI consumes PostgreSQL views or CSV exports. The report build package includes DAX measures, relationship guidance, page layout instructions, and a screenshot checklist.

## Design Decisions

- Synthetic data is the default so the project runs offline and is easy for recruiters to test.
- PostgreSQL is used to demonstrate relational modeling and SQL analytics contracts.
- SQL views provide a stable semantic layer for Power BI.
- FastAPI is intentionally lightweight and focused on read-only analytics endpoints.
- Data-quality checks are documented in business terms to show how technical validation supports trust.

