from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

try:
    from .config import Settings, get_settings
except ImportError:  # pragma: no cover
    from config import Settings, get_settings  # type: ignore


DANISH_REGIONS = ["Aarhus", "Horsens", "Skanderborg", "Vejle", "Odense", "Copenhagen"]
CUSTOMER_TYPES = ["Residential", "Commercial", "Industrial"]
METER_TYPES = ["Electricity", "Water", "Heat"]


BASE_CONSUMPTION = {
    ("Residential", "Electricity"): 9.5,
    ("Residential", "Water"): 0.42,
    ("Residential", "Heat"): 18.0,
    ("Commercial", "Electricity"): 48.0,
    ("Commercial", "Water"): 2.9,
    ("Commercial", "Heat"): 95.0,
    ("Industrial", "Electricity"): 240.0,
    ("Industrial", "Water"): 15.0,
    ("Industrial", "Heat"): 420.0,
}


@dataclass(frozen=True)
class SyntheticDataResult:
    datasets: dict[str, pd.DataFrame]
    metadata: dict[str, Any]


def create_date_dimension(start_date: str, end_date: str) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    return pd.DataFrame(
        {
            "date_key": dates.strftime("%Y%m%d").astype(int),
            "full_date": dates.date.astype(str),
            "day": dates.day,
            "week": dates.isocalendar().week.astype(int),
            "month": dates.month,
            "month_name": dates.strftime("%B"),
            "quarter": dates.quarter,
            "year": dates.year,
            "is_weekend": dates.dayofweek >= 5,
        }
    )


def _create_regions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region_id": range(1, len(DANISH_REGIONS) + 1),
            "region_name": DANISH_REGIONS,
            "country": "Denmark",
        }
    )


def _random_dates(
    rng: np.random.Generator,
    start: pd.Timestamp,
    end: pd.Timestamp,
    size: int,
) -> list[str]:
    total_days = max((end - start).days, 1)
    offsets = rng.integers(0, total_days + 1, size=size)
    return [(start + pd.Timedelta(days=int(offset))).date().isoformat() for offset in offsets]


def _create_customers(settings: Settings, regions: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    customer_types = rng.choice(CUSTOMER_TYPES, size=settings.num_customers, p=[0.76, 0.19, 0.05])
    region_ids = rng.choice(regions["region_id"], size=settings.num_customers)
    city_lookup = regions.set_index("region_id")["region_name"].to_dict()
    signup_dates = _random_dates(
        rng,
        pd.Timestamp("2018-01-01"),
        pd.Timestamp(settings.start_date) - pd.Timedelta(days=1),
        settings.num_customers,
    )

    return pd.DataFrame(
        {
            "customer_id": [f"CUST{i:06d}" for i in range(1, settings.num_customers + 1)],
            "customer_name": [f"Customer {i:06d}" for i in range(1, settings.num_customers + 1)],
            "customer_type": customer_types,
            "region_id": region_ids,
            "city": [city_lookup[int(region_id)] for region_id in region_ids],
            "signup_date": signup_dates,
        }
    )


def _create_meters(settings: Settings, customers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    customer_ids = rng.choice(customers["customer_id"], size=settings.num_meters, replace=True)
    meter_types = rng.choice(METER_TYPES, size=settings.num_meters, p=[0.55, 0.25, 0.20])
    inactive_count = max(1, int(round(settings.num_meters * settings.inactive_meter_rate)))
    statuses = np.array(["Active"] * settings.num_meters, dtype=object)
    statuses[rng.choice(settings.num_meters, size=inactive_count, replace=False)] = "Inactive"
    installation_dates = _random_dates(
        rng,
        pd.Timestamp("2019-01-01"),
        pd.Timestamp(settings.start_date),
        settings.num_meters,
    )

    return pd.DataFrame(
        {
            "meter_id": [f"MTR{i:06d}" for i in range(1, settings.num_meters + 1)],
            "customer_id": customer_ids,
            "meter_type": meter_types,
            "installation_date": installation_dates,
            "status": statuses,
            "expected_readings_per_day": 1,
        }
    )


def _seasonality_factor(meter_type: str, month: int) -> float:
    if meter_type == "Heat":
        return {12: 1.45, 1: 1.55, 2: 1.45, 3: 1.25, 4: 0.95, 5: 0.65, 6: 0.35, 7: 0.25, 8: 0.30, 9: 0.55, 10: 0.90, 11: 1.20}[month]
    if meter_type == "Electricity":
        return 1.12 if month in {11, 12, 1, 2} else 0.96 if month in {6, 7, 8} else 1.0
    return 1.0


def _consumption_value(
    rng: np.random.Generator,
    customer_type: str,
    meter_type: str,
    month: int,
    is_anomaly: bool,
) -> float:
    base = BASE_CONSUMPTION[(customer_type, meter_type)]
    seasonal = _seasonality_factor(meter_type, month)
    noise = rng.lognormal(mean=0.0, sigma=0.22)
    value = base * seasonal * noise
    if is_anomaly:
        value *= float(rng.uniform(3.0, 7.0))
    return round(max(value, 0.001), 3)


def _ensure_at_least_one_flag(readings: pd.DataFrame, column: str, rng: np.random.Generator) -> None:
    if len(readings) > 0 and not bool(readings[column].any()):
        index = int(rng.integers(0, len(readings)))
        readings.loc[index, column] = True


def _create_readings(
    settings: Settings,
    dim_date: pd.DataFrame,
    customers: pd.DataFrame,
    meters: pd.DataFrame,
    rng: np.random.Generator,
) -> tuple[pd.DataFrame, int]:
    customer_type_lookup = customers.set_index("customer_id")["customer_type"].to_dict()
    active_meters = meters[meters["status"] == "Active"].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    reading_number = 1

    for meter in active_meters.itertuples(index=False):
        customer_type = customer_type_lookup[meter.customer_id]
        for date in dim_date.itertuples(index=False):
            is_missing = bool(rng.random() < settings.missing_reading_rate)
            is_anomaly = bool((not is_missing) and rng.random() < settings.anomaly_rate)
            is_estimated = bool((not is_missing) and rng.random() < settings.estimated_reading_rate)
            reading_time = datetime.combine(pd.Timestamp(date.full_date).date(), datetime.min.time())
            reading_time += timedelta(hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60)))

            delay_hours = float(rng.uniform(0.2, 8.0))
            if rng.random() < settings.delayed_reading_rate:
                delay_hours = float(rng.uniform(24.0, 96.0))
            ingestion_time = reading_time + timedelta(hours=delay_hours)

            rows.append(
                {
                    "reading_id": f"READ{reading_number:09d}",
                    "meter_id": meter.meter_id,
                    "date_key": int(date.date_key),
                    "reading_timestamp": reading_time.isoformat(sep=" "),
                    "consumption_value": np.nan
                    if is_missing
                    else _consumption_value(rng, customer_type, meter.meter_type, int(date.month), is_anomaly),
                    "is_missing": is_missing,
                    "is_estimated": is_estimated,
                    "is_anomaly": is_anomaly,
                    "ingestion_timestamp": ingestion_time.isoformat(sep=" "),
                }
            )
            reading_number += 1

    readings = pd.DataFrame(rows)
    _ensure_at_least_one_flag(readings, "is_missing", rng)
    _ensure_at_least_one_flag(readings, "is_anomaly", rng)
    _ensure_at_least_one_flag(readings, "is_estimated", rng)

    duplicate_count = max(1, int(round(len(readings) * settings.duplicate_reading_rate)))
    duplicate_indexes = rng.choice(readings.index, size=duplicate_count, replace=False)
    duplicate_rows = readings.loc[duplicate_indexes].copy()
    duplicate_rows["reading_id"] = [
        f"READ{reading_number + idx:09d}" for idx in range(len(duplicate_rows))
    ]
    readings = pd.concat([readings, duplicate_rows], ignore_index=True)

    return readings, duplicate_count


def generate_synthetic_data(settings: Settings | None = None) -> SyntheticDataResult:
    settings = settings or get_settings()
    rng = np.random.default_rng(settings.random_seed)

    dim_date = create_date_dimension(settings.start_date, settings.end_date)
    dim_region = _create_regions()
    dim_customer = _create_customers(settings, dim_region, rng)
    dim_meter = _create_meters(settings, dim_customer, rng)
    readings, duplicate_count = _create_readings(settings, dim_date, dim_customer, dim_meter, rng)

    return SyntheticDataResult(
        datasets={
            "dim_date": dim_date,
            "dim_region": dim_region,
            "dim_customer": dim_customer,
            "dim_meter": dim_meter,
            "fact_meter_reading": readings,
        },
        metadata={"duplicate_records_created": duplicate_count},
    )


if __name__ == "__main__":
    result = generate_synthetic_data()
    for dataset_name, dataframe in result.datasets.items():
        print(f"{dataset_name}: {len(dataframe):,} rows")

