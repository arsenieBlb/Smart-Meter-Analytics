from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.engine import Connection

from api.database import get_db
from api.schemas import MeterDetail, MeterSummary
from api.services.meter_service import fetch_meter_detail, fetch_meters


router = APIRouter(prefix="/api/meters", tags=["Meters"])


@router.get("", response_model=list[MeterSummary])
def get_meters(
    meter_type: str | None = Query(default=None),
    region: str | None = Query(default=None),
    health_status: str | None = Query(default=None),
    db: Connection | None = Depends(get_db),
) -> list[dict[str, object]]:
    return fetch_meters(db, meter_type=meter_type, region=region, health_status=health_status)


@router.get("/{meter_id}", response_model=MeterDetail)
def get_meter(meter_id: str, db: Connection | None = Depends(get_db)) -> dict[str, object]:
    meter = fetch_meter_detail(db, meter_id)
    if meter is None:
        raise HTTPException(status_code=404, detail=f"Meter {meter_id} was not found.")
    return meter

