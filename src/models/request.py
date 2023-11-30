from pydantic import BaseModel
from datetime import datetime


class SensorRequest(BaseModel):
    id: str
    name: str
    type: str
    unit: str
    location: str
    active: bool
    activation_date: datetime
    updated_by: str
    updated_at: datetime | None = None  # Can fallback to default database model value (datetime.utcnow())


class SensorValueRequest(BaseModel):
    sensor_id: str
    value: float
    creation_date: datetime
