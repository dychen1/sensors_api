from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime

add_successful_response = JSONResponse(content={"message": "successfully added items!"}, status_code=200)
delete_successful_response = JSONResponse(content={"message": "successfully deleted sensor!"}, status_code=200)
db_error_response = JSONResponse(content={"message": "Error when queryin database!"}, status_code=500)
unknown_error_response = JSONResponse(content={"message": "Unknown error!"}, status_code=502)


class DailyAggregationResponse(BaseModel):
    min_val: float
    max_val: float
    q1: float
    median: float
    q3: float
    unit: str


class SensorResponse(BaseModel):
    id: str
    name: str
    type: str
    unit: str
    location: str
    active: bool
    activation_date: datetime
    updated_at: datetime
    updated_by: str


class SensorValueResponse(BaseModel):
    values: list[float]
    unit: str
