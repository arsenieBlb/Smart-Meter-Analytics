from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping

import numpy as np
import pandas as pd


def detect_duplicate_readings(readings: pd.DataFrame) -> pd.DataFrame:
    return readings[readings.duplicated(subset=["meter_id", "reading_timestamp"], keep=False)].copy()


def detect_negative_consumption(readings: pd.DataFrame) -> pd.DataFrame:
    return readings[readings["consumption_value"].fillna(0) < 0].copy()


def _standardize_boolean_columns(readings: pd.DataFrame) -> pd.DataFrame:
    for column in ["is_missing", "is_estimated", "is_anomaly"]:
        readings[column] = readings[column].fillna(False).astype(bool)
    return readings


def _calculate_meter_health(
    dim_meter: pd.DataFrame,
    dim_date: pd.DataFrame,
    readings: pd.DataFrame,
) -> pd.DataFrame:
    max_date_key = int(dim_date["date_key"].max())
    end_date = pd.to_datetime(dim_date["full_date"].max())
    reference_timestamp = end_date + pd.Timedelta(days=1)
    last_30_date_keys = set(dim_date.sort_values("full_date").tail(30)["date_key"].astype(int))

    readings_for_health = readings.copy()
    readings_for_health["reading_timestamp"] = pd.to_datetime(readings_for_health["reading_timestamp"])
    last_30 = readings_for_health[readings_for_health["date_key"].astype(int).isin(last_30_date_keys)]

    rows: list[dict[str, Any]] = []
    for idx, meter in enumerate(dim_meter.itertuples(index=False), start=1):
        meter_readings = readings_for_health[readings_for_health["meter_id"] == meter.meter_id]
        meter_last_30 = last_30[last_30["meter_id"] == meter.meter_id]
        latest_non_missing = meter_readings[~meter_readings["is_missing"]]["reading_timestamp"].max()
        missing_30d = int(meter_last_30["is_missing"].sum())
        anomaly_30d = int(meter_last_30["is_anomaly"].sum())

        if pd.isna(latest_non_missing):
            freshness_hours = 9999.0
        else:
            freshness_hours = round(
                max((reference_timestamp - latest_non_missing).total_seconds() / 3600, 0),
                2,
            )

        if meter.status == "Inactive":
            health_status = "Inactive"
            health_score = 25
        else:
            freshness_penalty = min(freshness_hours / 4, 25)
            health_score = round(
                max(0, min(100, 100 - (missing_30d * 7.0) - (anomaly_30d * 15.0) - freshness_penalty)),
                1,
            )
            if health_score >= 80:
                health_status = "Healthy"
            elif health_score >= 60:
                health_status = "Watch"
            else:
                health_status = "Critical"

        rows.append(
            {
                "health_id": f"HLTH{idx:06d}",
                "meter_id": meter.meter_id,
                "date_key": max_date_key,
                "latest_reading_timestamp": None
                if pd.isna(latest_non_missing)
                else latest_non_missing.isoformat(sep=" "),
                "missing_reading_count_30d": missing_30d,
                "anomaly_count_30d": anomaly_30d,
                "data_freshness_hours": freshness_hours,
                "health_status": health_status,
                "health_score": health_score,
            }
        )

    return pd.DataFrame(rows)


def _create_quality_events(
    dim_meter: pd.DataFrame,
    dim_date: pd.DataFrame,
    readings: pd.DataFrame,
) -> pd.DataFrame:
    events: list[dict[str, Any]] = []
    detected_at = datetime.now(UTC).replace(tzinfo=None, microsecond=0).isoformat(sep=" ")
    latest_date_key = int(dim_date["date_key"].max())

    def add_event(
        meter_id: str | None,
        date_key: int | None,
        event_type: str,
        severity: str,
        description: str,
    ) -> None:
        events.append(
            {
                "event_id": f"DQE{len(events) + 1:08d}",
                "meter_id": meter_id,
                "date_key": date_key,
                "event_type": event_type,
                "severity": severity,
                "description": description,
                "detected_at": detected_at,
            }
        )

    for row in readings[readings["is_missing"]].itertuples(index=False):
        add_event(row.meter_id, int(row.date_key), "Missing Reading", "Medium", "Expected daily meter reading was not received.")

    for row in readings[readings["is_anomaly"]].itertuples(index=False):
        add_event(row.meter_id, int(row.date_key), "Abnormal Spike", "High", "Consumption value is materially above the expected range for this meter.")

    duplicates = detect_duplicate_readings(readings)
    for row in duplicates.itertuples(index=False):
        add_event(row.meter_id, int(row.date_key), "Duplicate Reading", "High", "Multiple records exist for the same meter and timestamp.")

    negatives = detect_negative_consumption(readings)
    for row in negatives.itertuples(index=False):
        add_event(row.meter_id, int(row.date_key), "Negative Consumption", "Critical", "Consumption value is below zero and cannot be used for reporting.")

    timestamps = readings.copy()
    timestamps["reading_timestamp"] = pd.to_datetime(timestamps["reading_timestamp"])
    timestamps["ingestion_timestamp"] = pd.to_datetime(timestamps["ingestion_timestamp"])
    delayed = timestamps[(timestamps["ingestion_timestamp"] - timestamps["reading_timestamp"]) > pd.Timedelta(hours=24)]
    for row in delayed.itertuples(index=False):
        add_event(row.meter_id, int(row.date_key), "Delayed Reading", "Low", "Reading arrived more than 24 hours after it was captured.")

    for row in dim_meter[dim_meter["status"] == "Inactive"].itertuples(index=False):
        add_event(row.meter_id, latest_date_key, "Inactive Meter", "Info", "Meter is inactive and excluded from active-meter KPI counts.")

    return pd.DataFrame(events)


def clean_dataset(datasets: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    cleaned = {name: dataframe.copy() for name, dataframe in datasets.items()}

    readings = cleaned["fact_meter_reading"]
    readings = _standardize_boolean_columns(readings)
    readings["consumption_value"] = pd.to_numeric(readings["consumption_value"], errors="coerce")
    readings.loc[readings["is_missing"], "consumption_value"] = np.nan
    readings["date_key"] = readings["date_key"].astype(int)
    cleaned["fact_meter_reading"] = readings

    cleaned["fact_meter_health"] = _calculate_meter_health(
        cleaned["dim_meter"],
        cleaned["dim_date"],
        readings,
    )
    cleaned["fact_data_quality_event"] = _create_quality_events(
        cleaned["dim_meter"],
        cleaned["dim_date"],
        readings,
    )
    return cleaned


def validate_dataset(datasets: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    readings = datasets["fact_meter_reading"]
    meters = datasets["dim_meter"]
    customers = datasets["dim_customer"]
    health = datasets.get("fact_meter_health", pd.DataFrame())

    checks = [
        ("duplicate_readings", len(detect_duplicate_readings(readings))),
        ("negative_consumption", len(detect_negative_consumption(readings))),
        ("invalid_meter_ids", int((~readings["meter_id"].isin(meters["meter_id"])).sum())),
        ("invalid_customer_ids", int((~meters["customer_id"].isin(customers["customer_id"])).sum())),
        (
            "health_score_range",
            0
            if health.empty
            else int((~health["health_score"].between(0, 100, inclusive="both")).sum()),
        ),
    ]

    return pd.DataFrame(
        {
            "check_name": [name for name, _ in checks],
            "failed_records": [failed for _, failed in checks],
            "status": ["PASS" if failed == 0 else "FAIL" for _, failed in checks],
        }
    )
