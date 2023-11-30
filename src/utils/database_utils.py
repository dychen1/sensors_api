#!/usr/local/bin/python3 -u

import logging
import os
import urllib.parse
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Any

from models.database import Sensor, SensorValue


class SessionException(Exception):
    """
    Exception class for sessions
    """

    def __init__(self, message="Transaction failed within session!"):
        self.message = message
        super().__init__(self.message)


class EngineUtilities:
    """
    Base class using SQLAlchemy engines to initialize a database connection. Contains useful
    functions to transact with the database.
    """

    def __init__(
        self,
        host: str,
        database: str,
        port: int,
        dialect: str,
        recyle_timer: int,
        pool_size: int,
        max_overflow: int,
    ) -> None:
        self.logger = logging.getLogger("EngineUtilitiesLogs")
        self.host = host
        self.database = database
        self.port = port
        self.dialect = dialect

        self.username: str = urllib.parse.quote_plus(os.getenv("MYSQL_USER", ""))
        password: str = urllib.parse.quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        try:
            if not self.username or not password:
                raise Exception("Databaes credentials not found in environment.")

            conn_args = {"ssl": {"ssl-mode": "required"}}
            self.engine = create_engine(
                f"{dialect}://{self.username}:{password}@" f"{self.host}:{self.port}/{self.database}",
                connect_args=conn_args,
                pool_recycle=recyle_timer,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )
            self.init_session = sessionmaker(bind=self.engine)
            self.logger.info(f"Engine and/or sessionmaker configured for {self.database} on {self.host}!")
        except:
            pass  # Remove when a database is available
            # raise Exception(f"Could not configure engine and/or sessionmaker for {self.database} on {self.host}!")

    @contextmanager
    def session_manager(self) -> Any:
        """
        Creates a session from session factory and wraps query in session in database transaction.
        """
        session = self.init_session()
        try:
            yield session
            session.commit()
        except:
            self.logger.error("Session failed!", exc_info=True)
            session.rollback()
            raise SessionException
        finally:
            session.close()
        return


class DatabaseUtilities(EngineUtilities):
    """Utilities class to perform queries."""

    def __init__(
        self,
        host: str,
        database: str,
        port: int = 3306,
        dialect: str = "mysql+pymysql",
        recyle_timer: int = 14400,
        pool_size: int = 5,
        max_overflow: int = 5,
    ) -> None:
        super().__init__(host, database, port, dialect, recyle_timer, pool_size, max_overflow)
        self.logger = logging.getLogger("DatabaseUtilitiesLogs")

    def get_all_sensors(self) -> list[Sensor]:
        """Queries all sensors and returns them by latest activation date."""
        with self.session_manager() as session:
            sensors = session.query(Sensor).order_by(Sensor.activation_date.desc()).all()
        return sensors

    def get_sensor_by_id(self, sensor_id: str) -> Sensor:
        """Takes a sensor id and return a detached Sensor object."""
        with self.session_manager() as session:
            sensor = session.query(Sensor).filter(Sensor.id == sensor_id).first()
        return sensor

    def get_sensor_by_location(self, location: str) -> list[Sensor]:
        """Takes a location and return a list of detached Sensor objects."""
        with self.session_manager() as session:
            sensors = session.query(Sensor).filter(Sensor.location == location).all()
        return sensors

    def get_sensor_unit(self, sensor_id: str) -> str:
        """Fetches the unit for a given sensor id."""
        with self.session_manager() as session:
            unit: str = session.query(Sensor.unit).filter(Sensor.sensor_id == sensor_id).first()
            return unit

    def get_sensor_values_by_date(self, sensor_id: str, date: str, aggregate: bool = False) -> list[float]:
        """Gets sensor values by sensor id and a creation date (YYYY-MM-DD format)."""
        # TODO: Note we can add more support for different operators for date querying in order to
        # query more dates at a time depending on customer needs.
        with self.session_manager() as session:
            query = session.query(SensorValue.value, SensorValue.creation_date).filter(
                SensorValue.sensor_id == sensor_id,
                SensorValue.creation_date.between(date, date),
            )
            if not aggregate:  # When not used for aggregation purposes, we sort by creation date
                query = query.order_by(SensorValue.creation_date)
            sensor_values = query.all()  # Outputs a list of tuples

        return [value[0] for value in sensor_values]

    def bulk_add(self, objects: list[Sensor | SensorValue]) -> None:
        """Takes a list of Sensor or SensorValue objects and performs bulk insert into table."""
        with self.session_manager() as session:
            session.bulk_save_objects(objects)

    def remove_sensor(self, sensor_id: str) -> None:
        """Takes a sensor id and deletes the sensor along with all sensor values associated to it."""
        with self.session_manager() as session:
            sensor_to_delete = session.query(Sensor).get(sensor_id)
            if sensor_to_delete:
                session.delete(session)  # ORM handles propagation of delete onto sensor values
            else:
                self.logger.warning(f"No sensor with id {sensor_id} was found. Delete operation skipped.")
