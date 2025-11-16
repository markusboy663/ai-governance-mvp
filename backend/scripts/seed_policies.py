import asyncio
import uuid
from sqlmodel import select
from db import AsyncSessionLocal
from models import Policy

async def seed():
    policies = [
        {"key": "block_personal_data", "description": "Block requests that contain personal data", "default_value": {"enabled": True}},
        {"key": "block_external_models", "description": "Disallow external (3rd party) models", "default_value": {"enabled": False}},
        {"key": "max_risk_score", "description": "Maximum allowed risk score (0-100)", "default_value": {"max": 50}},
    ]

    async with AsyncSessionLocal() as session:
        for p in policies:
            existing = await session.exec(select(Policy).where(Policy.key == p["key"]))
            if existing.one_or_none():
                continue
            policy = Policy(id=str(uuid.uuid4()), key=p["key"], description=p["description"], default_value=p["default_value"])
            session.add(policy)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())
    print("Seeded policies")
