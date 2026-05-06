from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_power_bi_views_are_defined() -> None:
    sql = (PROJECT_ROOT / "sql" / "03_create_views.sql").read_text(encoding="utf-8")

    for view_name in [
        "vw_executive_kpis",
        "vw_daily_consumption",
        "vw_monthly_consumption",
        "vw_meter_health",
        "vw_region_data_quality",
        "vw_anomaly_summary",
    ]:
        assert view_name in sql


def test_validation_checks_cover_expected_quality_rules() -> None:
    sql = (PROJECT_ROOT / "sql" / "04_validation_checks.sql").read_text(encoding="utf-8")

    for check_name in [
        "duplicate_readings_same_meter_timestamp",
        "negative_consumption_values",
        "invalid_meter_ids",
        "invalid_customer_ids",
        "impossible_future_timestamps",
        "date_table_coverage",
        "fact_table_row_count",
        "active_meters_have_readings",
        "anomaly_count_consistency",
        "health_score_range_0_to_100",
    ]:
        assert check_name in sql

