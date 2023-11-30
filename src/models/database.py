# coding: utf-8
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Float, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String(90), primary_key=True)
    name = Column(String(90), nullable=False)
    type = Column(String(90), nullable=False)
    unit = Column(String(20), nullable=True)
    location = Column(String(120), nullable=False, index=True)
    active = Column(Boolean, nullable=False)
    activation_date = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow())
    updated_by = Column(String(45), nullable=False)

    sensor_values_rel = relationship("SensorValue", back_populates="sensors")


class SensorValue(Base):
    __tablename__ = "sensor_values"

    sensor_id = Column(ForeignKey("sensors.id"), primary_key=True)
    value = Column(Float, nullable=True)  # Assuming that sensors only read float values
    creation_date = Column(DateTime, nullable=False, primary_key=True)

    # Relationship ensures that deleted rows in 'sensors' table will propagate to 'sensor_values'
    sensors_rel = relationship("Sensor", back_populates="sensor_values", cascade="delete")
    __table_args__ = (PrimaryKeyConstraint("sensor_id", "creation_date"), {})
