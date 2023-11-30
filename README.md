# ShiftEnergy Assigment Documentation


## Overview

This API is written with FastAPI. It is meant to provide CRUD (no update endpoint implemented yet) operations services for sensors stored in a relational database with a default dialect of `mysql`. 

Upon startup, the application creates a pool of connection with the database using SQLAlchemy ORM engine. All operations against the database are wrapped in a transaction (code found in `src/utils/database_utils.py`)

API contract models are defined in `src/models/response.py` and `src/models/request.py`. Database models are defined in `src/models/database.py`.

All endpoints are defined under `src/app.py`. Some refactoring can be done here to clean up `app.py` and create a folder for endpoints where each endpoint is in a separate file. This is a matter of preference for now as there aren't that many endpoints. More on each endpoint can be found below.

A `.env` file is used to load credentials for now.

NOTE: The project is incomplete as it would take some more time to properly dockerize the service, spin up a mock db along with an `init.sql` script to populate the db, write test cases to test out the endpoints and most importantly, implement proper authentication.

NOTE2: I made some changes/assumptions with respect to the original instructions:
 - Added `unit` for sensor model
 - For route "get sensor values by their name and date of creation", we cannot ensure uniquess with name and date of creation fields therefore I changed it to take a sensor ID and a date of creation.
 - For route "get a values structure that provides daily aggregation values (e.g. min, q1, median, q3, max) for a given sensor id", I added a requirement that a date needs to be provided as we should have an endpoint which queries the entire timeseries data for a given sensor as the dataset grows over time.

### Some thoughts on authentication

On the note of authentication, currently, the only authentication implemented is a piece of middleware to check for the api key, however, since this service performs more than just read operations, a proper authentication system should be thoughtout. A proposed authentication method can be one where the user requesting the GET/POST/DELETE operation is checked against a permissions table to see if they have the necessary credentials and respond with a failure status code if they do not. With this, we avoid having to pass user database credentials and establish a new connection for each request as it would be very costly in terms of performance.

#### Some thoughts on scaling the service

All endpoints are async therefore they are limited by the number of threads available on the host machine for the Python process. If the bottleneck because machine resources (# of threads), the easy fix would be the up the machine size. However, this is unlikely to be the issue when scaling up. The most likely issue to arise is database I/O. The SQLAlchemy engine class used shares a pool of connections (default of 5, but can be configured with env vars with trivial changes) therefore all database operations must be performed by the connections available in the pool. If we imagine the API service receiving 100 requests at once with a connection pool of 5, all requests will have to wait for when a connection becomes available. This can be an issue if lots of data is pulled by requests. To remedy this, we can both increase the number of connections available in the pool and potentially create read-only replicas of our database as the read operations are potentially the heaviest and presumably the most common requests. The databases should also be put behind a load balancer in order to properly distribute traffic.

### TODOs

To summarize, the TODOs for this project are:
 - Proper dockerization
 - Spin up mock db for testing (sqlite would do)
 - Create init.sql to populate mock db
 - Write test cases
 - Test all endpoints to make sure they're functioning
 - Proper authentication
 - Better error handling and more precise response errors

## Project Structure

### 1. Database Models

- `Sensor` - Represents a sensor entity with attributes:
    - id (PK)
    - name
    - type
    - unit (not specified in the instructions but it would make sense to have)
    - location
    - active
    - activation_date
    - updated_by
    - updated_at
- `SensorValue` - Represents sensor readings with attributes:
    - sensor_id (FK)
    - value
    - creation_date
 - The `SensorValue` model has a foreign key relationship defined with the `Sensor` model where `sensor_value.sensor_id` is connected to `sensor.id`. This model also has a composite primary key (`sensor_id` + `creation_date`).

A relationship status is defined for both models between one another in order to ensure that deleted sensors in `sensors` table will propagate to `sensor_values` and have their values also deleted.

### 2. Request Models

- `SensorRequest`: Defines the structure for creating or updating a sensor.
- `SensorValueRequest`: Defines the structure for adding sensor values.

### 3. Response Models

- `DailyAggregationResponse`: Represents the aggregated values for a sensor on a specific date.
- `SensorResponse`: Represents the response format for a sensor entity.
- `SensorValueResponse`: Represents the response format for sensor values.

### 4. Database Classes and Functions

- `EngineUtilities`: Provides a base class for initializing a database connection and useful functions for interacting with the database using SQLAlchemy ORM.
- `DatabaseUtilities`: Extends `EngineUtilities` and includes functions for querying sensors and sensor values, as well as bulk insertion and sensor deletion.

### 5. Application

- `app`: The FastAPI instance.
- **Routes**:
  - `/sensors`: GET endpoint to retrieve all sensors.
  - `/sensors/{sensor_id}`: GET endpoint to retrieve a sensor by ID.
  - `/sensors/{location}`: GET endpoint to retrieve sensors by location.
  - `/sensor_values/{sensor_id}/{date}`: GET endpoint to retrieve sensor values for a specific sensor and date.
  - `/daily_aggregations/{sensor_id}/{date}`: GET endpoint to retrieve daily aggregations for a specific sensor and date.
  - `/sensors`: POST endpoint to add sensors.
  - `/sensor_values`: POST endpoint to add sensor values.
  - `/sensors/{sensor_id}`: DELETE endpoint to delete a sensor.

### 6. Authentication Middleware

- `validate_api_key`: Middleware function for validating API keys.

## Configuration

- The project relies on environment variables for database configuration and API key validation.

## Running the Project

1. Install dependencies: `pipenv install --dev`
2. Run the FastAPI application: `uvicorn main:app --reload`
