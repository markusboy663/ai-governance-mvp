import asyncio
from datetime import datetime, timedelta
from sqlmodel import select, delete
from db import AsyncSessionLocal
from models import UsageLog

async def cleanup(days=90):
    cutoff = datetime.utcnow() - timedelta(days=days)
    async with AsyncSessionLocal() as session:
        await session.exec(delete(UsageLog).where(UsageLog.created_at < cutoff))
        await session.commit()
        print(f"Cleaned up UsageLog entries older than {days} days (before {cutoff})")

if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    asyncio.run(cleanup(days))
