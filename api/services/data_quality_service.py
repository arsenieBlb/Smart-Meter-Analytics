from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from api.services.csv_fallback import read_processed_csv


def fetch_region_quality(db: Connection | None) -> list[dict[str, object]]:
    if db is not None:
        try:
            rows = db.execute(text("SELECT * FROM utility.vw_region_data_quality ORDER BY region_name")).mappings().all()
            return [dict(row) for row in rows]
        except SQLAlchemyError:
            pass

    meters = read_processed_csv("dim_meter")
    customers = read_processed_csv("dim_customer")
    regions = read_processed_csv("dim_region")
    readings = read_processed_csv("fact_meter_reading")
    health = read_processed_csv("fact_meter_health")
    if meters.empty or customers.empty or regions.empty:
        return []

    meter_region = meters.merge(customers[["customer_id", "region_id"]], on="customer_id").merge(
        regions[["region_id", "region_name"]], on="region_id"
    )
    reading_region = readings.merge(meter_region[["meter_id", "region_name"]], on="meter_id", how="left") if not readings.empty else readings
    health_region = health.merge(meter_region[["meter_id", "region_name"]], on="meter_id", how="left") if not health.empty else health

    results: list[dict[str, object]] = []
    for region_name, group in meter_region.groupby("region_name"):
        region_readings = reading_region[reading_region["region_name"] == region_name] if not reading_region.empty else reading_region
        region_health = health_region[health_region["region_name"] == region_name] if not health_region.empty else health_region
        missing_pct = round(100 * float(region_readings["is_missing"].sum()) / len(region_readings), 2) if len(region_readings) else 0.0
        results.append(
            {
                "region_name": region_name,
                "total_meters": int(group["meter_id"].nunique()),
                "active_meters": int((group["status"] == "Active").sum()),
                "missing_reading_percentage": missing_pct,
                "anomaly_count": int(region_readings["is_anomaly"].sum()) if not region_readings.empty else 0,
                "avg_health_score": round(float(region_health["health_score"].mean()), 2) if not region_health.empty else None,
                "critical_meter_count": int((region_health["health_status"] == "Critical").sum()) if not region_health.empty else 0,
            }
        )
    return results


def fetch_data_quality_events(db: Connection | None, limit: int = 250) -> list[dict[str, object]]:
    if db is not None:
        try:
            rows = db.execute(
                text(
                    """
                    SELECT event_id, meter_id, date_key, event_type, severity, description, detected_at
                    FROM utility.fact_data_quality_event
                    ORDER BY detected_at DESC, severity DESC
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            ).mappings().all()
            return [{**dict(row), "detected_at": str(row["detected_at"])} for row in rows]
        except SQLAlchemyError:
            pass

    events = read_processed_csv("fact_data_quality_event")
    if events.empty:
        return []
    return events.head(limit).where(events.notna(), None).to_dict(orient="records")

