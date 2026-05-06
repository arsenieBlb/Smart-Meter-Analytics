from __future__ import annotations

import pandas as pd

from python.clean_data import detect_duplicate_readings, detect_negative_consumption


def test_validation_logic_detects_duplicates_and_negative_values() -> None:
    readings = pd.DataFrame(
        [
            {
                "reading_id": "READ1",
                "meter_id": "MTR1",
                "reading_timestamp": "2025-01-01 01:00:00",
                "consumption_value": 12.4,
            },
            {
                "reading_id": "READ2",
                "meter_id": "MTR1",
                "reading_timestamp": "2025-01-01 01:00:00",
                "consumption_value": 12.4,
            },
            {
                "reading_id": "READ3",
                "meter_id": "MTR2",
                "reading_timestamp": "2025-01-01 02:00:00",
                "consumption_value": -1.0,
            },
        ]
    )

    assert len(detect_duplicate_readings(readings)) == 2
    assert len(detect_negative_consumption(readings)) == 1

