from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd


def ensure_directories(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def write_dataframes_to_csv(
    datasets: Mapping[str, pd.DataFrame],
    output_dir: Path,
    sample_dir: Path | None = None,
    sample_size: int = 250,
) -> dict[str, Path]:
    ensure_directories(output_dir)
    if sample_dir is not None:
        ensure_directories(sample_dir)

    written_paths: dict[str, Path] = {}
    for name, dataframe in datasets.items():
        path = output_dir / f"{name}.csv"
        dataframe.to_csv(path, index=False)
        written_paths[name] = path

        if sample_dir is not None:
            sample_path = sample_dir / f"{name}_sample.csv"
            dataframe.head(sample_size).to_csv(sample_path, index=False)

    return written_paths


def summarize_dataset(datasets: Mapping[str, pd.DataFrame], duplicates_created: int = 0) -> dict[str, int]:
    readings = datasets["fact_meter_reading"]
    return {
        "customers_generated": len(datasets["dim_customer"]),
        "meters_generated": len(datasets["dim_meter"]),
        "readings_generated": len(readings),
        "missing_readings": int(readings["is_missing"].sum()),
        "anomalies": int(readings["is_anomaly"].sum()),
        "duplicate_records_created": duplicates_created,
        "data_quality_events": len(datasets.get("fact_data_quality_event", pd.DataFrame())),
    }

