import bcrypt
import os
from fastapi import HTTPException, Request
from sqlmodel import select
from db import AsyncSessionLocal
from models import APIKey

async def get_api_key_from_header(request: Request):
    auth = request.headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    return auth.split(" ", 1)[1].strip()

async def verify_api_key(token: str):
    """O(1) lookup: token format is <key_id>.<secret>"""
    if "." not in token:
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    try:
        key_id, secret = token.rsplit(".", 1)  # split on last dot
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    # Development mode: if database not configured, allow test keys
    if AsyncSessionLocal is None:
        # Allow any key in format "key_id.secret" for development/testing
        # In production, DATABASE_URL must be set
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(status_code=500, detail="Database not configured")
        # Return mock APIKey for development
        from models import APIKey as APIKeyModel
        mock_key = APIKeyModel(
            key_id=key_id,
            api_key_hash="",
            is_active=True,
            customer_id="dev-customer",
            name=f"Dev Key {key_id}"
        )
        mock_key.id = key_id  # Set ID for rate limiting
        return mock_key
    
    async with AsyncSessionLocal() as session:
        # O(1) lookup by key_id (indexed)
        query = select(APIKey).where(APIKey.key_id == key_id)
        result = await session.exec(query)
        api_key = result.one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        if not api_key.is_active:
            raise HTTPException(status_code=403, detail="API key inactive")
        
        # verify bcrypt hash of secret part
        if not bcrypt.checkpw(secret.encode(), api_key.api_key_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return api_key

async def api_key_dependency(request: Request):
    key = await get_api_key_from_header(request)
    row = await verify_api_key(key)
    return row  # APIKey instance
