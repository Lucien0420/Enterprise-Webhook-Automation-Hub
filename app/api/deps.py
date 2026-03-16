"""Shared API dependencies."""
from fastapi import Header, HTTPException

from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-KEY")) -> str:
    """Validate X-API-KEY header."""
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key
