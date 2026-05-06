from __future__ import annotations

from pathlib import Path

import pandas as pd

from python.config import get_settings


def processed_path(name: str) -> Path:
    return get_settings().processed_data_dir / f"{name}.csv"


def read_processed_csv(name: str) -> pd.DataFrame:
    path = processed_path(name)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def empty_kpis() -> dict[str, object]:
    return {
        "total_consumption": 0.0,
        "active_meters": 0,
        "reading_success_rate": 0.0,
        "missing_reading_percentage": 0.0,
        "anomaly_count": 0,
        "critical_meter_count": 0,
        "latest_reading_timestamp": None,
    }

