from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from api.services.csv_fallback import empty_kpis, read_processed_csv


def fetch_executive_kpis(db: Connection | None) -> dict[str, object]:
    if db is not None:
        try:
            row = db.execute(text("SELECT * FROM utility.vw_executive_kpis")).mappings().first()
            if row:
                data = dict(row)
                if data.get("latest_reading_timestamp") is not None:
                    data["latest_reading_timestamp"] = str(data["latest_reading_timestamp"])
                data.pop("total_meters", None)
                return data
        except SQLAlchemyError:
            pass

    readings = read_processed_csv("fact_meter_reading")
    meters = read_processed_csv("dim_meter")
    health = read_processed_csv("fact_meter_health")
    if readings.empty or meters.empty:
        return empty_kpis()

    total_readings = len(readings)
    missing_count = int(readings["is_missing"].sum())
    latest = readings["reading_timestamp"].max() if "reading_timestamp" in readings else None

    return {
        "total_consumption": round(float(readings["consumption_value"].fillna(0).sum()), 3),
        "active_meters": int((meters["status"] == "Active").sum()),
        "reading_success_rate": round(100 * (total_readings - missing_count) / total_readings, 2) if total_readings else 0.0,
        "missing_reading_percentage": round(100 * missing_count / total_readings, 2) if total_readings else 0.0,
        "anomaly_count": int(readings["is_anomaly"].sum()),
        "critical_meter_count": int((health.get("health_status") == "Critical").sum()) if not health.empty else 0,
        "latest_reading_timestamp": None if latest is None else str(latest),
    }

