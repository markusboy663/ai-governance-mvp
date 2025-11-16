import bcrypt
from fastapi import HTTPException, Request
from sqlmodel import select
from db import AsyncSessionLocal
from models import APIKey

async def get_api_key_from_header(request: Request):
    auth = request.headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing API key")
    return auth.split(" ", 1)[1].strip()

async def verify_api_key(key: str):
    async with AsyncSessionLocal() as session:
        rows = await session.exec(select(APIKey))
        for row in rows:
            # compare hashes
            if bcrypt.checkpw(key.encode(), row.api_key_hash.encode()):
                if not row.is_active:
                    raise HTTPException(status_code=403, detail="API key inactive")
                return row
    raise HTTPException(status_code=401, detail="Invalid API key")

async def api_key_dependency(request: Request):
    key = await get_api_key_from_header(request)
    row = await verify_api_key(key)
    return row  # APIKey instance
