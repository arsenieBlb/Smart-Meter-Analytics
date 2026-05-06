# Data Dictionary

## dim_date

| Column | Type | Description |
|---|---|---|
| date_key | Integer | Primary key in `YYYYMMDD` format. |
| full_date | Date | Calendar date. |
| day | Integer | Day of month. |
| week | Integer | ISO week number. |
| month | Integer | Month number. |
| month_name | Text | Month name. |
| quarter | Integer | Calendar quarter. |
| year | Integer | Calendar year. |
| is_weekend | Boolean | True when the date is Saturday or Sunday. |

## dim_region

| Column | Type | Description |
|---|---|---|
| region_id | Integer | Primary key for the region. |
| region_name | Text | Danish city or region name. |
| country | Text | Country, default `Denmark`. |

## dim_customer

| Column | Type | Description |
|---|---|---|
| customer_id | Text | Primary key for the customer. |
| customer_name | Text | Synthetic customer display name. |
| customer_type | Text | Residential, Commercial, or Industrial. |
| region_id | Integer | Foreign key to `dim_region`. |
| city | Text | Customer city. |
| signup_date | Date | Date the customer joined the utility. |

## dim_meter

| Column | Type | Description |
|---|---|---|
| meter_id | Text | Primary key for the smart meter. |
| customer_id | Text | Foreign key to `dim_customer`. |
| meter_type | Text | Electricity, Water, or Heat. |
| installation_date | Date | Date the meter was installed. |
| status | Text | Active or Inactive. |
| expected_readings_per_day | Integer | Expected daily reading count. Default is 1. |

## fact_meter_reading

| Column | Type | Description |
|---|---|---|
| reading_id | Text | Primary key for the reading record. |
| meter_id | Text | Foreign key to `dim_meter`. |
| date_key | Integer | Foreign key to `dim_date`. |
| reading_timestamp | Timestamp | Time the reading was captured. |
| consumption_value | Numeric | Consumption amount. Null when the reading is missing. |
| is_missing | Boolean | True when the expected reading was not received. |
| is_estimated | Boolean | True when the value is estimated. |
| is_anomaly | Boolean | True when the reading is an abnormal spike. |
| ingestion_timestamp | Timestamp | Time the reading arrived in the platform. |

## fact_meter_health

| Column | Type | Description |
|---|---|---|
| health_id | Text | Primary key for the meter health snapshot. |
| meter_id | Text | Foreign key to `dim_meter`. |
| date_key | Integer | Snapshot date key. |
| latest_reading_timestamp | Timestamp | Most recent non-missing reading for the meter. |
| missing_reading_count_30d | Integer | Missing reading count in the latest 30-day window. |
| anomaly_count_30d | Integer | Anomaly count in the latest 30-day window. |
| data_freshness_hours | Numeric | Hours since the latest non-missing reading. |
| health_status | Text | Healthy, Watch, Critical, or Inactive. |
| health_score | Numeric | Score from 0 to 100. |

## fact_data_quality_event

| Column | Type | Description |
|---|---|---|
| event_id | Text | Primary key for the data-quality event. |
| meter_id | Text | Nullable foreign key to `dim_meter`. |
| date_key | Integer | Nullable foreign key to `dim_date`. |
| event_type | Text | Missing Reading, Duplicate Reading, Abnormal Spike, Delayed Reading, Inactive Meter, or Negative Consumption. |
| severity | Text | Info, Low, Medium, High, or Critical. |
| description | Text | Business-readable explanation of the issue. |
| detected_at | Timestamp | Time the event was detected by the pipeline. |

