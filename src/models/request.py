from pydantic import BaseModel
from datetime import datetime


class SensorRequest(BaseModel):
    id: str
    name: str
    type: str
    location: str
    active: bool
    activation_date: datetime
    updated_by: str
    updated_at: datetime | None = None  # Can fallback to default database model value (datetime.utcnow())


class SensorValueRequest(BaseModel):
    sensor_id: str
    value: float
    unit: str
    creation_date: datetime
