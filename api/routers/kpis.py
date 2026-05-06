from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection

from api.database import get_db
from api.schemas import ExecutiveKPI
from api.services.kpi_service import fetch_executive_kpis


router = APIRouter(prefix="/api", tags=["KPIs"])


@router.get("/kpis", response_model=ExecutiveKPI)
def get_kpis(db: Connection | None = Depends(get_db)) -> dict[str, object]:
    return fetch_executive_kpis(db)

