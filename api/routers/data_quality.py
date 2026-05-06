from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection

from api.database import get_db
from api.schemas import DataQualityEvent
from api.services.data_quality_service import fetch_data_quality_events


router = APIRouter(prefix="/api/data-quality", tags=["Data Quality"])


@router.get("/events", response_model=list[DataQualityEvent])
def get_data_quality_events(
    limit: int = Query(default=250, ge=1, le=1_000),
    db: Connection | None = Depends(get_db),
) -> list[dict[str, object]]:
    return fetch_data_quality_events(db, limit=limit)

