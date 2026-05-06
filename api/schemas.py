from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExecutiveKPI(BaseModel):
    total_consumption: float
    active_meters: int
    reading_success_rate: float
    missing_reading_percentage: float
    anomaly_count: int
    critical_meter_count: int
    latest_reading_timestamp: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MeterSummary(BaseModel):
    meter_id: str
    customer_id: str
    region_name: str
    meter_type: str
    status: str
    health_status: Optional[str] = None
    health_score: Optional[float] = None
    missing_reading_count_30d: Optional[int] = None
    anomaly_count_30d: Optional[int] = None
    data_freshness_hours: Optional[float] = None


class MeterDetail(MeterSummary):
    customer_type: Optional[str] = None
    latest_reading_timestamp: Optional[str] = None
    latest_consumption_value: Optional[float] = None
    total_consumption: Optional[float] = None
    reading_count: int = 0


class RegionQuality(BaseModel):
    region_name: str
    total_meters: int
    active_meters: int
    missing_reading_percentage: float
    anomaly_count: int
    avg_health_score: Optional[float] = None
    critical_meter_count: int


class AnomalySummary(BaseModel):
    meter_id: str
    region_name: str
    meter_type: str
    reading_timestamp: str
    consumption_value: Optional[float] = None
    customer_type: str
    anomaly_reason: str


class DataQualityEvent(BaseModel):
    event_id: str
    meter_id: Optional[str] = None
    date_key: Optional[int] = None
    event_type: str
    severity: str
    description: str
    detected_at: str

