from __future__ import annotations

from functools import lru_cache
from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - helps static inspection before deps are installed
    from pydantic import BaseSettings  # type: ignore

    SettingsConfigDict = dict  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime settings for the offline pipeline, API, and PostgreSQL loader."""

    project_name: str = "Smart Meter Analytics"

    postgres_db: str = "smart_utility"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    db_schema: str = "utility"
    load_to_postgres: bool = False

    num_customers: int = 1_000
    num_meters: int = 1_200
    start_date: str = "2025-01-01"
    end_date: str = "2025-12-31"
    random_seed: int = 42

    missing_reading_rate: float = 0.035
    duplicate_reading_rate: float = 0.0075
    anomaly_rate: float = 0.015
    inactive_meter_rate: float = 0.04
    estimated_reading_rate: float = 0.06
    delayed_reading_rate: float = 0.03

    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    sample_export_dir: Path = PROJECT_ROOT / "data" / "sample_exports"
    sql_dir: Path = PROJECT_ROOT / "sql"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            "postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
