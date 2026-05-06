from __future__ import annotations

from python.clean_data import clean_dataset
from python.config import Settings
from python.generate_synthetic_data import generate_synthetic_data


def small_settings() -> Settings:
    return Settings(
        num_customers=30,
        num_meters=36,
        start_date="2025-01-01",
        end_date="2025-01-31",
        random_seed=7,
        missing_reading_rate=0.05,
        duplicate_reading_rate=0.02,
        anomaly_rate=0.03,
        inactive_meter_rate=0.05,
        estimated_reading_rate=0.05,
    )


def test_generated_data_has_expected_columns() -> None:
    result = generate_synthetic_data(small_settings())
    readings = result.datasets["fact_meter_reading"]

    assert set(
        [
            "reading_id",
            "meter_id",
            "date_key",
            "reading_timestamp",
            "consumption_value",
            "is_missing",
            "is_estimated",
            "is_anomaly",
            "ingestion_timestamp",
        ]
    ).issubset(readings.columns)


def test_customer_and_meter_ids_are_unique() -> None:
    result = generate_synthetic_data(small_settings())

    assert result.datasets["dim_customer"]["customer_id"].is_unique
    assert result.datasets["dim_meter"]["meter_id"].is_unique


def test_generated_readings_contain_missing_and_anomaly_flags() -> None:
    result = generate_synthetic_data(small_settings())
    readings = result.datasets["fact_meter_reading"]

    assert readings["is_missing"].any()
    assert readings["is_anomaly"].any()


def test_health_scores_are_between_zero_and_one_hundred() -> None:
    result = generate_synthetic_data(small_settings())
    cleaned = clean_dataset(result.datasets)
    health = cleaned["fact_meter_health"]

    assert health["health_score"].between(0, 100, inclusive="both").all()

