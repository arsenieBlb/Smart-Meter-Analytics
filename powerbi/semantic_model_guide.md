# Power BI Semantic Model Guide

## Import Data

Preferred PostgreSQL import:

- `utility.dim_date`
- `utility.dim_region`
- `utility.dim_customer`
- `utility.dim_meter`
- `utility.fact_meter_reading`
- `utility.fact_meter_health`
- `utility.fact_data_quality_event`
- Optional reporting views such as `utility.vw_executive_kpis` and `utility.vw_region_data_quality`

CSV import:

- Import all files from `data/processed/`.
- Use the same relationships listed below.

## Relationships

Create these one-to-many relationships:

| From | To | Cardinality | Filter Direction |
|---|---|---|---|
| `dim_date[date_key]` | `fact_meter_reading[date_key]` | 1:* | Single |
| `dim_date[date_key]` | `fact_meter_health[date_key]` | 1:* | Single |
| `dim_date[date_key]` | `fact_data_quality_event[date_key]` | 1:* | Single |
| `dim_region[region_id]` | `dim_customer[region_id]` | 1:* | Single |
| `dim_customer[customer_id]` | `dim_meter[customer_id]` | 1:* | Single |
| `dim_meter[meter_id]` | `fact_meter_reading[meter_id]` | 1:* | Single |
| `dim_meter[meter_id]` | `fact_meter_health[meter_id]` | 1:* | Single |
| `dim_meter[meter_id]` | `fact_data_quality_event[meter_id]` | 1:* | Single |

## Date Table

Mark `dim_date` as the official Date table using `dim_date[full_date]`.

Sort `dim_date[month_name]` by `dim_date[month]`.

## Measures Table

Create a blank table called `Measures` and add all measures from `dax_measures.dax`.

Recommended formatting:

- Percentages: `Missing Reading %`, `Reading Success Rate`, `MoM Consumption Change %`, `Estimated Reading %`
- Whole numbers: `Active Meters`, `Total Meters`, `Anomaly Count`, `Critical Meter Count`
- Decimal values: `Total Consumption`, `Average Daily Consumption`, `Average Health Score`, `Data Freshness Hours`

## Model Cleanup

Hide technical columns from report view:

- Primary and foreign keys used only for relationships
- `reading_id`, `health_id`, `event_id`
- Sort/helper columns that are not useful to business users

Use business-friendly names:

- `Consumption Value`
- `Reading Timestamp`
- `Customer Type`
- `Meter Type`
- `Health Status`
- `Data Freshness Hours`

## Star Schema Guidance

Use dimensions for slicing and facts for measures. Avoid many-to-many relationships. Keep filter direction single unless there is a specific reporting need.

The SQL views can be imported for quick dashboard pages, but the core semantic model should be based on the star schema tables to support reusable DAX measures.

