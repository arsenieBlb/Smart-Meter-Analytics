from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection

from api.database import get_db
from api.schemas import AnomalySummary
from api.services.anomaly_service import fetch_anomalies


router = APIRouter(prefix="/api", tags=["Anomalies"])


@router.get("/anomalies", response_model=list[AnomalySummary])
def get_anomalies(
    limit: int = Query(default=100, ge=1, le=500),
    db: Connection | None = Depends(get_db),
) -> list[dict[str, object]]:
    return fetch_anomalies(db, limit=limit)

