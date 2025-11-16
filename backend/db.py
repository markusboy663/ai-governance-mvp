from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Only create engine if DATABASE_URL is set and valid
if DATABASE_URL:
    try:
        engine = create_async_engine(DATABASE_URL, echo=False, future=True)
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    except Exception as e:
        print(f"⚠️  Database connection error (this is OK for testing): {e}")
        engine = None
        AsyncSessionLocal = None
else:
    print("⚠️  DATABASE_URL not set - database features disabled")
    engine = None
    AsyncSessionLocal = None

async def init_db():
    if engine is None:
        print("⚠️  Cannot init_db - engine not configured")
        return
    import models  # sørg for at models importeres så metadata finnes
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
