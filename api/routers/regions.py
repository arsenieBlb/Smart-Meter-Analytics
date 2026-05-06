from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.engine import Connection

from api.database import get_db
from api.schemas import RegionQuality
from api.services.data_quality_service import fetch_region_quality


router = APIRouter(prefix="/api/regions", tags=["Regions"])


@router.get("/quality", response_model=list[RegionQuality])
def get_region_quality(db: Connection | None = Depends(get_db)) -> list[dict[str, object]]:
    return fetch_region_quality(db)

