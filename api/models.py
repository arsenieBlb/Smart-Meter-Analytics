from __future__ import annotations

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DimDate(Base):
    __tablename__ = "dim_date"
    __table_args__ = {"schema": "utility"}

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_date: Mapped[str] = mapped_column(Date)
    day: Mapped[int] = mapped_column(Integer)
    week: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    month_name: Mapped[str] = mapped_column(String(20))
    quarter: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    is_weekend: Mapped[bool] = mapped_column(Boolean)


class DimRegion(Base):
    __tablename__ = "dim_region"
    __table_args__ = {"schema": "utility"}

    region_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_name: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))


class DimCustomer(Base):
    __tablename__ = "dim_customer"
    __table_args__ = {"schema": "utility"}

    customer_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(150))
    customer_type: Mapped[str] = mapped_column(String(30))
    region_id: Mapped[int] = mapped_column(ForeignKey("utility.dim_region.region_id"))
    city: Mapped[str] = mapped_column(String(100))
    signup_date: Mapped[str] = mapped_column(Date)


class DimMeter(Base):
    __tablename__ = "dim_meter"
    __table_args__ = {"schema": "utility"}

    meter_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("utility.dim_customer.customer_id"))
    meter_type: Mapped[str] = mapped_column(String(30))
    installation_date: Mapped[str] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20))
    expected_readings_per_day: Mapped[int] = mapped_column(Integer)


class FactMeterReading(Base):
    __tablename__ = "fact_meter_reading"
    __table_args__ = {"schema": "utility"}

    reading_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    meter_id: Mapped[str] = mapped_column(ForeignKey("utility.dim_meter.meter_id"))
    date_key: Mapped[int] = mapped_column(ForeignKey("utility.dim_date.date_key"))
    reading_timestamp: Mapped[str] = mapped_column(DateTime)
    consumption_value: Mapped[float | None] = mapped_column(Numeric(14, 3))
    is_missing: Mapped[bool] = mapped_column(Boolean)
    is_estimated: Mapped[bool] = mapped_column(Boolean)
    is_anomaly: Mapped[bool] = mapped_column(Boolean)
    ingestion_timestamp: Mapped[str] = mapped_column(DateTime)


class FactMeterHealth(Base):
    __tablename__ = "fact_meter_health"
    __table_args__ = {"schema": "utility"}

    health_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    meter_id: Mapped[str] = mapped_column(ForeignKey("utility.dim_meter.meter_id"))
    date_key: Mapped[int] = mapped_column(ForeignKey("utility.dim_date.date_key"))
    latest_reading_timestamp: Mapped[str | None] = mapped_column(DateTime)
    missing_reading_count_30d: Mapped[int] = mapped_column(Integer)
    anomaly_count_30d: Mapped[int] = mapped_column(Integer)
    data_freshness_hours: Mapped[float] = mapped_column(Numeric(12, 2))
    health_status: Mapped[str] = mapped_column(String(20))
    health_score: Mapped[float] = mapped_column(Numeric(5, 2))


class FactDataQualityEvent(Base):
    __tablename__ = "fact_data_quality_event"
    __table_args__ = {"schema": "utility"}

    event_id: Mapped[str] = mapped_column(String(30), primary_key=True)
    meter_id: Mapped[str | None] = mapped_column(ForeignKey("utility.dim_meter.meter_id"))
    date_key: Mapped[int | None] = mapped_column(ForeignKey("utility.dim_date.date_key"))
    event_type: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[str] = mapped_column(DateTime)

