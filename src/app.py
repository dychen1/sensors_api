import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import numpy as np

from auth import validate_api_key
from models.response import (
    DailyAggregationResponse,
    SensorResponse,
    SensorValueResponse,
    unknown_error_response,
    db_error_response,
    add_successful_response,
    delete_successful_response,
)
from models.request import SensorRequest, SensorValueRequest
from models.database import Sensor
from utils.database_utils import DatabaseUtilities, SessionException


host: str | None = os.getenv("DATABASE_CONTAINER")
database: str | None = os.getenv("MYSQL_DATABASE")
if host is None or database is None:
    raise Exception("Database environment variables not set!")
db_utils = DatabaseUtilities(host, database)

app = FastAPI()
app.middleware("http")(validate_api_key)


@app.get("/sensors", response_model=list[SensorResponse])
async def get_all_sensors() -> list[SensorResponse] | JSONResponse:
    try:
        sensors = db_utils.get_all_sensors()
        return [SensorResponse(**sensor) for sensor in sensors]
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


@app.get("/sensors/{sensor_id}", response_model=SensorResponse)
async def get_sensor_by_id(sensor_id: str) -> SensorResponse | JSONResponse:
    try:
        return SensorResponse(**db_utils.get_sensor_by_id(sensor_id))
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


@app.get("/sensors/{location}", response_model=list[SensorResponse])
async def get_sensor_by_location(location: str) -> list[SensorResponse] | JSONResponse:
    try:
        sensors = db_utils.get_sensor_by_location(location)
        return [SensorResponse(**sensor) for sensor in sensors]
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


@app.get("/sensor_values/{sensor_id}/{date}", response_model=SensorValueResponse)
async def get_sensor_values_by_id_date(sensor_id: str, date: str) -> SensorValueResponse | JSONResponse:
    try:
        formatted_date: str = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")  # Ensure correct format
        sensor_values: list[float] = db_utils.get_sensor_values_by_date(sensor_id, formatted_date)
        return SensorValueResponse(values=sensor_values, unit=db_utils.get_sensor_unit(sensor_id))
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


@app.get("/daily_aggregations/{sensor_id}/{date}", response_model=DailyAggregationResponse)
async def get_daily_aggregations(sensor_id: str, date: str) -> DailyAggregationResponse | JSONResponse:
    try:
        formatted_date: str = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")  # Ensure correct format
        sensor_values: list[float] = db_utils.get_sensor_values_by_date(sensor_id, formatted_date)
        return DailyAggregationResponse(
            min_val=min(sensor_values),
            max_val=max(sensor_values),
            q1=np.percentile(sensor_values, 25),
            median=np.percentile(sensor_values, 50),
            q3=np.percentile(sensor_values, 75),
            unit=db_utils.get_sensor_unit(sensor_id=sensor_id),
        )
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


# TODO: Handle authentication for db insert route
@app.post("/sensors")
async def add_sensor(sensors: list[SensorRequest]) -> JSONResponse:
    try:
        sensors_orm = [Sensor(**sensor.model_dump()) for sensor in sensors]
        db_utils.bulk_add(sensors_orm)
        return add_successful_response
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


# TODO: Handle authentication for db insert route
@app.post("/sensor_values")
async def add_sensor_values(sensor_values: list[SensorValueRequest]) -> JSONResponse:
    try:
        sensor_values_orm = [Sensor(**sensor_value.model_dump()) for sensor_value in sensor_values]
        db_utils.bulk_add(sensor_values_orm)
        return add_successful_response
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response


# TODO: Handle authentication for db delete route
@app.delete("/sensors/{sensor_id}")
async def delete_sensor(sensor_id: str) -> JSONResponse:
    try:
        db_utils.remove_sensor(sensor_id)
        return delete_successful_response
    except SessionException:
        return db_error_response
    except:
        return unknown_error_response
