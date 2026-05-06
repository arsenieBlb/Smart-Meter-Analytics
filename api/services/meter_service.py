from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from api.services.csv_fallback import read_processed_csv


def fetch_meters(
    db: Connection | None,
    meter_type: str | None = None,
    region: str | None = None,
    health_status: str | None = None,
    limit: int = 250,
) -> list[dict[str, object]]:
    if db is not None:
        try:
            conditions: list[str] = []
            params: dict[str, object] = {"limit": limit}
            if meter_type:
                conditions.append("meter_type = :meter_type")
                params["meter_type"] = meter_type
            if region:
                conditions.append("region_name = :region")
                params["region"] = region
            if health_status:
                conditions.append("health_status = :health_status")
                params["health_status"] = health_status
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            rows = db.execute(
                text(f"SELECT * FROM utility.vw_meter_health {where_clause} ORDER BY health_score ASC NULLS LAST LIMIT :limit"),
                params,
            ).mappings().all()
            return [dict(row) for row in rows]
        except SQLAlchemyError:
            pass

    meters = read_processed_csv("dim_meter")
    customers = read_processed_csv("dim_customer")
    regions = read_processed_csv("dim_region")
    health = read_processed_csv("fact_meter_health")
    if meters.empty:
        return []
    merged = meters.merge(customers[["customer_id", "region_id"]], on="customer_id", how="left")
    merged = merged.merge(regions[["region_id", "region_name"]], on="region_id", how="left")
    if not health.empty:
        merged = merged.merge(
            health[
                [
                    "meter_id",
                    "health_status",
                    "health_score",
                    "missing_reading_count_30d",
                    "anomaly_count_30d",
                    "data_freshness_hours",
                ]
            ],
            on="meter_id",
            how="left",
        )
    if meter_type:
        merged = merged[merged["meter_type"] == meter_type]
    if region:
        merged = merged[merged["region_name"] == region]
    if health_status and "health_status" in merged:
        merged = merged[merged["health_status"] == health_status]
    selected = merged.head(limit)
    return selected.where(selected.notna(), None).to_dict(orient="records")


def fetch_meter_detail(db: Connection | None, meter_id: str) -> dict[str, object] | None:
    if db is not None:
        try:
            row = db.execute(
                text(
                    """
                    SELECT
                        mh.*,
                        dc.customer_type,
                        latest.reading_timestamp AS latest_reading_timestamp,
                        latest.consumption_value AS latest_consumption_value,
                        COALESCE(summary.total_consumption, 0) AS total_consumption,
                        COALESCE(summary.reading_count, 0) AS reading_count
                    FROM utility.vw_meter_health mh
                    JOIN utility.dim_meter dm ON mh.meter_id = dm.meter_id
                    JOIN utility.dim_customer dc ON dm.customer_id = dc.customer_id
                    LEFT JOIN LATERAL (
                        SELECT reading_timestamp, consumption_value
                        FROM utility.fact_meter_reading fr
                        WHERE fr.meter_id = mh.meter_id AND fr.is_missing = FALSE
                        ORDER BY reading_timestamp DESC
                        LIMIT 1
                    ) latest ON TRUE
                    LEFT JOIN (
                        SELECT meter_id,
                               SUM(consumption_value) FILTER (WHERE is_missing = FALSE) AS total_consumption,
                               COUNT(*) AS reading_count
                        FROM utility.fact_meter_reading
                        GROUP BY meter_id
                    ) summary ON mh.meter_id = summary.meter_id
                    WHERE mh.meter_id = :meter_id
                    """
                ),
                {"meter_id": meter_id},
            ).mappings().first()
            if row:
                data = dict(row)
                for key in ["latest_reading_timestamp"]:
                    if data.get(key) is not None:
                        data[key] = str(data[key])
                return data
        except SQLAlchemyError:
            pass

    meters = fetch_meters(None, limit=100_000)
    selected = next((meter for meter in meters if meter["meter_id"] == meter_id), None)
    if selected is None:
        return None

    readings = read_processed_csv("fact_meter_reading")
    customers = read_processed_csv("dim_customer")
    if not customers.empty:
        customer = customers[customers["customer_id"] == selected["customer_id"]]
        selected["customer_type"] = None if customer.empty else str(customer.iloc[0]["customer_type"])
    meter_readings = readings[(readings["meter_id"] == meter_id) & (~readings["is_missing"])] if not readings.empty else readings
    if meter_readings.empty:
        selected.update(
            {
                "latest_reading_timestamp": None,
                "latest_consumption_value": None,
                "total_consumption": 0.0,
                "reading_count": 0,
            }
        )
    else:
        latest = meter_readings.sort_values("reading_timestamp").iloc[-1]
        selected.update(
            {
                "latest_reading_timestamp": str(latest["reading_timestamp"]),
                "latest_consumption_value": float(latest["consumption_value"]),
                "total_consumption": round(float(meter_readings["consumption_value"].sum()), 3),
                "reading_count": int(len(meter_readings)),
            }
        )
    return selected
