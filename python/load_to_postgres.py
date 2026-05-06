from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

try:
    from .config import Settings, get_settings
except ImportError:  # pragma: no cover
    from config import Settings, get_settings  # type: ignore


LOAD_ORDER = [
    "dim_date",
    "dim_region",
    "dim_customer",
    "dim_meter",
    "fact_meter_reading",
    "fact_meter_health",
    "fact_data_quality_event",
]


def create_postgres_engine(settings: Settings | None = None) -> Engine:
    settings = settings or get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def execute_sql_file(engine: Engine, sql_file: Path) -> None:
    sql = sql_file.read_text(encoding="utf-8")
    with engine.begin() as connection:
        connection.execute(text(sql))


def prepare_database(engine: Engine, settings: Settings) -> None:
    execute_sql_file(engine, settings.sql_dir / "01_create_schema.sql")
    execute_sql_file(engine, settings.sql_dir / "02_create_tables.sql")


def create_views(engine: Engine, settings: Settings) -> None:
    execute_sql_file(engine, settings.sql_dir / "03_create_views.sql")


def truncate_tables(engine: Engine, settings: Settings) -> None:
    table_list = ", ".join(f"{settings.db_schema}.{table}" for table in reversed(LOAD_ORDER))
    with engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE;"))


def load_csvs_to_postgres(
    processed_dir: Path | None = None,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    processed_dir = processed_dir or settings.processed_data_dir
    engine = create_postgres_engine(settings)
    prepare_database(engine, settings)
    truncate_tables(engine, settings)

    for table in LOAD_ORDER:
        csv_path = processed_dir / f"{table}.csv"
        dataframe = pd.read_csv(csv_path)
        dataframe.to_sql(table, engine, schema=settings.db_schema, if_exists="append", index=False, method="multi", chunksize=5_000)

    create_views(engine, settings)


if __name__ == "__main__":
    load_csvs_to_postgres()
    print("CSV files loaded into PostgreSQL.")

