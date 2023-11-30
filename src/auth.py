from fastapi import HTTPException, Security
from fastapi.security import api_key
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY: str | None = os.getenv("API_KEY")


async def validate_api_key(key: str = Security(api_key.APIKeyHeader(name="X-API-KEY"))):
    if API_KEY is None:
        raise Exception("API key not set!")
    elif key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key!")
    return None
