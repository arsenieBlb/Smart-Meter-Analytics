from __future__ import annotations

from fastapi import FastAPI

from api.routers import anomalies, data_quality, kpis, meters, regions
from python.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    description="Analytics API for synthetic smart-meter consumption, meter health, and data-quality KPIs.",
    version="1.0.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": settings.project_name,
        "status": "healthy",
        "docs": "/docs",
    }


app.include_router(kpis.router)
app.include_router(meters.router)
app.include_router(regions.router)
app.include_router(anomalies.router)
app.include_router(data_quality.router)

