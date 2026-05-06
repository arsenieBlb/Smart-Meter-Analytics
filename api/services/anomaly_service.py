from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError

from api.services.csv_fallback import read_processed_csv


def fetch_anomalies(db: Connection | None, limit: int = 100) -> list[dict[str, object]]:
    if db is not None:
        try:
            rows = db.execute(
                text("SELECT * FROM utility.vw_anomaly_summary ORDER BY reading_timestamp DESC LIMIT :limit"),
                {"limit": limit},
            ).mappings().all()
            return [{**dict(row), "reading_timestamp": str(row["reading_timestamp"])} for row in rows]
        except SQLAlchemyError:
            pass

    readings = read_processed_csv("fact_meter_reading")
    meters = read_processed_csv("dim_meter")
    customers = read_processed_csv("dim_customer")
    regions = read_processed_csv("dim_region")
    if readings.empty:
        return []
    anomalies = readings[readings["is_anomaly"]].copy()
    if anomalies.empty:
        return []
    anomalies = anomalies.merge(meters[["meter_id", "customer_id", "meter_type"]], on="meter_id", how="left")
    anomalies = anomalies.merge(customers[["customer_id", "region_id", "customer_type"]], on="customer_id", how="left")
    anomalies = anomalies.merge(regions[["region_id", "region_name"]], on="region_id", how="left")
    anomalies["anomaly_reason"] = "Consumption spike above expected range"
    columns = [
        "meter_id",
        "region_name",
        "meter_type",
        "reading_timestamp",
        "consumption_value",
        "customer_type",
        "anomaly_reason",
    ]
    selected = anomalies.sort_values("reading_timestamp", ascending=False).head(limit)[columns]
    return selected.where(selected.notna(), None).to_dict(orient="records")
